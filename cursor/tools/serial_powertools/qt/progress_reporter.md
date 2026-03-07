# ============================================================
# 1. WAYBAR CONFIG (on marstation)
# ============================================================
# Add to your bar's "modules-right" (or wherever you want):
#   "custom/lyrik-progress"
#
# Add the module definition:

{
    "custom/lyrik-progress": {
        "exec": "~/.local/bin/waybar_progress.py",
        "return-type": "json",
        "interval": 5,
        "on-click": "~/.local/bin/waybar_progress.py --clear-done",
        "tooltip": true
    }
}

# ============================================================
# 2. WAYBAR CSS (in style.css)
# ============================================================

#custom-lyrik-progress {
    font-family: monospace;
    padding: 0 8px;
}

#custom-lyrik-progress.running {
    color: #a6e3a1;  /* green */
}

#custom-lyrik-progress.done {
    color: #f9e2af;  /* yellow — waiting for you to clear */
}

#custom-lyrik-progress.offline {
    color: #f38ba8;  /* red */
}

#custom-lyrik-progress.idle {
    /* hide when nothing is happening — or set color: transparent */
    color: #6c7086;
}


# ============================================================
# 3. SYSTEMD USER SERVICE (on lyrik.local)
# ============================================================
# Place at: ~/.config/systemd/user/progress-server.service
# Then: systemctl --user enable --now progress-server

[Unit]
Description=Job Progress Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/YOURUSER/progress_server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target


# ============================================================
# 4. USAGE IN YOUR PYTHON JOBS (on lyrik.local)
# ============================================================

# Copy progress_reporter.py next to your script, then:

from progress_reporter import ProgressReporter

reporter = ProgressReporter(label="My Render Job")
reporter.start()

total = len(my_items)
for i, item in enumerate(my_items):
    process(item)
    reporter.report((i + 1) / total)

reporter.finish()

# Each job gets a random 8-char ID automatically.
# You can also pass job_id="my-fixed-id" if you want stable IDs.


# ============================================================
# 5. MANUAL CLEAR (from terminal on marstation)
# ============================================================

# Clear a specific job:
#   python3 -c "
#     import socket, json
#     s = socket.create_connection(('lyrik.local', 9876))
#     s.sendall(json.dumps({'type': 'clear', 'id': 'JOB_ID_HERE'}).encode() + b'\n')
#     s.close()
#   "

# Clear all finished jobs (same as clicking the waybar module):
#   ~/.local/bin/waybar_progress.py --clear-done
