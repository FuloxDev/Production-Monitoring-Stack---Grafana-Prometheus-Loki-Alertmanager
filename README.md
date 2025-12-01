# 🔍 Production Monitoring Stack

Production-grade, security-hardened monitoring and observability stack for microservice infrastructure. Provides comprehensive monitoring, alerting, and log aggregation for microservices, Kafka clusters, and any language supported applications (here using Node.js application).

## 📋 Table of Contents

- [Overview](#overview)
- [Stack Components](#stack-components)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Alert Rules](#alert-rules)
- [Architecture](#architecture)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This monitoring stack is specifically designed for LCX cryptocurrency exchange infrastructure, providing:

- **Push-Based Metrics**: Grafana Alloy agents push metrics to Prometheus via remote_write API (not pull-based scraping)
- **Real-time Metrics**: System, application, and business metrics collection
- **Kafka Monitoring**: Comprehensive Kafka cluster health monitoring via JMX
- **APM**: Application performance monitoring for any service (irrespective of language)
- **Centralized Logging**: Log aggregation with Grafana Loki
- **Multi-Channel Alerting**: Slack notifications with severity-based routing
- **Security Hardened**: Container security, TLS encryption, bcrypt authentication

## 🏗️ Stack Components

| Component | Version | Purpose |
|-----------|---------|---------|
| **Prometheus** | 3.5.0 | Time-series metrics database with 15-day retention |
| **Grafana** | 12.0.2 Enterprise | Visualization and dashboarding platform |
| **Alertmanager** | 0.28.1 | Alert routing with Slack integration |
| **Loki** | 3.4.5 | Log aggregation and querying |
| **Grafana Alloy** | 1.10.1 | Unified observability agent for metrics/logs |

## ✨ Features

### Monitoring Coverage
- ✅ **Monitoring Stack Self-Monitoring**: Prometheus, Grafana, Alertmanager, Loki metrics
- ✅ **System Metrics**: CPU, memory, disk, network, filesystem via Alloy node exporter
- ✅ **Docker Containers**: Container discovery and metrics collection
- ✅ **GitLab Runner**: CI/CD pipeline runner metrics
- ✅ **Accounts Service**: Node.js application metrics (heap, event loop, memory)
- ✅ **Kafka Cluster**: Broker health, partition replication, ISR monitoring
- ✅ **Log Aggregation**: System and container logs via Loki

### Pre-Configured Alerts
- 🔔 **Accounts Service**: High memory, heap usage, event loop lag, high error rates
- 🔔 **Kafka**: Broker down, under-replicated partitions, consumer lag, disk space
- 🔔 **System**: Resource exhaustion, service unavailability

### Security Features
- 🔒 **TLS/HTTPS**: All services encrypted
- 🔒 **Basic Auth**: Password-protected UIs
- 🔒 **Container Hardening**: Read-only filesystems, dropped capabilities
- 🔒 **Network Isolation**: Private bridge network

## 📦 Prerequisites

- Docker 24.x+
- Docker Compose 2.x+
- 4GB+ RAM
- 50GB+ disk space
- Ports available: 3000, 9090, 9093, 3100, 12345
- Self-signed or CA-issued SSL certificates

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://gitlab.com/lcx-global/monitoring-stack.git
cd monitoring-stack/monitoring
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your configuration
nano .env
```

**Required Environment Variables:**
```bash
# Environment
ENV=production  # or staging/development

# Grafana Admin
GF_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=your-secure-password
GRAFANA_DOMAIN=monitoring.yourdomain.com

# Grafana Metrics Endpoint
GF_METRICS_ENABLED=true
GF_METRICS_BASIC_AUTH_USERNAME=prometheus
GF_METRICS_BASIC_AUTH_PASSWORD=your-metrics-password

# Prometheus Auth
PROM_USERNAME=admin
PROM_PASSWORD=your-prom-password

# Alertmanager Auth
ALERTMANAGER_USERNAME=admin
ALERTMANAGER_PASSWORD=your-alert-password

# Kafka JMX Exporters (if monitoring Kafka)
KAFKA_JMX_NODE1=kafka-node1:9991
KAFKA_JMX_NODE2=kafka-node2:9992
KAFKA_JMX_NODE3=kafka-node3:9993

# Slack Notifications
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=monitoring-alerts

# Kafka-specific Slack (optional)
SLACK_KAFKA_WEBHOOK=https://hooks.slack.com/services/YOUR/KAFKA/WEBHOOK
SLACK_KAFKA_CHANNEL=kafka-monitoring
```

### 3. Generate SSL Certificates and Authentication

**Generate SSL Certificates:**

The repository includes certificates in `./certs/` directory. For new deployments, generate your own:

```bash
cd certs

# Generate certificate for each service
for service in grafana prometheus alertmanager loki; do
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ${service}.key -out ${service}.crt \
    -subj "/C=LI/ST=Vaduz/L=Vaduz/O=LCX/CN=${service}.monitoring.local"
done

cd ..
```

**Generate Authentication Credentials:**

Each service uses `web.yml` for basic authentication. Generate bcrypt-hashed passwords:

```bash
# Install requirements (if not already installed)
pip install bcrypt pyyaml --break-system-packages

# Generate Prometheus credentials
cd config
python3 genpass.py
# Enter username and password when prompted
# This creates web.yml with bcrypt-hashed credentials
cd ..

# Generate Alertmanager credentials
cd alertmanager/auth
python3 ../config/genpass.py  # Or copy genpass.py here
cd ../..

# Generate Loki credentials (if authentication enabled)
cd loki
python3 genpass.py
cd ..
```

The `genpass.py` script creates a `web.yml` file with:
- TLS configuration (cert paths, TLS versions, cipher suites)
- Bcrypt-hashed passwords for basic authentication
- Username mapping

### 4. Start the Stack

```bash
# Process templates and start services
./pre-process.sh
```

**What this script does:**
1. Stops any running containers (`docker-compose down`)
2. Loads environment variables from `.env`
3. Generates configuration files from templates using `envsubst`:
   - `prometheus/prometheus.yml` from `prometheus.yml.tmpl`
   - `alertmanager/config.yml` from `config.yml.tmpl`
   - `config/alloy-monitoring.alloy` from `alloy-monitoring.alloy.tmpl`
4. Starts all services (`docker-compose up -d`)

### 5. Verify Services

```bash
# Check all services are running
docker-compose ps

# Should show 5 services in "Up" state:
# - grafana (port 3000)
# - prometheus (port 9090)
# - alertmanager (port 9093)
# - loki (port 3100)
# - alloy-local (port 12345)

# Check logs
docker-compose logs -f --tail=50
```

### 6. Access Services

- **Grafana**: https://localhost:3000
  - Username: from `GF_ADMIN_USER`
  - Password: from `GF_SECURITY_ADMIN_PASSWORD`

- **Prometheus**: http://localhost:9090
  - Basic Auth: `PROM_USERNAME` / `PROM_PASSWORD`

- **Alertmanager**: http://localhost:9093
  - Basic Auth: `ALERTMANAGER_USERNAME` / `ALERTMANAGER_PASSWORD`

- **Loki**: http://localhost:3100

- **Alloy**: http://localhost:12345

## 🔄 Architecture: Push-Based Metrics Collection

**CRITICAL: This stack uses a PUSH-BASED architecture, NOT traditional pull-based Prometheus scraping.**

### How It Works

```
┌──────────────────────────────────────────────────────────┐
│                  Grafana Alloy Agents                     │
│              (Deployed on target systems)                 │
│                                                           │
│  • Collect system metrics (node_exporter)                │
│  • Collect Docker container metrics                      │
│  • Collect application metrics                           │
│  • Scrape monitoring stack metrics internally            │
└────────────────┬─────────────────────────────────────────┘
                 │
                 │ Push via Remote Write API
                 ▼
┌──────────────────────────────────────────────────────────┐
│              Prometheus (Central Server)                  │
│         http://prometheus:9090/api/v1/write              │
│                                                           │
│  • Receives metrics from all Alloy agents                │
│  • Stores time-series data (15-day retention)            │
│  • Evaluates alert rules                                 │
│  • NO direct target scraping configured                  │
└──────────────────────────────────────────────────────────┘
```

### Key Differences from Traditional Prometheus

| Traditional (Pull) | This Stack (Push) |
|-------------------|-------------------|
| Prometheus scrapes targets | Alloy agents push to Prometheus |
| Requires network access to all targets | Targets only need outbound access |
| Configured in `prometheus.yml` scrape_configs | Configured in Alloy agent files |
| Service discovery needed | Agents self-register via push |
| Complex firewall rules | Simple: Allow outbound to Prometheus |

### Alloy Configuration

The local Alloy agent (`alloy-local`) monitors the monitoring stack itself:

```alloy
// Push endpoint configuration
prometheus.remote_write "default" {
  endpoint {
    url = "${PROM_URL}"  // http://prometheus:9090/api/v1/write
    basic_auth {
      username = "${PROM_USERNAME}"
      password = "${PROM_PASSWORD}"
    }
  }
}

// System metrics - pushes to Prometheus
prometheus.scrape "monitoring_stack_server_metrics" {
  targets = prometheus.exporter.unix.node.targets
  forward_to = [prometheus.remote_write.default.receiver]
}

// Self-monitoring - stack components push their own metrics
prometheus.scrape "prometheus_metrics" {
  targets = [{ __address__ = "prometheus:9090" }]
  forward_to = [prometheus.remote_write.default.receiver]
}
```

### Deploying Additional Alloy Agents

To monitor other servers/applications:

1. **Deploy Alloy agent** on target system
2. **Configure remote_write** pointing to your Prometheus
3. **Add scrape configs** for applications on that system
4. **Metrics automatically appear** in Prometheus

Example for external Alloy agent:
```alloy
prometheus.remote_write "central" {
  endpoint {
    url = "https://prometheus.yourdomain.com:9090/api/v1/write"
    basic_auth {
      username = "remote-agent"
      password = "secure-password"
    }
  }
}
```

## ⚙️ Configuration

### Adding Monitoring Targets

**Since this is a push-based architecture, you DON'T add targets to Prometheus directly.**

Instead, deploy Grafana Alloy agents on the systems you want to monitor:

**Option 1: Modify local Alloy configuration** (for co-located services)

Edit `config/alloy-monitoring.alloy.tmpl`:

```alloy
// Add new scrape job
prometheus.scrape "your_application" {
  targets = [
    {
      __address__ = "your-app:8080",
      __metrics_path__ = "/metrics",
    },
  ]
  
  scrape_interval = "15s"
  job_name = "your-application"
  forward_to = [prometheus.remote_write.default.receiver]
}
```

**Option 2: Deploy Alloy on remote systems** (recommended for distributed monitoring)

1. Install Grafana Alloy on target server
2. Configure it to push to your central Prometheus:

```alloy
prometheus.remote_write "central_prometheus" {
  endpoint {
    url = "https://prometheus.yourdomain.com:9090/api/v1/write"
    basic_auth {
      username = "agent-username"
      password = "agent-password"
    }
    tls_config {
      insecure_skip_verify = false  // Use true for self-signed certs
    }
  }
}

// Collect metrics from local application
prometheus.scrape "local_app" {
  targets = [{ __address__ = "localhost:8080" }]
  forward_to = [prometheus.remote_write.central_prometheus.receiver]
}
```

3. Restart Alloy: `systemctl restart alloy`

After configuration changes, regenerate and restart:
```bash
./pre-process.sh
```

### Adding Kafka Monitoring

Kafka metrics are collected via JMX exporters running on Kafka nodes. Update `.env`:

```bash
KAFKA_JMX_NODE1=kafka-broker-1.internal:<PORT1>
KAFKA_JMX_NODE2=kafka-broker-2.internal:<PORT2>  
KAFKA_JMX_NODE3=kafka-broker-3.internal:<PORT3>
```

Deploy Alloy agents on Kafka nodes to scrape JMX exporters and push to Prometheus.

### Customizing Alert Rules

Alert rules are located in `prometheus/rules/`:

- **`nodejs-alerts.yml`** - Node.js application monitoring
  - Service health, memory, heap, event loop
  - Error rates, response times
  - CPU and resource usage

- **`kafka-alerts.yml`** - Kafka cluster monitoring
  - Broker health and state
  - Partition replication (URPs, offline partitions)
  - Consumer lag
  - ISR shrinks/expansions
  - Disk space

- **`test-alert.yml`** - Test alerts for validation

Edit these files to customize thresholds and add new alerts.

### Configuring Slack Notifications

Alertmanager configuration in `alertmanager/config.yml.tmpl` routes alerts by severity:

```yaml
routes:
  # Kafka-specific alerts
  - match:
      service: kafka
    receiver: 'slack-kafka'
    
  # Critical alerts (30min repeat)
  - match:
      severity: critical
    receiver: 'slack-critical'
    repeat_interval: 30m
    
  # Warning alerts (12h repeat)
  - match:
      severity: warning
    receiver: 'slack-warning'
    repeat_interval: 12h
    
  # Info alerts (24h repeat)
  - match:
      severity: info
    receiver: 'slack-info'
    repeat_interval: 24h
```

Update `.env` with your Slack webhooks and channels.

## 📊 Alert Rules

### Accounts Service Alerts

**Critical:**
- `AccountsServiceDown` - Service unavailable for 1 minute
- `HighMemoryUsage` - Memory usage > 1GB for 5 minutes
- `HighHeapUsage` - Heap usage > 90% for 5 minutes
- `HighEventLoopLag` - Event loop lag > 0.1s for 2 minutes

**Warning:**
- `HighErrorRate` - Error rate > 5% for 5 minutes
- `SlowResponseTime` - P95 response time > 2s
- `HighCPUUsage` - CPU > 80% for 10 minutes

### Kafka Cluster Alerts

**Critical:**
- `KafkaBrokerDown` - Broker not in running state
- `KafkaUnderReplicatedPartitions` - URPs > 0 for 5 minutes
- `KafkaOfflinePartitions` - Offline partitions detected
- `KafkaConsumerLagHigh` - Consumer lag > 10000

**Warning:**
- `KafkaISRShrinks` - In-sync replicas decreasing
- `KafkaDiskSpaceWarning` - Disk usage > 75%
- `KafkaHighProducerLatency` - Producer latency > 500ms

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Target Systems                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Server 1  │  │   Server 2  │  │   Server 3  │        │
│  │             │  │             │  │             │        │
│  │ Alloy Agent │  │ Alloy Agent │  │ Alloy Agent │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                 │
└─────────┼────────────────┼────────────────┼─────────────────┘
          │                │                │
          │    Push Metrics via Remote Write API
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              Prometheus (Port 9090)                          │
│         /api/v1/write endpoint enabled                       │
│  • Receives metrics from all Alloy agents (PUSH)            │
│  • Stores time-series data (15 days retention)              │
│  • Evaluates alert rules every 15s                          │
│  • NO pull-based scraping configured                        │
└──────────────┬──────────────────────────────────────────────┘
               │
               ├──────────────┐
               │              │
     ┌─────────▼────┐  ┌──────▼──────────┐
     │ Alertmanager │  │     Grafana     │
     │  (Port 9093) │  │  (Port 3000)    │
     │              │  │                 │
     │ • Routes by  │  │ • Dashboards    │
     │   severity   │  │ • Queries via   │
     │ • Slack      │  │   PromQL        │
     │   webhooks   │  │ • Loki logs     │
     └──────┬───────┘  └─────────────────┘
            │
            ▼
     ┌──────────────┐
     │    Slack     │
     │  #critical   │
     │  #kafka      │
     │  #warnings   │
     └──────────────┘

┌─────────────────────────────────────────────────────────────┐
│          Local Alloy Agent (alloy-local)                     │
│                                                              │
│  Monitors the monitoring stack itself:                      │
│  • System metrics (CPU, RAM, disk)                         │
│  • Docker container metrics                                │
│  • Prometheus metrics                                      │
│  • Grafana metrics                                         │
│  • Alertmanager metrics                                    │
│  • GitLab Runner metrics                                   │
│                                                             │
│  Pushes to → Prometheus remote_write endpoint              │
└─────────────────────────────────────────────────────────────┘
```

### Key Architecture Points

1. **Push-Based Collection**: Alloy agents push metrics to Prometheus (not pull-based)
2. **Remote Write API**: Prometheus `/api/v1/write` endpoint receives metrics
3. **Distributed Agents**: Deploy Alloy on each system you want to monitor
4. **Self-Monitoring**: Local Alloy monitors the monitoring stack itself
5. **Centralized Storage**: All metrics centralized in Prometheus TSDB

### Network Configuration

All services run on isolated bridge network `172.20.0.0/16`:
- Services communicate internally via Docker DNS
- Ports bound to `127.0.0.1` (localhost only)
- Requires reverse proxy for external access

### Data Retention

- **Prometheus**: 15 days, 10GB size limit
- **Alertmanager**: 120 hours alert history
- **Loki**: Configured retention periods

## 🔐 Security

### Container Hardening

All services run with:
- **Read-only root filesystem** (`read_only: true`)
- **Dropped capabilities** (`cap_drop: ALL`)
- **Non-root users** (nobody:nobody, specific UIDs)
- **Security options** (`no-new-privileges:true`)
- **Limited tmpfs** (size-restricted temporary storage)

### Authentication

Every service requires authentication:
- **Grafana**: Admin username/password
- **Prometheus**: Basic auth via `config/web.yml`
- **Alertmanager**: Basic auth via `alertmanager/auth/web.yml`
- **Loki**: Authentication via `loki/web.yml`

### TLS/HTTPS

- Grafana serves HTTPS on port 3000
- Certificates mounted read-only from `./certs/`
- Self-signed or CA-issued certificates supported

### Best Practices

1. **Change default passwords** immediately
2. **Use strong passwords** (20+ characters, random)
3. **Rotate credentials** every 90 days
4. **Bind to localhost** - use reverse proxy (Nginx/Traefik) for external access
5. **Regular updates**: `docker-compose pull && ./pre-process.sh`
6. **Review logs**: `docker-compose logs -f`

## 🔧 Troubleshooting

### Services Won't Start

```bash
# Check logs for specific service
docker-compose logs grafana
docker-compose logs prometheus

# Common issues:
# 1. Port already in use
sudo netstat -tlnp | grep -E "3000|9090|9093|3100"

# 2. Certificate issues
ls -la certs/
# Ensure all .crt and .key files exist

# 3. Environment variables not loaded
cat .env
# Verify all required variables are set

# 4. Configuration template errors
cat prometheus/prometheus.yml
# Check for ${VARIABLE} placeholders that weren't replaced
```

### Prometheus Not Receiving Metrics

**Remember: Metrics are PUSHED to Prometheus, not pulled.**

```bash
# Check if remote write endpoint is enabled
docker-compose exec prometheus ps | grep prometheus
# Should see: --web.enable-remote-write-receiver

# Check Prometheus logs for incoming writes
docker-compose logs prometheus | grep "remote_write"

# Verify Alloy is pushing metrics
docker-compose logs alloy-local | grep -i "error\|push\|write"

# Check Alloy UI for remote write status
curl http://localhost:12345/

# Test if remote write endpoint is accessible
curl -X POST \
  -H "Content-Type: application/x-protobuf" \
  http://localhost:9090/api/v1/write \
  --user admin:password

# Check if metrics are arriving in Prometheus
curl http://localhost:9090/api/v1/query?query=up
# Should show metrics from Alloy agents
```

**Common Issues:**

1. **Alloy agent not pushing**:
   ```bash
   # Check Alloy configuration
   docker-compose exec alloy-local cat /etc/alloy/config.alloy
   
   # Verify remote_write endpoint URL
   echo $PROM_URL  # Should be http://prometheus:9090/api/v1/write
   ```

2. **Authentication failure**:
   ```bash
   # Verify credentials match
   cat .env | grep PROM_
   docker-compose exec prometheus cat /etc/config/web.yml
   ```

3. **Network connectivity**:
   ```bash
   # Test from Alloy to Prometheus
   docker-compose exec alloy-local wget -O- http://prometheus:9090/-/healthy
   ```

### Alerts Not Firing

```bash
# Check if alerts are defined
curl http://localhost:9090/api/v1/rules

# Check active alerts
curl http://localhost:9093/api/v1/alerts

# Test Slack webhook manually
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert from monitoring stack"}' \
  $SLACK_WEBHOOK

# Check Alertmanager logs
docker-compose logs alertmanager | grep -i error
```

### Configuration Not Generated from Templates

```bash
# Run pre-process manually and check for errors
./pre-process.sh

# Verify envsubst is available
which envsubst

# Check if templates exist
ls -la prometheus/prometheus.yml.tmpl
ls -la alertmanager/config.yml.tmpl
ls -la config/alloy-monitoring.alloy.tmpl

# Manually test template substitution
export $(grep -v '^#' .env | grep -v '^$' | xargs)
envsubst < prometheus/prometheus.yml.tmpl
```

### Grafana Can't Connect to Datasources

```bash
# Check if Prometheus is accessible from Grafana
docker-compose exec grafana wget -O- http://prometheus:9090/-/healthy

# Check if Loki is accessible
docker-compose exec grafana wget -O- http://loki:3100/ready

# Verify datasource configuration in Grafana UI:
# Configuration → Data Sources → Prometheus
# URL should be: http://prometheus:9090
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Reduce retention if needed (edit docker-compose.yml):
# Prometheus command section:
# --storage.tsdb.retention.time=7d
# --storage.tsdb.retention.size=5GB

# Restart services
./pre-process.sh
```

## 📈 Maintenance

### Regular Tasks

**Daily:**
- Check service health: `docker-compose ps`
- Review active alerts in Alertmanager
- Monitor disk usage: `df -h`

**Weekly:**
- Review Grafana dashboards
- Verify backup integrity
- Check Prometheus target health

**Monthly:**
- Update Docker images: `docker-compose pull`
- Rotate credentials
- Review and optimize alert rules
- Capacity planning

### Backup

```bash
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Backup Prometheus data
docker run --rm \
  -v monitoring_prom_data:/data \
  -v $(pwd)/$BACKUP_DIR:/backup \
  alpine tar czf /backup/prometheus-${DATE}.tar.gz -C /data .

# Backup Grafana
docker run --rm \
  -v monitoring_grafana-storage:/data \
  -v $(pwd)/$BACKUP_DIR:/backup \
  alpine tar czf /backup/grafana-${DATE}.tar.gz -C /data .

# Backup configuration
tar czf $BACKUP_DIR/config-${DATE}.tar.gz \
  prometheus/ alertmanager/ loki/ config/ .env.example

echo "Backup completed: ${DATE}"
```

### Updates

```bash
# Pull latest images
docker-compose pull

# Recreate containers with new images
./pre-process.sh

# Verify all services are running
docker-compose ps

# Check logs for errors
docker-compose logs -f --tail=100
```

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

**DevSecOps Team @ LCX**  
Cryptocurrency Exchange Infrastructure & Monitoring

## 📞 Support

- **GitLab Issues**: https://gitlab.com/lcx-global/monitoring-stack/-/issues
- **Internal Slack**: #devops-monitoring
- **Email**: devops@lcx.com

---

**Production-ready monitoring for cryptocurrency exchange infrastructure** 🔍📊
