set -e
cp ./README.md $DATA_DIR/README.md
rm $DATA_DIR/*.torrent* && rm  $DATA_DIR/*.md5
# --cors is required for webseed to work. Allow * and range requests
# are explicitly set.
pm2 start "http-server $DATA_DIR -p 80 --cors='*' -c-1"
# Generate files will be called whenever the content folder sees changes.
pm2 start "python ./generate_files.py" --watch $DATA_DIR/content --no-autorestart
pm2 save
# The final command is to keep the container running by streaming
# the logs.
pm2 logs
