

import time
import os

DATA_DIR = "/var/data"

def make_index_html() -> None:
  # Scan DATA_DIR for movie files
  html_str = "<html><body><ul>"
  files = os.listdir(DATA_DIR)
  for f in files:
    if f.lower().endswith(".mp4") or f.lower().endswith(".webm"):
      # Make a link to the movie
      html_str += f'<li><a href="{f}">{f}</a></li>'
  html_str += "</ul></body></html>"
  # Write the HTML file
  with open(os.path.join(DATA_DIR, "index.html"), "w") as f:
    f.write(html_str)
  


def main() -> int:
  while True:
    make_index_html()
    time.sleep(5)


if __name__ == '__main__':
  main()
