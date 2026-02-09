import subprocess
import time
import re

print("Starting Cloudflare Tunnel...")
# Run npx cloudflared tunnel
process = subprocess.Popen(
    ["npx", "-y", "cloudflared", "tunnel", "--url", "http://localhost:8501"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    shell=True,
    encoding="utf-8",
    errors="replace"
)

url = None
timeout = 60 # wait up to 60 seconds
start_time = time.time()

with open("tunnel_log.txt", "w", encoding="utf-8", errors="replace") as f:
    while time.time() - start_time < timeout:
        try:
            line = process.stdout.readline()
        except UnicodeDecodeError:
            continue
        if not line:
            break
        f.write(line)
        f.flush()
        print(line.strip())
        
        # Look for the URL
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            url = match.group(0)
            print(f"\nFOUND URL: {url}\n")
            break

if url:
    with open("final_url.txt", "w") as f:
        f.write(url)
else:
    print("Failed to find URL within timeout.")

# Keep it running in the background? 
# We'll let it stay for now and the user can check it.
# Note: This script will block until URL is found or timeout.
