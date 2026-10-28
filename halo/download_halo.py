from pathlib import Path
import subprocess
import shutil

URL = "https://gh-proxy.com/https://github.com/halo-dev/halo/releases/download/v2.27.1/halo-2.27.1.jar"
ROOT = Path(__file__).parent
PARTS = ROOT / "parts"
OUT = ROOT / "halo-2.27.1.jar"
TOTAL = 134790347
COUNT = 4

PARTS.mkdir(exist_ok=True)
for p in PARTS.glob("part-*.bin"):
    p.unlink()
if OUT.exists():
    OUT.unlink()

chunk = (TOTAL + COUNT - 1) // COUNT
procs = []
for i in range(COUNT):
    start = i * chunk
    end = min(TOTAL - 1, (i + 1) * chunk - 1)
    dest = PARTS / f"part-{i:02d}.bin"
    args = ["curl.exe", "-L", "--http1.1", "--fail", "--retry", "5", "--retry-all-errors", "--silent", "--show-error",
            "-r", f"{start}-{end}", "-o", str(dest), URL]
    procs.append(subprocess.Popen(args))

for p in procs:
    code = p.wait()
    if code != 0:
        raise SystemExit(f"download failed with exit code {code}")

with OUT.open("wb") as target:
    for i in range(COUNT):
        part = PARTS / f"part-{i:02d}.bin"
        if part.stat().st_size != min(chunk, TOTAL - i * chunk):
            raise SystemExit(f"unexpected segment size: {part}")
        with part.open("rb") as source:
            shutil.copyfileobj(source, target, length=1024 * 1024)

print(f"downloaded {OUT} ({OUT.stat().st_size} bytes)")
