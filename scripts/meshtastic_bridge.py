#!/usr/bin/env python3
"""
Meshtastic → FCI dashboard bridge (multi-sensor).

Subscribes to your Meshtastic gateway's MQTT JSON feed and keeps, per
node: its name (from nodeinfo), its position (from position packets),
its latest environment telemetry (temperature / humidity / pressure)
and its own 24-hour uptime. Serves one JSON the dashboard reads live:

  uptime_24h_pct    — share of the last 24 h (5-min buckets) in which the
                      mesh as a whole delivered telemetry. This is the
                      indicator: Environmental × Community ·
                      "Neighbourhood sensing uptime" (higher = better).
  sensors_connected — nodes with telemetry inside the active window
                      (default 60 min).
  averages          — mean of each environment metric across connected
                      sensors' latest readings.
  sensors[]         — per node: id, name, last values, lat/lng, last_seen,
                      its own uptime. The dashboard renders this list when
                      you click the sensor count on the cell.

Adding more sensors needs nothing here: any node that joins the same
mesh (same channel/region) and emits telemetry appears on the next
refresh. Use --node to restrict to an explicit comma-separated list.

Requirements: none — pure Python 3 standard library. It ships its own
minimal MQTT 3.1.1 client (subscribe/QoS-0). If paho-mqtt happens to be
installed (pip3 install paho-mqtt) it is used instead, but nothing needs
installing to run this.
Gateway: MQTT module enabled with JSON output. Telemetry topics look
like  msh/<region>/2/json/<channel>/!<gateway-id>

Usage
-----
    # node plugged into THIS computer via USB (simplest — auto-detects port):
    python3 scripts/meshtastic_bridge.py --serial
    #   needs once:  pip3 install meshtastic

    # no broker on the network? BE the broker (gateway points at this machine):
    python3 scripts/meshtastic_bridge.py --listen

    # classic: subscribe to an MQTT broker
    python3 scripts/meshtastic_bridge.py --broker mqtt.meshtastic.org \\
        --user meshdev --password large4cats --topic 'msh/EU_868/2/json/#'

    python3 scripts/meshtastic_bridge.py --broker 192.168.1.10 \\
        --topic 'msh/#' --node '!a1b2c3d4,!deadbeef'

    python3 scripts/meshtastic_bridge.py --selftest      # offline check

Dashboard → Environmental × Community → Attach a reading → Live feed:
    endpoint http://localhost:8787/reading.json · path uptime_24h_pct
    min 0 · max 100 · direction: higher = better

State survives restarts in ~/.fci_meshtastic_state.json. The server
sends Access-Control-Allow-Origin: * (localhost is a secure context, so
the dashboard may call it from file://, localhost or GitHub Pages).
"""

import argparse
import json
import os
import random
import socket
import ssl
import struct
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

WINDOW_S = 24 * 3600
BUCKET_S = 300                      # 5-minute buckets → 288 per day
STATE_PATH = os.path.expanduser("~/.fci_meshtastic_state.json")

ENV_KEYS = {
    "temperature": "temperature_c",
    "relative_humidity": "relative_humidity_pct",
    "barometric_pressure": "barometric_pressure_hpa",
}

# every metric family a Meshtastic sensor can emit, every key spelling seen
# in the wild (protobuf-dict camelCase, MQTT-JSON snake_case)
_ENV_FIELD_MAP = [
    (("temperature",), "temperature_c"),
    (("relativeHumidity", "relative_humidity"), "relative_humidity_pct"),
    (("barometricPressure", "barometric_pressure"), "barometric_pressure_hpa"),
    (("iaq",), "iaq"),
    (("lux",), "lux"),
]
_AQ_FIELD_MAP = [
    (("pm25Standard", "pm25_standard"), "pm25_ugm3"),
    (("pm100Standard", "pm100_standard"), "pm10_ugm3"),
    (("pm10Standard", "pm10_standard"), "pm1_ugm3"),
]


def metrics_to_env(em, aq=None):
    """Fold environment + air-quality metric dicts into our canonical keys."""
    env = {}
    for keys, out in _ENV_FIELD_MAP:
        for k in keys:
            v = (em or {}).get(k)
            if isinstance(v, (int, float)):
                env[out] = round(float(v), 2)
                break
    for keys, out in _AQ_FIELD_MAP:
        for k in keys:
            v = (aq or {}).get(k)
            if isinstance(v, (int, float)):
                env[out] = round(float(v), 2)
                break
    return env


def iso(ts):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


