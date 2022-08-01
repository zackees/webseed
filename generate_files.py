"""
Service generates webtorrent files and 
"""
import os
import hashlib
import time
import sys

# Directory structure is
# DATA_DIR/content - contains *.mp4 or *.webm files
# DATA_DIR - contains the generated files
CHUNK_FACTOR = 17  # 128KB, or n^17
OUT_DIR = os.environ.get("DATA_DIR", "/var/data")
CONTENT_DIR = os.path.join(OUT_DIR, "content")
os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

TRACKER_ANNOUNCE_LIST = [
  "wss://webtorrent-tracker.onrender.com",
  "wss://tracker.btorrent.xyz"
]
DOMAIN_NAME = os.environ.get("DOMAIN_NAME", "https://webtorrent-webseed.onrender.com")
STUN_SERVERS = os.environ.get("STUN_SERVERS", '"stun:relay.socket.dev:443", "stun:global.stun.twilio.com:3478"')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>

<style>
  video {
    width: 100%;
    height: 100%;
  }

</style>

<body>
  <section>
    <h1 id="info">Movie player loading....</h1>
    <div id="content"></div>
  </section>
</body>

<script src="https://cdn.jsdelivr.net/npm/webtorrent@latest/webtorrent.min.js"></script>
<script>
  // Enable WebTorrent debugging for now.
  localStorage.debug = '*'

  const rtcConfig = {
    "iceServers": [
      {
        "urls": [
          __STUN_SERVERS__
        ]
      }
    ],
    "sdpSemantics": "unified-plan",
    "bundlePolicy": "max-bundle",
    "iceCandidatePoolsize": 1
  }

  const WEBTORRENT_CONFIG = {
    tracker: {
      rtcConfig
    }
  }

  // EXPERIMENT, does this play better with other clients?
  // const client = new WebTorrent()
  const client = new WebTorrent(WEBTORRENT_CONFIG)
  // get the current time
  const time = new Date().getTime()

  const TORRENT_URL = '__TORRENT_URL__'
  const WEBSEED = '__WEBSEED__'
  const torrent = client.add(TORRENT_URL, () => {
    console.log('ON TORRENT STARTED')
  })

  console.log("created torrent")

  /*
  torrent.on('warning', console.warn)
  torrent.on('error', console.error)
  torrent.on('download', console.log)
  torrent.on('upload', console.log)
  */

  torrent.on('warning', (a) => { console.warn(`warning: ${a}`) })
  torrent.on('error', (a) => { console.error(`error: ${a}`) })
  //torrent.on('download', (a) => { console.log(`download: ${a}`) })
  //torrent.on('upload', (a) => { console.log(`upload: ${a}`) })


  torrent.on('ready', () => {
    torrent.addWebSeed(WEBSEED)
    document.getElementById("info").innerHTML = "Movie name: " + torrent.name
    console.log('Torrent loaded!')
    console.log('Torrent name:', torrent.name)
    console.log('Found at:', new Date().getTime() - time, " in the load")
    console.log(`Files:`)
    torrent.files.forEach(file => {
      console.log('- ' + file.name)
    })
    // Torrents can contain many files. Let's use the .mp4 file
    const file = torrent.files.find(file => file.name.endsWith('.mp4') || file.name.endsWith('.webm'))
    // Display the file by adding it to the DOM
    file.appendTo('body', { muted: true, autoplay: true })
  })
</script>

</html>
"""

# import md5 lib
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
                <li><a href="{f"content/{os.path.basename(movie_file)}"}>{f"content/{os.path.basename(movie_file)}"}</a></li>
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
