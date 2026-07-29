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
            and len(got["sensors"]) == len(fresh["sensors"]) == 3)   # 2 fakes + 1 via mini-broker
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
    ap.add_argument("--listen", action="store_true", help="no broker needed: BE the broker — the gateway connects straight to this machine")
    ap.add_argument("--listen-port", type=int, default=1883)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    node_filter = set(x.strip() for x in args.node.split(",")) if args.node else None
    serve(args.http_port, active_s=args.active_window * 60)
    if args.listen:
        run_mini_broker(args, node_filter)
        try:
            my_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            my_ip = "<this machine's IP>"
        mqtt_line = f"mini-broker on 0.0.0.0:{args.listen_port} — set the gateway's MQTT server address to {my_ip} (JSON output enabled)"
    else:
        run_mqtt(args, node_filter)
        mqtt_line = f"{args.broker}:{args.port}  topic {args.topic}"
    print(f"""
Bridge running.
  MQTT     : {mqtt_line}""" + (f"  nodes {args.node}" if args.node else "  (all nodes on the mesh)") + f"""
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