class TelemetryStore:
    """Rolling 24 h window of per-node telemetry. No network — testable."""

    def __init__(self):
        self.lock = threading.Lock()
        self.nodes = {}     # id -> {name, short, env, env_ts, pos, last_seen, buckets:set}
        self.messages = 0
        self.load()

    # -- persistence ------------------------------------------------------
    def load(self):
        try:
            with open(STATE_PATH) as fh:
                s = json.load(fh)
            for nid, n in s.get("nodes", {}).items():
                n["buckets"] = set(int(b) for b in n.get("buckets", []))
                self.nodes[nid] = n
            self.messages = int(s.get("messages", 0))
            self.prune()
        except Exception:
            pass

    def save(self):
        try:
            with self.lock:
                s = {"messages": self.messages, "nodes": {
                    nid: dict(n, buckets=sorted(n["buckets"])) for nid, n in self.nodes.items()}}
            with open(STATE_PATH, "w") as fh:
                json.dump(s, fh)
        except Exception:
            pass

    # -- ingest -----------------------------------------------------------
    def _node(self, nid):
        return self.nodes.setdefault(nid, {
            "name": None, "short": None, "env": None, "env_ts": 0, "dev": None,
            "pos": None, "last_seen": 0, "buckets": set()})

    def prune(self, now=None):
        cutoff = (now or time.time()) - WINDOW_S
        for n in self.nodes.values():
            n["buckets"] = {b for b in n["buckets"] if b >= cutoff}

    def record_telemetry(self, nid, env, now=None):
        now = now or time.time()
        with self.lock:
            n = self._node(nid)
            n["buckets"].add(int(now // BUCKET_S) * BUCKET_S)
            n["last_seen"] = max(n["last_seen"], now)
            if env and now >= n["env_ts"]:      # out-of-order MQTT must not roll back the latest reading
                n["env"], n["env_ts"] = env, now
            self.messages += 1
            self.prune(now)

    def record_nodeinfo(self, nid, longname, shortname, now=None):
        with self.lock:
            n = self._node(nid)
            if longname: n["name"] = longname
            if shortname: n["short"] = shortname
            if now: n["last_seen"] = max(n.get("last_seen") or 0, now)

    def record_device(self, nid, dev, now=None):
        """Battery / voltage — every node has these, sensor or not."""
        with self.lock:
            n = self._node(nid)
            n["dev"] = dict(n.get("dev") or {}, **dev)
            n["last_seen"] = max(n.get("last_seen") or 0, now or time.time())

    def record_position(self, nid, lat, lng, now=None):
        with self.lock:
            n = self._node(nid)
            n["pos"] = {"lat": round(lat, 5), "lng": round(lng, 5)}
            if now is None: now = time.time()
            n["last_seen"] = max(n.get("last_seen") or 0, now)

    # -- read -------------------------------------------------------------
    def snapshot(self, now=None, active_s=3600):
        now = now or time.time()
        with self.lock:
            self.prune(now)
            total = WINDOW_S // BUCKET_S
            mesh_buckets = set()
            sensors, connected, mesh_nodes = [], [], []
            for nid, n in sorted(self.nodes.items()):
                is_sensor = bool(n["buckets"] or n["env"])
                mesh_nodes.append({
                    "node": nid,
                    "name": n["name"] or nid,
                    "short": n["short"],
                    "is_sensor": is_sensor,
                    "connected": (now - n["env_ts"]) <= active_s if n["env_ts"] else False,
                    "last": n["env"],
                    "dev": n.get("dev"),
                    "last_seen": iso(n["last_seen"]) if n["last_seen"] else None,
                    "position": n["pos"],
                    "uptime_24h_pct": round(100.0 * len(n["buckets"]) / total, 1) if is_sensor else None,
                })
                if not is_sensor:
                    continue                      # never sent env telemetry — a router, not a sensor
                mesh_buckets |= n["buckets"]
                is_conn = (now - n["env_ts"]) <= active_s if n["env_ts"] else False
                s = {
                    "node": nid,
                    "name": n["name"] or nid,
                    "short": n["short"],
                    "connected": is_conn,
                    "last": n["env"],
                    "last_seen": iso(n["last_seen"]) if n["last_seen"] else None,
                    "position": n["pos"],
                    "uptime_24h_pct": round(100.0 * len(n["buckets"]) / total, 1),
                }
                sensors.append(s)
                if is_conn and n["env"]:
                    connected.append(n["env"])
            averages = {}
            if connected:
                for k in set().union(*connected):
                    vals = [e[k] for e in connected if isinstance(e.get(k), (int, float))]
                    if vals:
                        averages[k] = round(sum(vals) / len(vals), 2)
            return {
                "source": "Meshtastic mesh via local bridge",
                "binds_to": {"cell": "environmental:community",
                             "indicator": "Neighbourhood sensing uptime"},
                "updated_at": iso(now),
                "uptime_24h_pct": round(100.0 * len(mesh_buckets) / total, 1),
                "buckets_filled": len(mesh_buckets),
                "buckets_total": total,
                "sensors_connected": len(connected),
                "mesh_nodes": mesh_nodes,
                "nodes_total": len(mesh_nodes),
                "sensors_seen_24h": len(sensors),
                "averages": averages,
                "sensors": sensors,
                "messages_24h": self.messages,
                "active_window_s": active_s,
                "normalisation": {"scale_min": 0, "scale_max": 100, "direction": "dido"},
            }


STORE = TelemetryStore()


def node_id_of(msg):
    """Originating node: numeric `from` (formatted !hex) beats `sender`,
    which is the gateway that uplinked the packet."""
    f = msg.get("from")
    if isinstance(f, int):
        return "!%08x" % (f & 0xFFFFFFFF)
    s = msg.get("sender")
    return str(s) if s else "?"


_NONJSON_WARNED = set()
_QUIET = False


def _log(s):
    if not _QUIET:
        print(time.strftime("%H:%M:%S ") + s, flush=True)


def handle_mqtt_message(topic, payload_bytes, node_filter=None):
    try:
        msg = json.loads(payload_bytes.decode("utf-8", "replace"))
    except Exception:
        base = topic.rsplit("/", 1)[0]
        if base not in _NONJSON_WARNED:
            _NONJSON_WARNED.add(base)
            _log(f"⚠ non-JSON packet on {topic} — that is the encrypted protobuf feed. "
                 f"If this is your gateway, enable 'JSON output enabled' in Module config → MQTT and reboot the node.")
        return
    nid = node_id_of(msg)
    if node_filter and nid not in node_filter:
        return
    t, p = msg.get("type"), msg.get("payload") or {}
    if t == "telemetry":
        dev = {}
        if isinstance(p.get("battery_level"), (int, float)):
            dev["battery_pct"] = min(100, round(float(p["battery_level"])))
        if isinstance(p.get("voltage"), (int, float)):
            dev["voltage_v"] = round(float(p["voltage"]), 2)
        if dev:
            STORE.record_device(nid, dev)
        env = metrics_to_env(p, p)
        if env:
            STORE.record_telemetry(nid, env)
            _log(f"✓ environment telemetry from {nid}: " +
                 " ".join(f"{k}={v}" for k, v in env.items()))
        else:
            _log(f"· telemetry from {nid} has no environment metrics (battery/airtime only) — "
                 f"check Module config → Telemetry → environment measurement enabled, and that the sensor is detected")
    elif t == "nodeinfo":
        STORE.record_nodeinfo(p.get("id") or nid, p.get("longname"), p.get("shortname"), now=time.time())
        _log(f"· nodeinfo: {nid} is '{p.get('longname') or '?'}'")
    elif t == "position":
        lat, lng = p.get("latitude_i"), p.get("longitude_i")
        if isinstance(lat, int) and isinstance(lng, int) and (lat or lng):
            STORE.record_position(nid, lat / 1e7, lng / 1e7)
            _log(f"· position for {nid}: {lat/1e7:.5f}, {lng/1e7:.5f}")


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STATIC = {                       # the bridge also serves the dashboard itself —
    "/index.html": "text/html; charset=utf-8",          # same origin as the data,
    "/assets/data.js": "text/javascript; charset=utf-8" # so no CORS, one URL to open
}


class Handler(BaseHTTPRequestHandler):
    active_s = 3600

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/reading.json", "/reading"):
            body = json.dumps(STORE.snapshot(active_s=self.active_s), indent=1).encode()
            return self._send(200, "application/json", body)
        if path == "/":
            path = "/index.html"
        if path in _STATIC:
            try:
                with open(os.path.join(REPO_ROOT, path.lstrip("/")), "rb") as fh:
                    return self._send(200, _STATIC[path], fh.read())
            except OSError:
                pass
        self._send(404, "application/json", b'{"error":"not found - use /reading.json or /"}')

    def log_message(self, *a):
        pass


def serve(port, active_s=3600):
    Handler.active_s = active_s
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


"""── Serial mode (--serial) — the node is plugged into THIS computer ──────
No WiFi, no MQTT, no broker: telemetry is read straight off the USB
port via the official meshtastic library (pip3 install meshtastic).
Every node of the mesh reaches us through the plugged gateway."""


_DEBUG = False


def _ingest_serial_packet(packet, node_filter=None):
    """Map a decoded meshtastic-python packet into the store. Pure — testable."""
    d = packet.get("decoded") or {}
    nid = packet.get("fromId")
    if not nid:
        n = packet.get("from")
        nid = "!%08x" % (n & 0xFFFFFFFF) if isinstance(n, int) else "?"
    if node_filter and nid not in node_filter:
        return
    if _DEBUG:
        _log(f"[debug] packet from {nid} port={d.get('portnum')} decoded-keys={sorted(d.keys())}")
    port = d.get("portnum")
    tele = d.get("telemetry") or {}
    if port in ("TELEMETRY_APP", 67) or tele:
        dm = tele.get("deviceMetrics") or tele.get("device_metrics") or {}
        dev = {}
        if isinstance(dm.get("batteryLevel", dm.get("battery_level")), (int, float)):
            dev["battery_pct"] = min(100, round(float(dm.get("batteryLevel", dm.get("battery_level")))))
        if isinstance(dm.get("voltage"), (int, float)):
            dev["voltage_v"] = round(float(dm["voltage"]), 2)
        if dev:
            STORE.record_device(nid, dev)
        env = metrics_to_env(
            tele.get("environmentMetrics") or tele.get("environment_metrics"),
            tele.get("airQualityMetrics") or tele.get("air_quality_metrics"))
        if env:
            STORE.record_telemetry(nid, env)
            _log(f"✓ environment telemetry from {nid}: " + " ".join(f"{k}={v}" for k, v in env.items()))
        else:
            _log(f"· telemetry from {nid} without environment metrics (battery/airtime only)")
    elif port == "POSITION_APP":
        p = d.get("position") or {}
        lat, lng = p.get("latitude"), p.get("longitude")
        if lat is None and isinstance(p.get("latitudeI"), int):
            lat = p["latitudeI"] / 1e7
        if lng is None and isinstance(p.get("longitudeI"), int):
            lng = p["longitudeI"] / 1e7
        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)) and (lat or lng):
            STORE.record_position(nid, float(lat), float(lng))
            _log(f"· position for {nid}: {lat:.5f}, {lng:.5f}")
    elif port == "NODEINFO_APP":
        u = d.get("user") or {}
        STORE.record_nodeinfo(u.get("id") or nid, u.get("longName"), u.get("shortName"), now=time.time())
        _log(f"· nodeinfo: {nid} is '{u.get('longName') or '?'}'")


