#!/usr/bin/env python3
"""
Meshtastic → FCI dashboard bridge.

Subscribes to your Meshtastic gateway's MQTT JSON feed, keeps a rolling
24-hour window of environment telemetry (temperature / humidity /
pressure), and serves ONE number the dashboard can read live:

    uptime_24h_pct — the share of the last 24 hours (in 5-minute buckets)
    in which your community's own mesh delivered at least one telemetry
    reading. This feeds Environmental × Community · "Neighbourhood
    sensing uptime" (direction: higher = better).

The raw last readings travel alongside in the same JSON, but the
indicator is the uptime: the cell asks whether the neighbourhood KNOWS
its own air, not what the temperature was.

Requirements
------------
    pip install paho-mqtt        (the only dependency)

Your Meshtastic gateway node must have MQTT enabled with JSON output
(Settings → Module config → MQTT → JSON output enabled). Telemetry then
appears on topics like:   msh/<region>/2/json/<channel>/!<gateway-id>

Usage
-----
    # public broker, default Meshtastic credentials, all nodes:
    python3 scripts/meshtastic_bridge.py --broker mqtt.meshtastic.org \\
        --user meshdev --password large4cats --topic 'msh/#'

    # your own broker, one specific sensor node:
    python3 scripts/meshtastic_bridge.py --broker 192.168.1.10 \\
        --topic 'msh/EU_868/2/json/#' --node '!a1b2c3d4'

    # then point the dashboard's Live-feed panel at:
    #   endpoint : http://localhost:8787/reading.json
    #   path     : uptime_24h_pct
    #   min 0 · max 100 · direction: higher = better

    # offline self-test (no broker, fake telemetry):
    python3 scripts/meshtastic_bridge.py --selftest

State survives restarts in ~/.fci_meshtastic_state.json.
The HTTP server sends Access-Control-Allow-Origin: * so the dashboard
can read it whether it is opened from file://, localhost, or GitHub
Pages (localhost is a secure context, so https pages may call it).
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


class TelemetryStore:
    """Rolling window of telemetry events. No network — unit-testable."""

    def __init__(self):
        self.lock = threading.Lock()
        self.buckets = {}           # bucket_ts -> set of node ids
        self.last = None            # last environment reading seen
        self.messages = 0
        self.load()

    # -- persistence ------------------------------------------------------
    def load(self):
        try:
            with open(STATE_PATH) as fh:
                s = json.load(fh)
            self.buckets = {int(k): set(v) for k, v in s.get("buckets", {}).items()}
            self.last = s.get("last")
            self.messages = int(s.get("messages", 0))
            self.prune()
        except Exception:
            pass

    def save(self):
        try:
            with self.lock:
                s = {"buckets": {str(k): sorted(v) for k, v in self.buckets.items()},
                     "last": self.last, "messages": self.messages}
            with open(STATE_PATH, "w") as fh:
                json.dump(s, fh)
        except Exception:
            pass

    # -- ingest -----------------------------------------------------------
    def prune(self, now=None):
        cutoff = (now or time.time()) - WINDOW_S
        self.buckets = {b: n for b, n in self.buckets.items() if b >= cutoff}

    def record(self, node, env, now=None):
        now = now or time.time()
        bucket = int(now // BUCKET_S) * BUCKET_S
        with self.lock:
            self.buckets.setdefault(bucket, set()).add(node or "?")
            self.messages += 1
            if env:
                self.last = dict(env, node=node,
                                 received_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)))
            self.prune(now)

    # -- read -------------------------------------------------------------
    def snapshot(self, now=None):
        now = now or time.time()
        with self.lock:
            self.prune(now)
            filled = len(self.buckets)
            nodes = set()
            for n in self.buckets.values():
                nodes |= n
            total = WINDOW_S // BUCKET_S
            return {
                "source": "Meshtastic mesh via local bridge",
                "binds_to": {"cell": "environmental:community",
                             "indicator": "Neighbourhood sensing uptime"},
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
                "uptime_24h_pct": round(100.0 * filled / total, 1),
                "buckets_filled": filled,
                "buckets_total": total,
                "nodes_seen_24h": sorted(nodes),
                "messages_24h": self.messages if filled else 0,
                "last": self.last,
                "normalisation": {"scale_min": 0, "scale_max": 100, "direction": "dido"},
            }


STORE = TelemetryStore()


def handle_mqtt_message(topic, payload_bytes):
    """Parse a Meshtastic JSON MQTT message; record telemetry events."""
    try:
        msg = json.loads(payload_bytes.decode("utf-8", "replace"))
    except Exception:
        return
    if msg.get("type") != "telemetry":
        return
    p = msg.get("payload") or {}
    env = {out: round(float(p[k]), 2) for k, out in ENV_KEYS.items() if isinstance(p.get(k), (int, float))}
    node = msg.get("sender") or msg.get("from")
    node = str(node) if node is not None else "?"
    STORE.record(node, env or None)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(STORE.snapshot(), indent=1).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):        # keep the terminal readable
        pass


def serve(port):
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
        if node_filter:
            try:
                sender = json.loads(m.payload).get("sender")
            except Exception:
                sender = None
            if sender != node_filter:
                return
        handle_mqtt_message(m.topic, m.payload)

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
    """Feed fake telemetry, start the server, check the arithmetic."""
    now = time.time()
    for i in range(72):                       # 6 hours of 5-min readings
        STORE.record("!selftest", {"temperature_c": 21.5, "relative_humidity_pct": 48.0},
                     now=now - i * BUCKET_S)
    snap = STORE.snapshot(now=now)
    expected = round(100.0 * 72 / 288, 1)     # 25.0
    ok = abs(snap["uptime_24h_pct"] - expected) < 0.2
    print(("PASS" if ok else "FAIL") + f": uptime arithmetic — {snap['uptime_24h_pct']}% (expected ~{expected}%)")
    print(("PASS" if snap["last"]["temperature_c"] == 21.5 else "FAIL") + ": last reading carried")
    httpd = serve(8787)
    import urllib.request
    got = json.load(urllib.request.urlopen("http://127.0.0.1:8787/reading.json"))
    print(("PASS" if got["uptime_24h_pct"] == snap["uptime_24h_pct"] else "FAIL") + ": HTTP endpoint serves the same number")
    httpd.shutdown()
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--broker", default="mqtt.meshtastic.org")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--user", default=None, help="e.g. meshdev on the public broker")
    ap.add_argument("--password", default=None)
    ap.add_argument("--tls", action="store_true")
    ap.add_argument("--topic", default="msh/#", help="MQTT topic filter — narrow it to your region/channel")
    ap.add_argument("--node", default=None, help="only count one node id, e.g. '!a1b2c3d4'")
    ap.add_argument("--http-port", type=int, default=8787)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    serve(args.http_port)
    run_mqtt(args, args.node)
    print(f"""
Bridge running.
  MQTT     : {args.broker}:{args.port}  topic {args.topic}""" + (f"  node {args.node}" if args.node else "") + f"""
  Endpoint : http://localhost:{args.http_port}/reading.json

In the dashboard → Environmental × Community → Attach a reading → Live feed:
  API endpoint : http://localhost:{args.http_port}/reading.json
  JSON path    : uptime_24h_pct
  min 0 · max 100 · direction: higher = better
Then 'Test & read now'. Ctrl-C to stop; state persists in {STATE_PATH}.""")
    try:
        while True:
            time.sleep(60)
            STORE.save()
    except KeyboardInterrupt:
        STORE.save()
        print("\nState saved. Bye.")


if __name__ == "__main__":
    main()
