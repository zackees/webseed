import time
import os
import subprocess

DATA_DIR = "/var/data"


def create_webtorrent_files(file: str) -> None:
    torrent_path = os.path.join(file + ".torrent")
    magnet_path = os.path.join(torrent_path + ".magnet")
    if not os.path.exists(torrent_path):
        cmd = f"webtorrent-hybrid create {file} -o {file}.torrent"
        print(f"Running: {cmd}")
        os.system(cmd)
    if not os.path.exists(magnet_path):
        # Now create the magnet file
        cmd = f"webtorrent-hybrid seed {file} -q"
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
        with open(f"{file}.magnet", "w") as f:
            f.write(magneturi)
    assert os.path.exists(torrent_path), f"Missing {torrent_path}"
    assert os.path.exists(magnet_path), f"Missing {magnet_path}"


def make_index_html() -> None:
    # Scan DATA_DIR for movie files
    html_str = "<html><body><ul>"
    files = os.listdir(DATA_DIR)
    files = [
        f for f in files if f.lower().endswith(".mp4") or f.lower().endswith(".webm")
    ]
    for file in files:
      create_webtorrent_files(file)
    for file in files:
        # Make a link to the movie
        html_str += f'<li><a href="{file}">{file}</a></li>'
    html_str += "</ul></body></html>"
    # Write the HTML file
    index_html = os.path.join(DATA_DIR, "_index.html")
    print(f"Writing {index_html}")
    with open(index_html, "w") as f:
        f.write(html_str)


def main() -> int:
    make_index_html()



if __name__ == "__main__":
    main()
