set -e
mkdir -p .temp
export DOMAIN_NAME=localhost
export DATA_DIR=.temp
export STUN_SERVERS='"stun:relay.socket.dev:443", "stun:global.stun.twilio.com:3478"'
./run.sh
