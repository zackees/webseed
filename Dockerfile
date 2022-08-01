# FROM ubuntu:22.04
FROM --platform=linux/amd64 python:3.10.5-slim-bullseye

WORKDIR /app

# Might be necessary.
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --force-yes --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl nodejs npm nano \
    sudo \
    mktorrent \
    && rm -rf /var/lib/apt/lists/*;

RUN npm install http-server pm2 -g
RUN pip install magic-wormhole yt-dlp


# Expose the port and then launch the app.
EXPOSE 80
COPY . .
ENV DOMAIN_NAME https://webtorrent-webseed.onrender.com
ENV DATA_DIR /var/data
ENV STUN_SERVERS '"stun:relay.socket.dev:443", "stun:global.stun.twilio.com:3478"'
ENV DOMAIN_NAME https://webtorrent-webseed.onrender.com
CMD ["/bin/sh", "./run.sh"]
