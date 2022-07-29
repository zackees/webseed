set -e
cp /app/README.md /var/data/README.md
cp /app/service.py /var/data/service.py
pm2 start "python /var/data/service.py" --watch
pm2 start "http-server /var/data -p 80 --cors='*'"
pm2 save
while true; do sleep 10000; done
