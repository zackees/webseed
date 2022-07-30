set -e
cd /var/data && rm *.torrent* && rm *.md5
cp /app/README.md /var/data/README.md
# Generate files will be called whenever the content folder sees changes.
pm2 start "python /app/generate_files.py" --watch /var/data/content --no-autorestart
# --cors is required for webseed to work. Allow * and range requests
# are explicitly set.
pm2 start "http-server /var/data -p 80 --cors='*' -c-1"
pm2 save
# The final command is to keep the container running by streaming
# the logs.
pm2 logs
