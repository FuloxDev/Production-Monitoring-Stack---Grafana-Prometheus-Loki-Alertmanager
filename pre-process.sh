#!/bin/sh

docker-compose down

# Load environment variables (filtering out comments and empty lines)
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# Generate configuration files from templates
envsubst < ./prometheus/prometheus.yml.tmpl > ./prometheus/prometheus.yml
envsubst '${SLACK_WEBHOOK},${SLACK_CHANNEL},${SLACK_KAFKA_WEBHOOK},${SLACK_KAFKA_CHANNEL}' < ./alertmanager/config.yml.tmpl > ./alertmanager/config.yml
envsubst < ./config/alloy-monitoring.alloy.tmpl > ./config/alloy-monitoring.alloy

# Start Docker Compose
docker-compose up -d