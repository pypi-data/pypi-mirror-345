from pathlib import Path

PRELOAD_SCRIPT_PATH = Path(__file__).resolve().parent / "preload.sh"
with PRELOAD_SCRIPT_PATH.open() as f:
    PRELOAD_SCRIPT = f.read()
PRELOAD_COMMAND = [
    "/bin/bash",
    "-c",
    f"echo '{PRELOAD_SCRIPT}' > /tmp/preload.sh; chmod +x /tmp/preload.sh; /tmp/preload.sh",
]
