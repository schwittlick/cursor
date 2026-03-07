#!/usr/bin/env python3
"""
progress_server.py — run this on lyrik.local
Listens on TCP port 9876 for job reporters,
serves current state to waybar polling clients.

Protocol:
  Reporters connect and send newline-delimited JSON:
    {"type": "report", "id": "job-xyz", "label": "my job", "progress": 0.42}
    {"type": "report", "id": "job-xyz", "label": "my job", "progress": 1.0, "done": true}
    {"type": "clear", "id": "job-xyz"}   # remove a finished job
    {"type": "clear_done"}               # remove all finished jobs

  Pollers connect, send:
    {"type": "query"}
  and receive one JSON response then the connection closes:
    {"jobs": [{"id": ..., "label": ..., "progress": ..., "done": ..., "started": ..., "finished": ...}]}
"""

import asyncio
import json
import logging
import time
from collections import OrderedDict

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("progress_server")

HOST = "0.0.0.0"
PORT = 9876

# job_id -> dict
jobs: OrderedDict = OrderedDict()
jobs_lock = asyncio.Lock()

# callbacks to notify when a job finishes (for notify-send on marstation side,
# we just flag done=true and the poller handles the notification)


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    try:
        while True:
            line = await reader.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                log.warning("Bad JSON from %s: %r", peer, line)
                continue

            t = msg.get("type")

            if t == "report":
                job_id = msg.get("id")
                if not job_id:
                    continue
                async with jobs_lock:
                    existing = jobs.get(job_id, {})
                    done = msg.get("done", False)
                    now = time.time()
                    jobs[job_id] = {
                        "id": job_id,
                        "label": msg.get("label", job_id),
                        "progress": float(msg.get("progress", 0.0)),
                        "done": done,
                        "started": existing.get("started", now),
                        "finished": now if done else existing.get("finished"),
                        "notified": existing.get("notified", False),
                    }
                    if done and not existing.get("notified"):
                        jobs[job_id]["notified"] = False  # poller sets this after notify
                log.info("Job %s: %.1f%% done=%s", job_id, float(msg.get("progress", 0)) * 100, done)

            elif t == "clear":
                job_id = msg.get("id")
                if job_id:
                    async with jobs_lock:
                        jobs.pop(job_id, None)
                    log.info("Cleared job %s", job_id)

            elif t == "clear_done":
                async with jobs_lock:
                    to_remove = [k for k, v in jobs.items() if v.get("done")]
                    for k in to_remove:
                        del jobs[k]
                log.info("Cleared %d finished jobs", len(to_remove))

            elif t == "query":
                async with jobs_lock:
                    snapshot = list(jobs.values())
                response = json.dumps({"jobs": snapshot}) + "\n"
                writer.write(response.encode())
                await writer.drain()
                break  # pollers get one response and disconnect

            elif t == "ack_notify":
                # waybar script tells us it already sent the notification
                job_id = msg.get("id")
                if job_id:
                    async with jobs_lock:
                        if job_id in jobs:
                            jobs[job_id]["notified"] = True

    except asyncio.IncompleteReadError, ConnectionResetError:
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addrs = ", ".join(str(s.getsockname()) for s in server.sockets)
    log.info("Progress server listening on %s", addrs)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
