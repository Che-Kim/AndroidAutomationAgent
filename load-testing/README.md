# 🧪 AndroidWorld Load Testing & Autoscaling

This directory contains comprehensive load testing and autoscaling configurations for the AndroidWorld system.

## 📁 Contents

### **Autoscaling Configurations**
- `../k8s/autoscaling.yaml` - Kubernetes HPA with deployment and service
- `../k8s/cloud-run.yaml` - Cloud Run autoscaling configuration

### **Load Testing Tools**
- `k6-load-test.js` - k6-based load testing (JavaScript)
- `stress-test.py` - Python stress testing with threading
- `locust-load-test.py` - Locust-based load testing (Python)

## 🚀 Quick Start

### **1. Kubernetes Autoscaling**

```bash
# Create namespace
kubectl create namespace android-world

# Apply autoscaling configuration
kubectl apply -f ../k8s/autoscaling.yaml

# Check HPA status
kubectl get hpa -n android-world

# Monitor scaling
kubectl describe hpa android-world-hpa -n android-world
```

### **2. Cloud Run Autoscaling**

```bash
# Deploy to Cloud Run (replace PROJECT_ID)
gcloud run deploy android-world \
  --image gcr.io/PROJECT_ID/android-world:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --concurrency 80 \
  --max-instances 10 \
  --cpu 1 \
  --memory 512Mi
```

## 🧪 Load Testing

### **Option 1: k6 (Recommended for CI/CD)**

```bash
# Install k6
brew install k6  # macOS
# or download from https://k6.io/docs/getting-started/installation/

# Run basic load test (requires BASE_URL environment variable)
k6 run --env BASE_URL=http://your-service-url k6-load-test.js

# Run in CI environment
k6 run --env BASE_URL=http://your-service-url k6-load-test.js
```

**k6 Features:**
- ✅ JavaScript-based, easy to customize
- ✅ Built-in metrics and thresholds
- ✅ CI/CD friendly
- ✅ Cloud-native (k6 Cloud integration)

### **Option 2: Python Stress Test**

```bash
# Install dependencies
pip install aiohttp requests

# Run stress test
python stress-test.py --url http://your-service-url --requests 100 --concurrency 10

# Custom configuration
python stress-test.py \
  --url http://your-service-url \
  --requests 500 \
  --concurrency 25 \
  --output custom_stress_report.json
```

**Python Stress Test Features:**
- ✅ Threading-based concurrency
- ✅ Comprehensive reporting
- ✅ Resource usage estimates
- ✅ Customizable scenarios

### **Option 3: Locust**

```bash
# Install Locust
pip install locust

# Run Locust web interface
locust -f locust-load-test.py --host=http://your-service-url

# Run headless
locust -f locust-load-test.py \
  --host=http://your-service-url \
  --users 10 \
  --spawn-rate 2 \
  --run-time 5m \
  --headless
```

**Locust Features:**
- ✅ Web-based UI for real-time monitoring
- ✅ Python-based, easy to extend
- ✅ Distributed load testing
- ✅ Detailed statistics

## 📊 Test Scenarios

All load testing tools include these test scenarios:

1. **App Navigation** (High frequency)
   - Episodes: 1-5
   - Weight: 3x

2. **Text Input** (Medium frequency)
   - Episodes: 1-3
   - Weight: 2x

3. **Button Click** (Medium frequency)
   - Episodes: 1-4
   - Weight: 2x

4. **Swipe Gesture** (Low frequency)
   - Episodes: 1-2
   - Weight: 1x

5. **Health Checks** (Monitoring)
   - Weight: 1x

6. **Metrics Endpoint** (Monitoring)
   - Weight: 1x

## 🎯 Performance Targets

### **Response Time Thresholds**
- **95th percentile**: < 2 seconds
- **99th percentile**: < 5 seconds
- **Average**: < 1 second

### **Success Rate Targets**
- **Minimum**: 95%
- **Target**: 99%
- **Load test failure**: < 90%

### **Throughput Goals**
- **Minimum**: 10 requests/second
- **Target**: 50+ requests/second
- **Peak capacity**: 100+ requests/second

## 📈 Scaling Strategy

### **Kubernetes HPA**
- **Min replicas**: 1
- **Max replicas**: 10
- **CPU threshold**: 70%
- **Memory threshold**: 80%
- **Scale up**: Aggressive (100% increase)
- **Scale down**: Conservative (10% decrease)

### **Cloud Run**
- **Min instances**: 1
- **Max instances**: 10
- **CPU utilization**: 70%
- **Concurrency**: 80 requests per instance
- **Timeout**: 5 minutes

## 🔧 Configuration

### **Environment Variables**
```bash
# For load testing
BASE_URL=http://your-service-url
MAX_CONCURRENT_EPISODES=5

# For autoscaling
GENYMOTION_API_KEY=your_api_key
K8S_NAMESPACE=android-world
CLOUD_RUN_REGION=us-central1
```

### **Resource Limits**
```yaml
# Kubernetes
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

# Cloud Run
resources:
  limits:
    cpu: "1000m"
    memory: "512Mi"
```

## 📋 CI/CD Integration

### **GitHub Actions Example**
```yaml
- name: Load Test
  run: |
    k6 run --env BASE_URL=${{ steps.deploy.outputs.url }} k6-load-test.js
    
- name: Stress Test
  run: |
    python stress-test.py --url ${{ steps.deploy.outputs.url }} --requests 50 --concurrency 5
```

### **Cloud Build Example**
```yaml
- name: 'gcr.io/cloud-builders/k6'
  args: ['run', '--env', 'BASE_URL=$_SERVICE_URL', 'k6-load-test.js']
```

## 📊 Monitoring & Alerts

### **Key Metrics to Monitor**
1. **Response Time**: p95, p99, average
2. **Success Rate**: Overall and per endpoint
3. **Throughput**: Requests per second
4. **Resource Usage**: CPU, memory, network
5. **Error Rates**: HTTP errors, timeouts, failures

### **Alerting Thresholds**
- Response time p95 > 2s
- Success rate < 95%
- CPU usage > 80%
- Memory usage > 80%
- Error rate > 5%

## 🚨 Troubleshooting

### **Common Issues**

1. **High Response Times**
   - Check resource limits
   - Verify database connections
   - Monitor external dependencies

2. **High Error Rates**
   - Check application logs
   - Verify endpoint availability
   - Check authentication/authorization

3. **Scaling Issues**
   - Verify HPA configuration
   - Check resource quotas
   - Monitor node capacity

### **Debug Commands**
```bash
# Check HPA status
kubectl describe hpa -n android-world

# Check pod resources
kubectl top pods -n android-world

# Check service endpoints
kubectl get endpoints -n android-world

# Check Cloud Run scaling
gcloud run services describe android-world --region=us-central1
```

## 📚 Additional Resources

- [k6 Documentation](https://k6.io/docs/)
- [Locust Documentation](https://docs.locust.io/)
- [Kubernetes HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Cloud Run Autoscaling](https://cloud.google.com/run/docs/configuring/autoscaling)
- [Load Testing Best Practices](https://k6.io/docs/testing-guides/)

## 🎯 Next Steps

1. **Baseline Testing**: Run load tests against current system
2. **Performance Tuning**: Optimize based on test results
3. **Capacity Planning**: Determine production scaling needs
4. **Monitoring Setup**: Implement comprehensive observability
5. **Automated Testing**: Integrate load tests into CI/CD pipeline
