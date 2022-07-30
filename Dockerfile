# FROM ubuntu:22.04
FROM --platform=linux/amd64 python:3.10.5-bullseye

# Might be necessary.
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8


RUN apt-get update && apt-get install -y --force-yes --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common \
    git-all \
    pkg-config \
    libncurses5-dev \
    libssl-dev \
    libnss3-dev \
    libexpat-dev \
    npm \
    nodejs
#&& rm -rf /var/lib/apt/lists/*;





# From the webtorrent-hybrid dockerfile.

RUN apt-get install -y \
    libgtk2.0-dev \
    libgconf-2-4 \
    libasound2 \
    libxtst6 \
    libxss1 \
    libnss3 \
    xvfb \
    git \
    make gcc g++ nodejs npm nano

RUN npm install node-pre-gyp webtorrent-cli webtorrent-hybrid http-server pm2 -g
RUN pip install magic-wormhole

# Still work in progress.

#RUN apt-get full-upgrade -y && \
#    apt-get install -y libgtk2.0-dev libgconf-2-4 libasound2 libxtst6 libxss1 libnss3 xvfb git -y && \
#    apt-get autoremove --purge -y && \
#    rm -rf /var/lib/apt/lists/* && \
#    npm i -g node-pre-gyp

WORKDIR /app
# Expose the port and then launch the app.
EXPOSE 80
COPY . .
CMD ["/bin/sh", "./run.sh"]
