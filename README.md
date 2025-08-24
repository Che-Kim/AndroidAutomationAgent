# Android Automation Agent

## 🎯 Overview

An Android automation agent system that integrates with AndroidWorld and cloud Android emulators (Genymotion). The system demonstrates agent-based task execution, multi-episode evaluation, and production deployment patterns.

## 🚀 Quick Start (Runbook)

### Prerequisites
- Docker running
- Python 3.11+
- Genymotion Cloud API key

### Environment Variables
```bash
# Required
GENYMOTION_API_KEY=your-api-key-here
```

**Note**: The system will use default values for all other configuration options

### Steps

1. **Clone & Setup**
   ```bash
   git clone https://github.com/Che-Kim/QualGent-Challenge.git
   cd QualGent-Challenge
   ./setup.sh
   ```

2. **Get Genymotion API Key**
   - Sign up: [https://cloud.geny.io](https://cloud.geny.io)
   - Create API key in Account → API Keys
   - Update `.env` file: Replace `your-actual-api-key-here` with your API key

3. **Create Devices**
   ```bash
   ./infra/create_devices.sh
   ```

4. **Build & Run**
   ```bash
   docker build -t candidate/android-world .
   docker run --env-file .env candidate/android-world
   ```

5. **Evaluate**
   ```bash
   ./agents/evaluate.sh --episodes 50
   ```

6. **Check Results**
   ```bash
   cat results/report.md
   ```

## 📁 Project Structure

```
QualGentChallenge/
├── README.md                  # This file
├── setup.sh                   # Environment setup
├── run.sh                     # Main execution script
├── Dockerfile                 # Container
├── env.example                # Environment template
├── infra/                     # Genymotion provisioning
├── agents/                    # Agent implementation
├── android_world/             # AndroidWorld integration
├── .github/workflows/         # CI pipeline
├── k8s/                       # Autoscaling configs
├── load-testing/              # Load testing tools
└── results/                   # Sample output
```

## 🧪 Testing

### Run Smoke Test
```bash
./smoke_test.sh
```
Automatically detects environment and runs appropriate tests.

### Test Individual Components
```bash
python3 -c "from agents.agent import AndroidWorldAgent; print('✅ Agent works')"
```

## 📊 Sample Output

After running evaluation, check:
- `results/report.md` - Human-readable report
- `results/results.json` - Machine-readable data
- `results/metrics.json` - Performance metrics

## 🔧 Troubleshooting

### Common Issues
- **Docker not running**: Start Docker Desktop
- **API key not set**: Use `./setup.sh` or export `GENYMOTION_API_KEY`
- **Device connection failed**: Verify Genymotion API key and device status

### Local Testing (No Genymotion)
```bash
# Set in .env
TEST_ENVIRONMENT=true
GENYMOTION_API_KEY=mock-key-for-local-testing

# Run evaluation (simulated)
./agents/evaluate.sh --episodes 5
```

## 📚 For More Details

- **Architecture**: See individual Python files for implementation details
- **CI/CD**: Check `.github/workflows/ci.yml` for automated testing
- **Load Testing**: Explore `load-testing/` directory for performance tools
- **Autoscaling**: Review `k8s/` directory for deployment configurations