def write_publish_snapshot(active_s, path=None):
    """Write the current mesh picture as a dated snapshot the dashboard can
    serve from the repo (GitHub Pages). Same shape as /reading.json plus
    observation_date + published_at."""
    snap = STORE.snapshot(active_s=active_s)
    snap["observation_date"] = time.strftime("%Y-%m-%d", time.gmtime())
    snap["published_at"] = iso(time.time())
    snap["note"] = "Published by scripts/meshtastic_bridge.py --publish. Git history is the provenance ledger."
    path = path or os.path.join(REPO_ROOT, "data", "snapshots", "meshtastic.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(snap, fh, indent=1)
        fh.write("\n")
    return path


def git_publish(path):
    """add + commit + push the snapshot. Tolerant: a failed push must never
    kill the bridge — it reports and retries on the next cycle."""
    import subprocess
    rel = os.path.relpath(path, REPO_ROOT)
    try:
        subprocess.run(["git", "-C", REPO_ROOT, "add", rel], check=True, capture_output=True, timeout=30)
        r = subprocess.run(["git", "-C", REPO_ROOT, "commit", "-m",
                            "Snapshot: meshtastic mesh " + time.strftime("%Y-%m-%d %H:%M")],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return "no changes to publish"
        p = subprocess.run(["git", "-C", REPO_ROOT, "push"], capture_output=True, text=True, timeout=120)
        if p.returncode == 0:
            return "pushed — Pages updates in ~1 min"
        tail = (p.stderr or p.stdout or "").strip().splitlines()
        return "committed, but push failed: " + (tail[-1][:140] if tail else "?")
    except Exception as e:
        return "git error: %s" % e


def setup_wifi(args):
    """One-shot: with the node on USB, write WiFi credentials + MQTT →
    this machine + JSON output + primary-channel uplink. Order matters:
    network config goes LAST because the node reboots into WiFi on write."""
    try:
        from meshtastic.serial_interface import SerialInterface
    except ImportError:
        sys.exit("Needs the official library once:  pip3 install meshtastic")
    ssid, psk = args.setup_wifi
    server = args.mqtt_server
    if not server:
        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe.connect(("8.8.8.8", 80))
            server = probe.getsockname()[0]
            probe.close()
        except Exception:
            sys.exit("Could not determine this machine's LAN IP — pass --mqtt-server <ip>")
    print("Connecting over USB…")
    dev = None if args.serial in (None, "auto") else args.serial
    iface = SerialInterface(devPath=dev)
    time.sleep(2)
    node = iface.localNode
    print(f"Configuring: MQTT → {server}:1883 (JSON, no auth) · uplink on · WiFi '{ssid}'")
    try:
        mq = node.moduleConfig.mqtt
        mq.enabled = True
        mq.address = server
        mq.json_enabled = True
        mq.encryption_enabled = False
        mq.tls_enabled = False
        mq.username = ""
        mq.password = ""
        node.writeConfig("mqtt")
        print("✔ MQTT module written (JSON output enabled)")
    except Exception as e:
        print(f"✗ MQTT config failed ({e}) — set it in the app: Module config → MQTT")
    try:
        ch = node.channels[0]
        ch.settings.uplink_enabled = True
        node.writeChannel(0)
        print("✔ primary channel uplink enabled")
    except Exception as e:
        print(f"✗ channel uplink failed ({e}) — enable it in the app: Channels → primary → Uplink")
    try:
        net = node.localConfig.network
        net.wifi_enabled = True
        net.wifi_ssid = ssid
        net.wifi_psk = psk
        node.writeConfig("network")
        print("✔ WiFi written — the node is rebooting into WiFi now")
    except Exception as e:
        print(f"✗ WiFi config failed ({e}) — set it in the app: Radio config → Network")
    print("""
Done. Next:
  1. Unplug the USB — power the node from battery/charger anywhere in WiFi range.
     (2.4 GHz networks only: ESP32 does not see 5 GHz.)
  2. Start the bridge in WiFi mode and leave it running:
       python3 scripts/meshtastic_bridge.py --listen --publish 5
  3. Within ~2 min you should see:  Gateway connected from 192.168.x.x
     then:  ✓ environment telemetry from !xxxx …
  If macOS asks whether Python may accept incoming connections: Allow.""")
    try:
        iface.close()
    except Exception:
        pass


def diagnose(args, enable_env=False):
    """Read the plugged node's real state over USB and say plainly why
    environment data is or is not flowing. With enable_env=True, switch the
    telemetry module on (interval 120 s) and save it to the device."""
    try:
        from meshtastic.serial_interface import SerialInterface
    except ImportError:
        sys.exit("Needs the official library. Run once:\n\n    pip3 install meshtastic\n")
    print("Connecting over USB…")
    dev = None if args.serial in (None, "auto") else args.serial
    iface = SerialInterface(devPath=dev)
    time.sleep(2)

    try:
        me = iface.getMyNodeInfo() or {}
        u = me.get("user") or {}
        print(f"\nPlugged node : {u.get('longName') or '?'} ({u.get('id') or '?'}) · hw {u.get('hwModel') or '?'}")
    except Exception as e:
        print(f"Could not read node info: {e}")

    print("\nMesh node DB (what the gateway has heard):")
    any_env = False
    try:
        now = time.time()
        for nid, n in (iface.nodes or {}).items():
            uu = n.get("user") or {}
            age = (now - n["lastHeard"]) / 60 if n.get("lastHeard") else None
            env = n.get("environmentMetrics")
            if env:
                any_env = True
            print(f"  {uu.get('id') or nid:<12} {uu.get('longName') or '?':<24} "
                  f"last heard {age:.0f} min ago" if age is not None else
                  f"  {uu.get('id') or nid:<12} {uu.get('longName') or '?':<24} never heard", end="")
            print(f" · env metrics: {'YES ' + str(env) if env else 'none seen'}")
    except Exception as e:
        print(f"  could not list nodes: {e}")

    print("\nTelemetry module config on the plugged node:")
    tel = None
    try:
        tel = iface.localNode.moduleConfig.telemetry
        print("  " + str(tel).strip().replace("\n", "\n  "))
        enabled = bool(getattr(tel, "environment_measurement_enabled", False))
        interval = int(getattr(tel, "environment_update_interval", 0) or 0)
        print(f"\n  → environment measurement: {'ENABLED' if enabled else '*** DISABLED ***'}"
              f" · interval {interval or 'default (1800)'} s")
        if not enabled:
            print("  This is why no data flows. Fix: run with --enable-env, or in the app:")
            print("  Module config → Telemetry → Environment measurement enabled ✓")
    except Exception as e:
        print(f"  could not read module config ({e}) — check it in the app instead.")

    if enable_env and tel is not None:
        try:
            tel.environment_measurement_enabled = True
            tel.environment_update_interval = 120
            iface.localNode.writeConfig("telemetry")
            print("\n✔ Wrote config: environment measurement ENABLED, interval 120 s.")
            print("  The node saves and may reboot itself; give it ~1 minute,")
            print("  then start the bridge:  python3 scripts/meshtastic_bridge.py --serial")
        except Exception as e:
            print(f"\nCould not write the config over USB ({e}) — enable it in the app.")
    elif not any_env:
        print("\nNo node in this mesh has ever delivered environment metrics to the gateway.")
        print("If the sensor hangs off the plugged node: run  --enable-env  once.")
        print("If it hangs off ANOTHER node: enable the telemetry module on that node in the app.")

    try:
        iface.close()
    except Exception:
        pass


def _ingest_nodedb(nodes, node_filter=None):
    """Pull names, positions AND environment metrics straight out of the
    gateway's node DB. Crucial detail: the plugged node's OWN telemetry does
    not always surface as a receive event — but it always lands in the node
    DB, so polling this is what makes the local sensor visible. The lastHeard
    guard keeps stale DB entries from inflating uptime."""
    count = 0
    for nid, n in list((nodes or {}).items()):
        u = n.get("user") or {}
        key = u.get("id") or nid
        if node_filter and key not in node_filter:
            continue
        heard = n.get("lastHeard")
        heard = heard if isinstance(heard, (int, float)) and heard > 0 else None
        if u.get("longName") or u.get("shortName"):
            STORE.record_nodeinfo(key, u.get("longName"), u.get("shortName"), now=heard)
        pos = n.get("position") or {}
        lat, lng = pos.get("latitude"), pos.get("longitude")
        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)) and (lat or lng):
            STORE.record_position(key, lat, lng, now=heard)
        dm = n.get("deviceMetrics") or {}
        dev = {}
        if isinstance(dm.get("batteryLevel"), (int, float)):
            dev["battery_pct"] = min(100, round(float(dm["batteryLevel"])))
        if isinstance(dm.get("voltage"), (int, float)):
            dev["voltage_v"] = round(float(dm["voltage"]), 2)
        if dev:
            STORE.record_device(key, dev, now=n.get("lastHeard"))
        env = metrics_to_env(n.get("environmentMetrics"), n.get("airQualityMetrics"))
        if env:
            ts = n.get("lastHeard")
            cur = STORE.nodes.get(key)
            changed = not cur or cur.get("env") != env
            fresh_by_heard = (isinstance(ts, (int, float)) and ts > 0
                              and (not cur or ts > cur.get("env_ts", 0))
                              and (time.time() - ts) < WINDOW_S)
            if changed:
                # values moved → the reading is fresh NOW, whatever lastHeard says
                # (a node never hears itself over radio, so its own lastHeard stalls)
                STORE.record_telemetry(key, env, now=time.time())
            elif fresh_by_heard:
                STORE.record_telemetry(key, env, now=min(ts, time.time()))
            if changed or fresh_by_heard:
                _log(f"✓ environment telemetry from {key} (node DB): " +
                     " ".join(f"{k}={v}" for k, v in env.items()))
                count += 1
    return count


