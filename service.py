"""
Service generates webtorrent files and index.html
"""

import os
import subprocess

DATA_DIR = os.environ.get("DATA_DIR", "/var/data")

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


def create_webtorrent_files(file: str) -> None:
    torrent_path = os.path.join(file + ".torrent")
    magnet_path = os.path.join(torrent_path + ".magnet.txt")
    html_path = os.path.join(torrent_path + ".html")
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
        html = HTML_TEMPLATE.replace("__TORRENT_ID__", torrent_path).replace(
            "__WEBSEED__", f"{DOMAIN_NAME}/{file}"
        )
        with open(html_path, "w") as f:
            f.write(html)
        assert os.path.exists(html_path), f"Missing {html_path}"


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
            create_webtorrent_files(file)
            html_str += f'<li><a href="{file}">{file}</a></li>'
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
