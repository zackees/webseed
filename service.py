import time
import os
import subprocess

DATA_DIR = os.environ.get('DATA_DIR', "/var/data")


def create_webtorrent_files(file: str) -> None:
    torrent_path = os.path.join(file + ".torrent")
    magnet_path = os.path.join(torrent_path + ".magnet.txt")
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