def run_serial(args, node_filter):
    try:
        from meshtastic.serial_interface import SerialInterface
        from pubsub import pub
    except ImportError:
        sys.exit("Serial mode needs the official library. Run once:\n\n    pip3 install meshtastic\n\nthen start the bridge again with --serial.")

    state = {"lost": False}

    def on_receive(packet, interface=None):
        try:
            _ingest_serial_packet(packet, node_filter)
        except Exception:
            pass

    def on_lost(interface=None):
        state["lost"] = True

    pub.subscribe(on_receive, "meshtastic.receive")
    try:
        pub.subscribe(on_lost, "meshtastic.connection.lost")
    except Exception:
        pass

    def request_telemetry(iface):
        for kwargs in (
            {"destinationId": "^all", "wantResponse": True, "telemetryType": "environment_metrics"},
            {"destinationId": "^all", "wantResponse": True},
            {},
        ):
            try:
                iface.sendTelemetry(**kwargs)
                return True
            except TypeError:
                continue
            except Exception:
                return False
        return False

    def connect_loop():
        backoff = 5
        while True:
            iface = None
            try:
                dev = None if args.serial in (None, "auto") else args.serial
                iface = SerialInterface(devPath=dev)
                state["lost"] = False
                n = _ingest_nodedb(getattr(iface, "nodes", None), node_filter)
                _log(f"Serial link up — node DB read: {len(getattr(iface,'nodes',{}) or {})} node(s), "
                     f"{n} with environment metrics. Polling the DB every 30 s and requesting telemetry every 5 min.")
                backoff = 5
                last_req = 0
                while not state["lost"]:
                    time.sleep(30)
                    _ingest_nodedb(getattr(iface, "nodes", None), node_filter)
                    if getattr(args, "request_telemetry", False) and time.time() - last_req >= 300:
                        if request_telemetry(iface):
                            _log("· requested environment telemetry from the mesh")
                        last_req = time.time()
                raise ConnectionError("serial connection lost")
            except Exception as e:
                _log(f"Serial problem ({e}) — retrying in {backoff}s (node rebooting or replugged? that's fine)")
                try:
                    if iface:
                        iface.close()
                except Exception:
                    pass
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)

    threading.Thread(target=connect_loop, daemon=True).start()


