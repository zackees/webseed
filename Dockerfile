FROM node:18-alpine
WORKDIR /app
RUN npm install -g node-pre-gyp webtorrent-cli webtorrent-hybrid http-server
EXPOSE 80
COPY . .
# CMD ["/bin/sh", "./run.sh"]
CMD http-server . -p 80 --cors='*'