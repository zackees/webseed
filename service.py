import time
import os
import subprocess

DATA_DIR = "/var/data"


def create_webtorrent_files(file: str) -> None:
    torrent_path = os.path.join(DATA_DIR, file + ".torrent")
    magnet_path = os.path.join(DATA_DIR, file + ".magnet")
    if not os.path.exists(torrent_path):
        cmd = f"webtorrent-hybrid create {file} -o {file}.torrent"
        os.system(cmd)
    if not os.path.exists(magnet_path):
        # Now create the magnet file
        cmd = f"webtorrent-hybrid seed {file} -q"
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        # Wait for the first line to appear from stdout
        magneturi = proc.stdout.readline().strip()
        proc.kill()
        # Write the magnet file
        with open(f"{file}.magnet", "w") as f:
            f.write(magneturi)
    assert os.path.exists(torrent_path)
    assert os.path.exists(magnet_path)


def make_index_html() -> None:
    # Scan DATA_DIR for movie files
    html_str = "<html><body><ul>"
    files = os.listdir(DATA_DIR)
    files = [
        f for f in files if f.lower().endswith(".mp4") or f.lower().endswith(".webm")
    ]
    for f in files:
        create_webtorrent_files(f)
        # Make a link to the movie
        html_str += f'<li><a href="{f}">{f}</a></li>'
    html_str += "</ul></body></html>"
    # Write the HTML file
    with open(os.path.join(DATA_DIR, "_index.html"), "w") as f:
        f.write(html_str)


def main() -> int:
    while True:
        make_index_html()
        time.sleep(5)


if __name__ == "__main__":
    main()