"""── Minimal MQTT 3.1.1 client — stdlib only, subscribe/QoS-0 ─────────────
Enough protocol for this job: CONNECT, SUBSCRIBE, receive PUBLISH,
answer keepalive with PINGREQ, reconnect with backoff. Used when
paho-mqtt is not installed, so the bridge runs on a bare macOS python3."""


def _enc_len(n):
    out = b""
    while True:
        d = n % 128
        n //= 128
        out += bytes([d | (0x80 if n else 0)])
        if not n:
            return out


def _enc_str(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


class _SockReader:
    """Buffered exact-read over a socket (or any object with .recv)."""

    def __init__(self, sock):
        self.sock, self.buf = sock, b""

    def read_exact(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(4096)      # may raise socket.timeout
            if not chunk:
                raise ConnectionError("connection closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out


def mqtt_connect_packet(client_id, user=None, password=None, keepalive=60):
    flags = 0x02                              # clean session
    payload = _enc_str(client_id)
    if user is not None:
        flags |= 0x80
        payload += _enc_str(user)
        if password is not None:
            flags |= 0x40
            payload += _enc_str(password)
    body = _enc_str("MQTT") + bytes([4, flags]) + struct.pack(">H", keepalive) + payload
    return bytes([0x10]) + _enc_len(len(body)) + body


def mqtt_subscribe_packet(topic, pid=1):
    body = struct.pack(">H", pid) + _enc_str(topic) + bytes([0])   # QoS 0
    return bytes([0x82]) + _enc_len(len(body)) + body


def mqtt_read_packet(reader):
    header = reader.read_exact(1)[0]
    mul, length = 1, 0
    for _ in range(4):
        b = reader.read_exact(1)[0]
        length += (b & 0x7F) * mul
        if not (b & 0x80):
            break
        mul *= 128
    return header, reader.read_exact(length) if length else b""


def mqtt_parse_publish(header, body):
    qos = (header >> 1) & 0x03
    tlen = struct.unpack(">H", body[:2])[0]
    topic = body[2:2 + tlen].decode("utf-8", "replace")
    i = 2 + tlen + (2 if qos else 0)          # QoS>0 carries a packet id
    return topic, body[i:]


def run_mqtt_builtin(args, node_filter):
    def worker():
        backoff = 3
        while True:
            try:
                raw = socket.create_connection((args.broker, args.port), timeout=15)
                if args.tls:
                    raw = ssl.create_default_context().wrap_socket(raw, server_hostname=args.broker)
                raw.settimeout(30)            # idle → time to ping
                rd = _SockReader(raw)
                cid = "fci-bridge-%08x" % random.getrandbits(32)
                raw.sendall(mqtt_connect_packet(cid, args.user, args.password))
                h, body = mqtt_read_packet(rd)
                if h >> 4 != 2 or (len(body) > 1 and body[1] != 0):
                    raise ConnectionError("broker refused connection (CONNACK rc=%s)" % (body[1] if len(body) > 1 else "?"))
                raw.sendall(mqtt_subscribe_packet(args.topic))
                print(f"MQTT connected (builtin client) — subscribed to {args.topic}")
                backoff = 3
                while True:
                    try:
                        h, body = mqtt_read_packet(rd)
                    except socket.timeout:
                        raw.sendall(b"\xc0\x00")          # PINGREQ
                        continue
                    if h >> 4 == 3:                        # PUBLISH
                        topic, payload = mqtt_parse_publish(h, body)
                        handle_mqtt_message(topic, payload, node_filter)
                    # CONNACK/SUBACK/PINGRESP and the rest: nothing to do
            except Exception as e:
                print(f"MQTT connection lost ({e}) — retrying in {backoff}s")
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)

    threading.Thread(target=worker, daemon=True).start()


"""── Mini-broker mode (--listen) ──────────────────────────────────────────
No broker on your network? The bridge can BE the broker: it listens on
port 1883, the Meshtastic gateway connects straight to this machine, and
every JSON publish lands in the store. Uplink-capture only — it does not
forward anything back to the mesh, which is all this instrument needs."""


def _broker_client_thread(conn, addr, node_filter):
    conn.settimeout(180)
    rd = _SockReader(conn)
    try:
        while True:
            h, body = mqtt_read_packet(rd)
            t = h >> 4
            if t == 1:                                   # CONNECT → accept anyone
                conn.sendall(b"\x20\x02\x00\x00")
                print(f"Gateway connected from {addr[0]}")
            elif t == 3:                                 # PUBLISH
                if (h >> 1) & 0x03 == 1:                 # QoS 1 → PUBACK
                    tlen = struct.unpack(">H", body[:2])[0]
                    conn.sendall(b"\x40\x02" + body[2 + tlen:4 + tlen])
                topic, payload = mqtt_parse_publish(h, body)
                handle_mqtt_message(topic, payload, node_filter)
            elif t == 8:                                 # SUBSCRIBE → grant QoS 0
                conn.sendall(b"\x90\x03" + body[:2] + b"\x00")
            elif t == 12:                                # PINGREQ
                conn.sendall(b"\xd0\x00")
            elif t == 14:                                # DISCONNECT
                return
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def run_mini_broker(args, node_filter):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", args.listen_port))
    srv.listen(8)

    def accept_loop():
        while True:
            try:
                conn, addr = srv.accept()
                threading.Thread(target=_broker_client_thread, args=(conn, addr, node_filter), daemon=True).start()
            except Exception:
                time.sleep(1)

    threading.Thread(target=accept_loop, daemon=True).start()
    return srv


def run_mqtt(args, node_filter):
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        return run_mqtt_builtin(args, node_filter)

    def on_connect(client, userdata, flags, rc, properties=None):
        print(f"MQTT connected (paho, rc={rc}) — subscribing to {args.topic}")
        client.subscribe(args.topic)

    def on_message(client, userdata, m):
        handle_mqtt_message(m.topic, m.payload, node_filter)

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except (AttributeError, TypeError):
        client = mqtt.Client()      # paho 1.x
    if args.user:
        client.username_pw_set(args.user, args.password or "")
    if args.tls:
        client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=3, max_delay=60)

    def connect_with_retry():
        backoff = 3
        while True:
            try:
                client.connect(args.broker, args.port, keepalive=60)
                client.loop_start()               # paho auto-reconnects from here on
                return
            except Exception as e:
                print(f"Cannot reach {args.broker}:{args.port} ({e}) — retrying in {backoff}s. "
                      f"No broker on your network? Run with --listen and point the gateway at this machine.")
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)

    threading.Thread(target=connect_with_retry, daemon=True).start()
    return client


