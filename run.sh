cp /app/README.md /var/data/README.md
pm2 start "python service.py"
pm2 start "http-server /var/data -p 80 --cors='*'"
pm2 save
while true; do sleep 10000; done
