set -e
cp /app/README.md /var/data/README.md
# Create services and start running them.
pm2 start "python /app/generate_files.py" --watch /var/data/content --restart-delay=10000
pm2 start "http-server /var/data -p 80 --cors='*'"
pm2 save
# The final command is to keep the container running by streaming
# the logs.
pm2 logs