def selftest():
    global _QUIET
    _QUIET = True
    """Two fake sensors + a router node; checks counts, averages, list."""
    global STORE
    STORE = TelemetryStore.__new__(TelemetryStore)
    STORE.lock, STORE.nodes, STORE.messages = threading.Lock(), {}, 0
    now = time.time()
    mk = lambda d: json.dumps(d).encode()

    # sensor A: names itself, positions itself, 6 h of telemetry
    handle_mqtt_message("t", mk({"from": 0x11223344, "type": "nodeinfo",
        "payload": {"id": "!11223344", "longname": "Patio sensor", "shortname": "PAT"}}))
    handle_mqtt_message("t", mk({"from": 0x11223344, "type": "position",
        "payload": {"latitude_i": 413874000, "longitude_i": 21686000}}))
    for i in range(72):
        STORE.record_telemetry("!11223344", {"temperature_c": 21.0, "relative_humidity_pct": 50.0},
                               now=now - i * BUCKET_S)
    # deliberately out of order: the i-loop above fed newest first, so this
    # also exercises the env_ts guard — the latest reading must win.
    # sensor B: telemetry only, no name, currently connected
    handle_mqtt_message("t", mk({"from": 0xdeadbeef, "type": "telemetry",
        "payload": {"temperature_c_IGNORED": 1, "temperature": 23.0,
                    "relative_humidity": 40.0, "barometric_pressure": 1012.0}}))
    # a router that never sent telemetry must NOT count as a sensor
    handle_mqtt_message("t", mk({"from": 0x0c0ffee0, "type": "nodeinfo",
        "payload": {"id": "!0c0ffee0", "longname": "Rooftop router"}}))

    s = STORE.snapshot(now=now)
    checks = [
        ("two sensors seen, router excluded", s["sensors_seen_24h"] == 2),
        ("both connected inside active window", s["sensors_connected"] == 2),
        ("averages across connected sensors", s["averages"].get("temperature_c") == 22.0
                                             and s["averages"].get("relative_humidity_pct") == 45.0),
        ("pressure averaged over the node that has it", s["averages"].get("barometric_pressure_hpa") == 1012.0),
        ("nodeinfo name attached", any(x["name"] == "Patio sensor" for x in s["sensors"])),
        ("position decoded", any(x["position"] == {"lat": 41.3874, "lng": 2.1686} for x in s["sensors"])),
        ("mesh uptime ~25%", abs(s["uptime_24h_pct"] - 25.0) < 0.5),
        ("per-node uptime present", all("uptime_24h_pct" in x for x in s["sensors"])),
    ]
    # serial-mode packet mapping (meshtastic-python decoded shapes), offline
    _ingest_serial_packet({"fromId": "!aabbccdd", "decoded": {"portnum": "TELEMETRY_APP",
        "telemetry": {"environmentMetrics": {"temperature": 24.3, "relativeHumidity": 55.0,
                                             "barometricPressure": 1009.8}}}})
    _ingest_serial_packet({"fromId": "!aabbccdd", "decoded": {"portnum": "POSITION_APP",
        "position": {"latitude": -33.44890, "longitude": -70.66930}}})
    _ingest_serial_packet({"fromId": "!aabbccdd", "decoded": {"portnum": "NODEINFO_APP",
        "user": {"id": "!aabbccdd", "longName": "Sensor patio PC", "shortName": "PC1"}}})
    sn = STORE.snapshot()
    ser = next((x for x in sn["sensors"] if x["node"] == "!aabbccdd"), None)
    checks.append(("serial telemetry mapped", ser is not None and ser["last"]["temperature_c"] == 24.3
                   and ser["last"]["barometric_pressure_hpa"] == 1009.8))
    checks.append(("serial position + name mapped", ser is not None
                   and ser["position"] == {"lat": -33.4489, "lng": -70.6693}
                   and ser["name"] == "Sensor patio PC"))
    _ingest_serial_packet({"from": 12345, "decoded": {"portnum": "POSITION_APP",
        "position": {"latitudeI": 413874000, "longitudeI": 21686000}}})
    sn2 = STORE.snapshot()
    checks.append(("integer position decoded via from-num id",
                   any(x["node"] == "!00003039" and x["position"] == {"lat": 41.3874, "lng": 2.1686}
                       for x in sn2["sensors"] if x["position"]) or
                   ("!00003039" in STORE.nodes and STORE.nodes["!00003039"]["pos"] == {"lat": 41.3874, "lng": 2.1686})))

    # node-DB ingestion (the local plugged sensor lives here, not in receive events)
    fake_nodes = {
        "!8f494c08": {"user": {"id": "!8f494c08", "longName": "Meshtastic 4c08", "shortName": "4c08"},
                      "lastHeard": int(now),
                      "environmentMetrics": {"temperature": 24.063848, "relativeHumidity": 46.802254,
                                             "barometricPressure": 1002.8946, "iaq": 61},
                      "position": {"latitude": 41.39, "longitude": 2.17}},
        "!f6baca57": {"user": {"id": "!f6baca57", "longName": "PLANETAI FAB CITY WATCHER"},
                      "lastHeard": int(now) - 200},
    }
    got_n = _ingest_nodedb(fake_nodes)
    dbn = STORE.nodes.get("!8f494c08")
    checks.append(("node DB env metrics ingested", got_n == 1 and dbn is not None
                   and dbn["env"]["temperature_c"] == 24.06 and dbn["env"]["iaq"] == 61))
    got_again = _ingest_nodedb(fake_nodes)
    checks.append(("node DB re-poll does not double-count", got_again == 0))
    fake_nodes["!8f494c08"]["lastHeard"] = int(now) + 300
    fake_nodes["!8f494c08"]["environmentMetrics"]["temperature"] = 25.5
    checks.append(("node DB newer reading updates", _ingest_nodedb(fake_nodes) == 1
                   and STORE.nodes["!8f494c08"]["env"]["temperature_c"] == 25.5))
    # the plugged node never hears itself: lastHeard stalls but values move —
    # a changed value must still be ingested as fresh
    fake_nodes["!8f494c08"]["lastHeard"] = int(now) - 7200          # stale
    fake_nodes["!8f494c08"]["environmentMetrics"]["temperature"] = 26.1
    checks.append(("changed values beat a stale lastHeard", _ingest_nodedb(fake_nodes) == 1
                   and STORE.nodes["!8f494c08"]["env"]["temperature_c"] == 26.1
                   and (time.time() - STORE.nodes["!8f494c08"]["env_ts"]) < 5))

    # mesh_nodes: ALL nodes visible, sensors and plain nodes alike
    fake_nodes["!f6baca57"]["deviceMetrics"] = {"batteryLevel": 87, "voltage": 4.05}
    _ingest_nodedb(fake_nodes)
    snx = STORE.snapshot()
    watcher = next((x for x in snx["mesh_nodes"] if x["node"] == "!f6baca57"), None)
    checks.append(("plain nodes appear in mesh_nodes with battery",
                   watcher is not None and watcher["is_sensor"] is False
                   and (watcher["dev"] or {}).get("battery_pct") == 87))
    checks.append(("sensors list still env-only",
                   not any(x["node"] == "!f6baca57" for x in snx["sensors"])
                   and snx["nodes_total"] >= len(snx["sensors"])))

    # air-quality-only node (e.g. a PM2.5 watcher): must count as a sensor
    _ingest_serial_packet({"fromId": "!0a1b2c3d", "decoded": {"portnum": "TELEMETRY_APP",
        "telemetry": {"airQualityMetrics": {"pm25Standard": 12, "pm100Standard": 18}}}})
    aq = STORE.nodes.get("!0a1b2c3d")
    checks.append(("air-quality metrics count as sensing", aq is not None
                   and aq["env"]["pm25_ugm3"] == 12 and aq["env"]["pm10_ugm3"] == 18))
    # numeric portnum + snake_case keys (other decode paths in the wild)
    _ingest_serial_packet({"fromId": "!0a1b2c3d", "decoded": {"portnum": 67,
        "telemetry": {"environment_metrics": {"temperature": 19.0, "relative_humidity": 61.0}}}})
    checks.append(("numeric portnum + snake_case keys ingested",
                   STORE.nodes["!0a1b2c3d"]["env"].get("temperature_c") == 19.0))
    # MQTT JSON with air-quality fields
    handle_mqtt_message("msh/t", mk({"from": 0x0eeeeeee, "type": "telemetry",
        "payload": {"pm25_standard": 33, "temperature": 22.0}}))
    checks.append(("MQTT air-quality payload ingested",
                   STORE.nodes.get("!0eeeeeee", {}).get("env", {}).get("pm25_ugm3") == 33))

    # --publish: snapshot file shape
    import tempfile
    tmp = tempfile.mktemp(suffix=".json")
    write_publish_snapshot(3600, path=tmp)
    with open(tmp) as fh:
        pub = json.load(fh)
    os.unlink(tmp)
    checks.append(("published snapshot carries date + normalisation + nodes",
                   "observation_date" in pub and "published_at" in pub
                   and pub.get("normalisation", {}).get("scale_max") == 100
                   and isinstance(pub.get("mesh_nodes"), list) and len(pub["mesh_nodes"]) > 0))

    # builtin MQTT codec, offline
    class _Fake:
        def __init__(self, data): self.data = data
        def recv(self, n):
            out, self.data = self.data[:n], self.data[n:]
            return out
    con = mqtt_connect_packet("cid", "meshdev", "large4cats")
    checks.append(("CONNECT packet well-formed",
                   con[0] == 0x10 and b"MQTT" in con and b"meshdev" in con and b"large4cats" in con))
    checks.append(("remaining-length encoding", _enc_len(0) == b"\x00" and _enc_len(321) == b"\xc1\x02"))
    payload = json.dumps({"from": 1, "type": "telemetry", "payload": {"temperature": 20.0}}).encode()
    pub = bytes([0x30]) + _enc_len(2 + 5 + len(payload)) + _enc_str("msh/x") + payload
    h, body = mqtt_read_packet(_SockReader(_Fake(pub)))
    topic, got = mqtt_parse_publish(h, body)
    checks.append(("PUBLISH round-trip parse", h >> 4 == 3 and topic == "msh/x" and got == payload))
    pub1 = bytes([0x32]) + _enc_len(2 + 5 + 2 + len(payload)) + _enc_str("msh/x") + b"\x00\x07" + payload
    h1, body1 = mqtt_read_packet(_SockReader(_Fake(pub1)))
    checks.append(("QoS-1 PUBLISH skips the packet id", mqtt_parse_publish(h1, body1)[1] == payload))

    # mini-broker (--listen) over a socketpair, offline
    a, b = socket.socketpair()
    threading.Thread(target=_broker_client_thread, args=(b, ("selftest", 0), None), daemon=True).start()
    conn_pkt = mqtt_connect_packet("gateway")
    pub_payload = json.dumps({"from": 0x77777777, "type": "telemetry",
                              "payload": {"temperature": 19.5, "relative_humidity": 60.0}}).encode()
    pub_pkt = bytes([0x30]) + _enc_len(2 + 5 + len(pub_payload)) + _enc_str("msh/t") + pub_payload
    a.sendall(conn_pkt + pub_pkt + b"\xc0\x00")            # CONNECT + PUBLISH + PINGREQ
    time.sleep(0.3)
    a.settimeout(2)
    resp = a.recv(64)
    checks.append(("mini-broker answers CONNACK + PINGRESP", resp.startswith(b"\x20\x02\x00\x00") and b"\xd0\x00" in resp))
    checks.append(("mini-broker ingests gateway publishes", "!77777777" in STORE.nodes
                   and STORE.nodes["!77777777"]["env"]["temperature_c"] == 19.5))
    a.close()

    ok = True
    for label, passed in checks:
        print(("PASS" if passed else "FAIL") + ": " + label)
        ok &= passed
    httpd = serve(8787)
    import urllib.request
    got = json.load(urllib.request.urlopen("http://127.0.0.1:8787/reading.json"))
    fresh = STORE.snapshot()
    same = (got["sensors_connected"] == fresh["sensors_connected"]
            and len(got["sensors"]) == len(fresh["sensors"]) > 0)
    print(("PASS" if same else "FAIL") + ": HTTP endpoint serves the same picture")
    html = urllib.request.urlopen("http://127.0.0.1:8787/").read()
    okhtml = b"Fab City Index" in html and b"assets/data.js" in html
    print(("PASS" if okhtml else "FAIL") + ": / serves the dashboard itself (same origin as the data)")
    same = same and okhtml
    httpd.shutdown()
    return 0 if (ok and same) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--broker", default="mqtt.meshtastic.org")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--user", default=None, help="e.g. meshdev on the public broker")
    ap.add_argument("--password", default=None)
    ap.add_argument("--tls", action="store_true")
    ap.add_argument("--topic", default="msh/#", help="narrow to your region/channel, e.g. msh/EU_868/2/json/#")
    ap.add_argument("--node", default=None, help="restrict to these node ids, comma-separated: '!a1b2c3d4,!deadbeef'")
    ap.add_argument("--active-window", type=int, default=60, help="minutes without telemetry before a sensor stops counting as connected")
    ap.add_argument("--http-port", type=int, default=8787)
    ap.add_argument("--listen", action="store_true", help="no broker needed: BE the broker — the gateway connects straight to this machine")
    ap.add_argument("--listen-port", type=int, default=1883)
    ap.add_argument("--serial", nargs="?", const="auto", default=None, metavar="PORT",
                    help="node plugged into THIS computer via USB — reads telemetry off the port (auto-detects; needs: pip3 install meshtastic)")
    ap.add_argument("--publish", type=int, metavar="MIN", default=None,
                    help="every MIN minutes, write data/snapshots/meshtastic.json and git commit+push it — so GitHub Pages shows the mesh to everyone")
    ap.add_argument("--debug", action="store_true", help="log every packet reaching the bridge, with its port and keys")
    ap.add_argument("--request-telemetry", action="store_true", help="also broadcast telemetry requests every 5 min (some firmwares print 'No response from node' — harmless)")
    ap.add_argument("--setup-wifi", nargs=2, metavar=("SSID", "PASSWORD"), default=None,
                    help="one-shot over USB: write WiFi + MQTT→this machine + JSON + uplink, then go wireless with --listen")
    ap.add_argument("--mqtt-server", default=None, metavar="IP", help="override the MQTT server IP written by --setup-wifi (default: this machine's LAN IP)")
    ap.add_argument("--diagnose", action="store_true", help="read the plugged node's real config over USB and say why data is/isn't flowing")
    ap.add_argument("--enable-env", action="store_true", help="diagnose + switch environment telemetry ON (interval 120 s) on the plugged node")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())
    if args.debug:
        global _DEBUG
        _DEBUG = True
    if args.setup_wifi:
        setup_wifi(args)
        sys.exit(0)
    if args.diagnose or args.enable_env:
        diagnose(args, enable_env=args.enable_env)
        sys.exit(0)

    node_filter = set(x.strip() for x in args.node.split(",")) if args.node else None
    serve(args.http_port, active_s=args.active_window * 60)
    if args.serial is not None:
        run_serial(args, node_filter)
        mqtt_line = f"serial (USB){'' if args.serial=='auto' else ' on '+args.serial} — reading the mesh through the plugged node"
    elif args.listen:
        run_mini_broker(args, node_filter)
        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe.connect(("8.8.8.8", 80))          # no packet sent — just picks the LAN interface
            my_ip = probe.getsockname()[0]
            probe.close()
        except Exception:
            my_ip = "the IP from: ipconfig getifaddr en0"
        mqtt_line = f"mini-broker on 0.0.0.0:{args.listen_port} — set the gateway's MQTT server address to {my_ip} (JSON output enabled)"
    else:
        run_mqtt(args, node_filter)
        mqtt_line = f"{args.broker}:{args.port}  topic {args.topic}"
    print(f"""
Bridge running.
  MQTT      : {mqtt_line}""" + (f"  nodes {args.node}" if args.node else "  (all nodes on the mesh)") + f"""
  Dashboard : http://localhost:{args.http_port}/          ← open this in the browser
  Data      : http://localhost:{args.http_port}/reading.json

Any new sensor that joins the same mesh appears automatically.
Dashboard → Environmental × Community → Attach a reading → Live feed:
  API endpoint : http://localhost:{args.http_port}/reading.json
  JSON path    : uptime_24h_pct
  min 0 · max 100 · direction: higher = better
Ctrl-C to stop; state persists in {STATE_PATH}.""")
    try:
        last_pub = 0
        while True:
            time.sleep(60)
            STORE.save()
            if args.publish and time.time() - last_pub >= args.publish * 60:
                last_pub = time.time()
                try:
                    p = write_publish_snapshot(args.active_window * 60)
                    _log("snapshot → repo: " + git_publish(p))
                except Exception as e:
                    _log(f"publish failed ({e}) — will retry")
    except KeyboardInterrupt:
        STORE.save()
        if args.publish:
            try:
                p = write_publish_snapshot(args.active_window * 60)
                _log("final snapshot → repo: " + git_publish(p))
            except Exception:
                pass
        print("\nState saved. Bye.")


if __name__ == "__main__":
    main()
