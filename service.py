

import time
import os
import subprocess

DATA_DIR = "/var/data"

def create_webtorrent_files(file: str) -> None:
  # Check if the magnet file exists
  magnet_path = os.path.join(DATA_DIR, file + ".magnet")
  if os.path.exists(magnet_path):
    return
  # Create a magnet file
  #subprocess.run(["mktorrent", "-a", "http://localhost:8080", "-o", magnet_path, os.path.join(DATA_DIR, file)])
  #return
  #pass
  cmd = f'webtorrent-hybrid create -o {file}.torrent'
  os.system(cmd)


def make_index_html() -> None:
  # Scan DATA_DIR for movie files
  html_str = "<html><body><ul>"
  files = os.listdir(DATA_DIR)
  for f in files:
    if f.lower().endswith(".mp4") or f.lower().endswith(".webm"):
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


if __name__ == '__main__':
  main()
