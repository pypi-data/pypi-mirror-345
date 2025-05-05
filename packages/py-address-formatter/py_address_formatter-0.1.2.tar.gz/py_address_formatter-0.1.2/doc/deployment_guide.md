# Address Formatter Deployment Guide

This guide provides step-by-step instructions for deploying the Address Formatter to a production environment.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Manual Deployment](#manual-deployment)
6. [Post-Deployment Validation](#post-deployment-validation)
7. [Monitoring Setup](#monitoring-setup)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

- Python 3.9+ (for manual deployment)
- Docker and Docker Compose (for containerized deployment)
- Kubernetes cluster (for Kubernetes deployment)
- Access to the repository (for pulling the code)
- Access to monitoring infrastructure (Prometheus, Grafana, etc.)

## Deployment Options

The Address Formatter can be deployed in multiple ways:

1. **Docker Deployment**: Recommended for most cases
2. **Kubernetes Deployment**: For large-scale or cloud deployments
3. **Manual Deployment**: For testing or specialized environments

## Docker Deployment

### Step 1: Clone the repository

```bash
git clone --recurse-submodules https://github.com/yourusername/pyaddress.git
cd pyaddress
```

### Step 2: Configure environment

Create a `.env.production` file in the root directory with your settings:

```bash
# Use the automated script
python -m config.production

# Or manually copy from the template
cp .env.example .env.production
# Edit .env.production with your settings
```

### Step 3: Build the Docker image

```bash
docker build -t address-formatter:latest .
```

### Step 4: Run using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3'
services:
  api:
    image: address-formatter:latest
    ports:
      - "8000:8000"
    environment:
      - ADDRESS_API_HOST=0.0.0.0
      - ADDRESS_API_PORT=8000
      - ADDRESS_API_WORKERS=4
    restart: unless-stopped
    volumes:
      - ./data:/app/data
  
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/alerts.rules:/etc/prometheus/alerts.rules
    restart: unless-stopped
    depends_on:
      - api
```

Start the services:

```bash
docker-compose up -d
```

## Kubernetes Deployment

### Step 1: Prepare Kubernetes manifests

Create the namespace:

```bash
kubectl create namespace address-formatter
```

Create ConfigMap for configuration:

```yaml
# config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: address-formatter-config
  namespace: address-formatter
data:
  ADDRESS_API_HOST: "0.0.0.0"
  ADDRESS_API_PORT: "8000"
  ADDRESS_API_WORKERS: "4"
  ADDRESS_ENABLE_ML: "true"
  ADDRESS_CACHE_SIZE: "10000"
```

Apply the ConfigMap:

```bash
kubectl apply -f config.yaml
```

### Step 2: Create Deployment and Service

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: address-formatter
  namespace: address-formatter
spec:
  replicas: 3
  selector:
    matchLabels:
      app: address-formatter
  template:
    metadata:
      labels:
        app: address-formatter
    spec:
      containers:
      - name: address-formatter
        image: address-formatter:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: address-formatter-config
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "500m"
            memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: address-formatter
  namespace: address-formatter
spec:
  selector:
    app: address-formatter
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

Apply the deployment:

```bash
kubectl apply -f deployment.yaml
```

### Step 3: Create Ingress (optional)

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: address-formatter
  namespace: address-formatter
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: address.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: address-formatter
            port:
              number: 80
```

Apply the ingress:

```bash
kubectl apply -f ingress.yaml
```

## Manual Deployment

### Step 1: Set up environment

```bash
# Clone repository
git clone --recurse-submodules https://github.com/yourusername/pyaddress.git
cd pyaddress

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure

```bash
# Create production environment file
python -m config.production

# Edit the configuration as needed
```

### Step 3: Run

```bash
# Run the API server
uvicorn address_formatter.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Post-Deployment Validation

After deploying, validate the installation:

```bash
# Check API health
curl http://localhost:8000/health

# Test formatting an address
curl -X POST http://localhost:8000/format \
  -H "Content-Type: application/json" \
  -d '{"components": {"road": "Main St", "house_number": "123", "city": "Anytown", "country_code": "US"}}'
```

Or use the automated deployment script which includes validation:

```bash
python scripts/deploy.py --validate
```

## Monitoring Setup

### Step 1: Configure Prometheus

The deployment script automatically creates Prometheus configuration:

```bash
python scripts/deploy.py --deploy-monitoring
```

Or manually create configuration:

```bash
python -m config.monitoring
```

### Step 2: Configure Grafana

1. Add Prometheus as a data source in Grafana
2. Import the dashboard template from `monitoring/dashboards/address_formatter.json`

## Troubleshooting

### Common Issues

1. **Template errors**: Ensure the OpenCageData submodule is properly initialized:
   ```bash
   git submodule update --init --recursive
   ```

2. **Permission issues with Docker volumes**:
   ```bash
   chmod -R 755 ./data
   ```

3. **Memory issues with performance tests**:
   Increase the container memory limit or decrease the test batch size

4. **API connection refused**:
   - Check if the service is running
   - Verify port mappings and firewall settings
   - Check the API logs: `docker-compose logs api`

### Logs

- Docker logs: `docker-compose logs -f api`
- Kubernetes logs: `kubectl logs -f -l app=address-formatter -n address-formatter`
- Application logs: Check `/var/log/address-formatter/` (default log location)

### Support

For additional help, contact the development team or open an issue on the repository. 