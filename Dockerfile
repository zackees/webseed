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
    && rm -rf /var/lib/apt/lists/*;

RUN npm install node-pre-gyp webtorrent-cli webtorrent-hybrid http-server pm2 -g
RUN pip install magic-wormhole yt-dlp

# Still work in progress.

#RUN apt-get full-upgrade -y && \
#    apt-get install -y libgtk2.0-dev libgconf-2-4 libasound2 libxtst6 libxss1 libnss3 xvfb git -y && \
#    apt-get autoremove --purge -y && \
#    rm -rf /var/lib/apt/lists/* && \
#    npm i -g node-pre-gyp


# Expose the port and then launch the app.
EXPOSE 80
COPY . .
ENV DOMAIN_NAME https://webtorrent-webseed.onrender.com
ENV DATA_DIR /var/data
CMD ["/bin/sh", "./run.sh"]
