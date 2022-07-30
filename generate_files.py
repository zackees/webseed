"""
Service generates webtorrent files and 
"""
import os
import subprocess
import hashlib

# Directory structure is
# DATA_DIR/content - contains *.mp4 or *.webm files
# DATA_DIR - contains the generated files
DATA_DIR = os.environ.get("DATA_DIR", "/var/data")
CONTENT_DIR = os.path.join(DATA_DIR, "content")
OUT_DIR = DATA_DIR
os.makedirs(DATA_DIR, exist_ok=True)

DOMAIN_NAME = "https://webtorrent-webseed.onrender.com"


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
          "stun:relay.socket.dev:443",
          "stun:global.stun.twilio.com:3478"
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

  const TORRENT_ID = '__TORRENT_ID__'
  const WEBSEED = '__WEBSEED__'
  const torrent = client.add(TORRENT_ID, () => {
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
    with open(filename, 'rb') as f:
        d = hashlib.md5()
        for buf in iter(lambda: f.read(128 * d.block_size), b''):
            d.update(buf)
    return d.hexdigest()


def create_webtorrent_files(file: str) -> str:
    filename = os.path.basename(file)
    md5file = os.path.join(OUT_DIR, f"{filename}.md5")
    torrent_path = os.path.join(OUT_DIR, filename + ".torrent")
    magnet_path = os.path.join(torrent_path + ".magnet.txt")
    html_path = os.path.join(torrent_path + ".html")

    # Generate the md5 file
    md5 = filemd5(file)
    if not os.path.exists(md5file) or md5 != open(md5file).read():
        print(f"MD5 mismatch for {file}")
        for f in [md5file, torrent_path, magnet_path, html_path]:
            if os.path.exists(f):
                os.remove(f)
        with open(md5file, "w") as f:
            f.write(md5)
    if not os.path.exists(torrent_path):
        cmd = f'webtorrent-hybrid create "{file}" -o "{torrent_path}"'
        print(f"Running: {cmd}")
        os.system(cmd)
        assert os.path.exists(torrent_path), f"Missing expected {torrent_path}"
    if not os.path.exists(magnet_path):
        # Now create the magnet file
        cmd = f'webtorrent-hybrid seed "{file}" -q'
        print(f"Running: {cmd}")
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        # Wait for the first line to appear from stdout
        print("Waiting for magnet url")
        magneturi = proc.stdout.readline().strip()
        print(f"Got magnet url: {magneturi}")
        proc.kill()
        # Write the magnet file
        with open(magnet_path, "w") as f:
            f.write(magneturi)
        assert os.path.exists(magnet_path), f"Missing {magnet_path}"
    if not os.path.exists(html_path) and os.path.exists(magnet_path):
        magneturi = open(magnet_path).read().strip()
        html = HTML_TEMPLATE.replace("__TORRENT_ID__", os.path.relpath(torrent_path, OUT_DIR))
        html = html.replace("__WEBSEED__", f"{DOMAIN_NAME}/{os.path.relpath(file, OUT_DIR)}")
        with open(html_path, "w") as f:
            f.write(html)
        assert os.path.exists(html_path), f"Missing {html_path}"
    return html_path


def main() -> int:
    # Scan DATA_DIR for movie files
    os.chdir(DATA_DIR)
    html_str = "<html><body><ul>"
    files = os.listdir()
    files = [
        f for f in files if f.lower().endswith(".mp4") or f.lower().endswith(".webm")
    ]
    for file in files:
        try:
            iframe_src = create_webtorrent_files(file)
            assert os.path.exists(iframe_src), f"Missing {iframe_src}, skipping"
            html_str += f'<li><h3><a href="{iframe_src}">{file}</a></h3></li>'
        except Exception as e:
            print(f"Failed to create webtorrent files for {file}: {e}")
            continue
    html_str += "</ul></body></html>"
    # Write the HTML file
    index_html = "_index.html"
    print(f"Writing {index_html}")
    with open(index_html, "w") as f:
        f.write(html_str)
    return 0


if __name__ == "__main__":
    main()
