cp /app/README.md /var/data/README.md
pm2 start "python service.py"
pm2 save
http-server /var/data -p 80 --cors='*'
