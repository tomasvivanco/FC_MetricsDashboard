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

Requirements:  pip install paho-mqtt
Gateway: MQTT module enabled with JSON output. Telemetry topics look
like  msh/<region>/2/json/<channel>/!<gateway-id>

Usage
-----
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
            "name": None, "short": None, "env": None, "env_ts": 0,
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
            n["last_seen"] = now or time.time()

    def record_position(self, nid, lat, lng, now=None):
        with self.lock:
            n = self._node(nid)
            n["pos"] = {"lat": round(lat, 5), "lng": round(lng, 5)}
            n["last_seen"] = now or time.time()

    # -- read -------------------------------------------------------------
    def snapshot(self, now=None, active_s=3600):
        now = now or time.time()
        with self.lock:
            self.prune(now)
            total = WINDOW_S // BUCKET_S
            mesh_buckets = set()
            sensors, connected = [], []
            for nid, n in sorted(self.nodes.items()):
                if not n["buckets"] and not n["env"]:
                    continue                      # never sent telemetry — a router, not a sensor
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


def handle_mqtt_message(topic, payload_bytes, node_filter=None):
    try:
        msg = json.loads(payload_bytes.decode("utf-8", "replace"))
    except Exception:
        return
    nid = node_id_of(msg)
    if node_filter and nid not in node_filter:
        return
    t, p = msg.get("type"), msg.get("payload") or {}
    if t == "telemetry":
        env = {out: round(float(p[k]), 2) for k, out in ENV_KEYS.items()
               if isinstance(p.get(k), (int, float))}
        if env:                                   # ignore device-metrics-only telemetry
            STORE.record_telemetry(nid, env)
    elif t == "nodeinfo":
        STORE.record_nodeinfo(p.get("id") or nid, p.get("longname"), p.get("shortname"))
    elif t == "position":
        lat, lng = p.get("latitude_i"), p.get("longitude_i")
        if isinstance(lat, int) and isinstance(lng, int) and (lat or lng):
            STORE.record_position(nid, lat / 1e7, lng / 1e7)


class Handler(BaseHTTPRequestHandler):
    active_s = 3600

    def do_GET(self):
        body = json.dumps(STORE.snapshot(active_s=self.active_s), indent=1).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def serve(port, active_s=3600):
    Handler.active_s = active_s
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def run_mqtt(args, node_filter):
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        sys.exit("paho-mqtt is not installed. Run:  pip install paho-mqtt")

    def on_connect(client, userdata, flags, rc, properties=None):
        print(f"MQTT connected (rc={rc}) — subscribing to {args.topic}")
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
    client.connect(args.broker, args.port, keepalive=60)
    client.loop_start()
    return client


def selftest():
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
    ok = True
    for label, passed in checks:
        print(("PASS" if passed else "FAIL") + ": " + label)
        ok &= passed
    httpd = serve(8787)
    import urllib.request
    got = json.load(urllib.request.urlopen("http://127.0.0.1:8787/reading.json"))
    same = got["sensors_connected"] == s["sensors_connected"] and len(got["sensors"]) == 2
    print(("PASS" if same else "FAIL") + ": HTTP endpoint serves the same picture")
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
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    node_filter = set(x.strip() for x in args.node.split(",")) if args.node else None
    serve(args.http_port, active_s=args.active_window * 60)
    run_mqtt(args, node_filter)
    print(f"""
Bridge running.
  MQTT     : {args.broker}:{args.port}  topic {args.topic}""" + (f"  nodes {args.node}" if args.node else "  (all nodes on the mesh)") + f"""
  Endpoint : http://localhost:{args.http_port}/reading.json

Any new sensor that joins the same mesh appears automatically.
Dashboard → Environmental × Community → Attach a reading → Live feed:
  API endpoint : http://localhost:{args.http_port}/reading.json
  JSON path    : uptime_24h_pct
  min 0 · max 100 · direction: higher = better
Ctrl-C to stop; state persists in {STATE_PATH}.""")
    try:
        while True:
            time.sleep(60)
            STORE.save()
    except KeyboardInterrupt:
        STORE.save()
        print("\nState saved. Bye.")


if __name__ == "__main__":
    main()
