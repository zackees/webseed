"""
Service generates webtorrent files and 
"""
import os
import hashlib
import time
import sys
import shutil

# Directory structure is
# $DATA_DIR/content - contains *.mp4 or *.webm files
# $DATA_DIR - contains the generated files
CHUNK_FACTOR = 17  # 128KB, or n^17
OUT_DIR = os.environ.get("DATA_DIR", "/var/data")
CONTENT_DIR = os.path.join(OUT_DIR, "content")
os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_TEMPLATE = open(os.path.join(HERE, "template.html"),
                     encoding="utf-8").read()

# Copy webtorrent.zach.min.js to the output directory
WEBTORRENT_JS = os.path.join(HERE, "webtorrent.zach.min.js")
WEBTORRENT_JS_OUT = os.path.join(OUT_DIR, "webtorrent.zach.min.js")

if not os.path.exists(WEBTORRENT_JS_OUT):
    shutil.copyfile(WEBTORRENT_JS, WEBTORRENT_JS_OUT)
else:
    WEBTORRENT_JS_STR = open(WEBTORRENT_JS, encoding="utf-8", mode="r").read()
    WEBTORRENT_OUT_JS_STR = open(
        WEBTORRENT_JS_OUT, encoding="utf-8", mode="r").read()
    if WEBTORRENT_JS_STR != WEBTORRENT_OUT_JS_STR:
        print(f"{WEBTORRENT_JS_OUT} is out of date")
        shutil.copyfile(WEBTORRENT_JS, WEBTORRENT_JS_OUT)

TRACKER_ANNOUNCE_LIST = [
    "wss://webtorrent-tracker.onrender.com",
    "wss://tracker.btorrent.xyz"
]
DOMAIN_NAME = os.environ.get(
    "DOMAIN_NAME", "https://webtorrent-webseed.onrender.com")
STUN_SERVERS = os.environ.get(
    "STUN_SERVERS", '"stun:relay.socket.dev:443", "stun:global.stun.twilio.com:3478"')


def filemd5(filename):
    with open(filename, mode="rb") as f:
        d = hashlib.md5()
        for buf in iter(lambda: f.read(128 * d.block_size), b""):
            d.update(buf)
    return d.hexdigest()


def get_files(file: str) -> str:
    filename = os.path.basename(file)
    md5file = os.path.join(OUT_DIR, f"{filename}.md5")
    torrent_path = os.path.join(OUT_DIR, filename + ".torrent")
    html_path = os.path.join(torrent_path + ".html")
    return md5file, torrent_path, html_path


def create_webtorrent_files(file: str) -> str:
    md5file, torrent_path, html_path = get_files(file)
    # Generate the md5 file
    md5 = filemd5(file)
    if not os.path.exists(md5file) or md5 != open(md5file).read():
        print(f"MD5 mismatch for {file}")
        for f in [md5file, torrent_path, html_path]:
            if os.path.exists(f):
                os.remove(f)
        with open(md5file, "w") as f:
            f.write(md5)
    if not os.path.exists(torrent_path):
        assert TRACKER_ANNOUNCE_LIST
        tracker_announce = "-a " + " -a ".join(TRACKER_ANNOUNCE_LIST)
        cmd = f'mktorrent "{file}" {tracker_announce} -l {CHUNK_FACTOR} -o "{torrent_path}"'
        print(f"Running: {cmd}")
        os.system(cmd)
        assert os.path.exists(torrent_path), f"Missing expected {torrent_path}"
    if not os.path.exists(html_path):
        torrent_id = f"{DOMAIN_NAME}/{os.path.basename(torrent_path)}"
        webseed = f"{DOMAIN_NAME}/content/{os.path.basename(file)}"
        html = HTML_TEMPLATE.replace("__TORRENT_URL__", torrent_id)
        html = html.replace("__WEBSEED__", webseed)
        html = html.replace("__STUN_SERVERS__", STUN_SERVERS)
        with open(html_path, encoding="utf-8", mode="w") as f:
            f.write(html)
        assert os.path.exists(html_path), f"Missing {html_path}"
    return html_path, torrent_path


# Scan DATA_DIR for movie files
os.chdir(CONTENT_DIR)

while True:
    files = os.listdir()
    files = [
        f
        for f in files
        if f.lower().endswith(".mp4") or f.lower().endswith(".webm")
    ]
    if not files:
        sys.exit(0)
    # Get the most recent time stamps
    newest_file = sorted(files, key=lambda f: os.path.getmtime(f))[0]
    # If newest_file is younger than 10 seconds, then wait then try again
    if os.path.getmtime(newest_file) > time.time() - 10:
        time.sleep(1)
        continue
    break
html_str = "<html><body><ul>"
for movie_file in files:
    try:
        iframe_src, torrent_path = create_webtorrent_files(movie_file)
        assert os.path.exists(iframe_src), f"Missing {iframe_src}, skipping"
        html_str += (
            f"""
            <li>
              <h3><a href="{os.path.basename(iframe_src)}">{os.path.basename(iframe_src)}</a></h3>
              <ul>
                <li><a href="{f"content/{os.path.basename(movie_file)}"}">{f"content/{os.path.basename(movie_file)}"}</a></li>
                <li><a href="{os.path.basename(torrent_path)}">{os.path.basename(torrent_path)}</a></li>
              </ul>
            </li>
        """)
    except Exception as e:
        print(f"Failed to create webtorrent files for {movie_file}: {e}")
        continue
html_str += "</ul></body></html>"
# Write the HTML file
index_html = os.path.join(OUT_DIR, "index.html")
print(f"Writing {index_html}")
with open(index_html, encoding="utf-8", mode="w") as f:
    f.write(html_str)

sys.exit(0)
