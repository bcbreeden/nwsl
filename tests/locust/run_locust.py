import json
import subprocess

# Load config
with open("config.json") as f:
    config = json.load(f)

# Format run time (e.g., "180s")
run_time = f"{config['run_time_seconds']}s"

# Build the command
command = [
    "locust",
    "--headless",
    f"--host={config['host']}",
    f"--users={config['users']}",
    f"--spawn-rate={config['spawn_rate']}",
    f"--run-time={run_time}",
    "-f", "perf.py"
]

# Run the command
subprocess.run(command)