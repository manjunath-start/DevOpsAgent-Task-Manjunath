# OpsBot: AI-Powered DevOps Agent

## Overview
OpsBot is an intelligent DevOps agent designed to maintain system uptime (99.99%) by automating infrastructure monitoring, anomaly detection, root cause analysis, remediation, and notifications. Built for AWS EC2 Free Tier, it uses Prometheus, Loki, Docker, and LangChain to handle CPU, memory, disk, and network spikes, with a Streamlit frontend for visualization and manual overrides.

### Features
- **Monitoring & Anomaly Detection**: Tracks CPU, memory, disk, and network usage using Prometheus Node Exporter, detecting spikes based on configurable thresholds.
- **Root Cause Analysis**: Retrieves logs via Loki and analyzes them using an LLM (OpenAI or Ollama) to identify issues like memory leaks or infinite loops.
- **Auto Remediation**: Restarts failing containers/services and verifies system stability post-action.
- **Notifications**: Sends incident reports via Slack and email with spike details, root cause, actions taken, and system status.
- **Frontend Interface**: Streamlit dashboard displays live metrics, logs, and supports manual remediation.
- **Extensibility**: Supports additional metrics (memory, disk, network) in the same workflow.

## Architecture
- **Infrastructure**: AWS EC2 (t2.micro, Ubuntu 22.04), Docker, Prometheus, Loki, Promtail.
- **Monitoring**: Prometheus Node Exporter for metrics, queried via `prometheus-api-client`.
- **Logging**: Loki and Promtail for log aggregation.
- **Agent**: LangChain orchestrates monitoring, analysis, remediation, and notification tools.
- **Frontend**: Streamlit for real-time metrics and manual controls.
- **LLM**: OpenAI GPT-3.5 (or Ollama for local inference) for log analysis.
- **Notifications**: Slack and SMTP-based email alerts.

## Prerequisites
- AWS Free Tier account
- SSH key pair for EC2 access
- Slack bot token for notifications
- Email SMTP credentials
- OpenAI API key (or Ollama setup for local LLM)
- Basic knowledge of Docker, Python, and AWS

## Setup Instructions

### 1. Launch AWS EC2 Instance
1. Create a t2.micro instance with Ubuntu 22.04 LTS in AWS Free Tier.
2. Configure security group to allow:
   - SSH (port 22)
   - HTTP (port 80)
   - Prometheus (port 9090)
   - Node Exporter (port 9100)
   - Loki (port 3100)
   - Streamlit (port 8501)
3. Note the public IP and download the `.pem` key.

### 2. Install Dependencies
1. SSH into the EC2 instance:
   ```bash
   ssh -i <your-key.pem> ubuntu@<ec2-public-ip>
   ```
2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd opsbot
   ```
3. Run the setup script to install Docker, Prometheus, Loki, Promtail, and Python dependencies:
   ```bash
   chmod +x setup_infrastructure.sh
   ./setup_infrastructure.sh
   ```

### 3. Configure Credentials
1. Update `analyze_logs.py`, `notify.py`, and `opsbot_agent.py` with:
   - OpenAI API key (or Ollama endpoint)
   - Slack bot token
   - Email SMTP server, username, and password
2. Store credentials securely (e.g., environment variables or AWS Secrets Manager).

### 4. Start Test Container
Run a CPU-intensive container for testing:
```bash
chmod +x test_container.sh
./test_container.sh
```

## Usage

### Run the Agent
Start the OpsBot agent to monitor, analyze, remediate, and notify:
```bash
python3 opsbot_agent.py
```
- The agent checks for spikes every minute, triggers analysis and remediation on detection, and sends notifications.

### Run the Frontend
Launch the Streamlit dashboard:
```bash
streamlit run frontend.py &
```
- Access at `http://<ec2-public-ip>:8501` to view metrics, logs, and perform manual remediation.

### Monitor Services
- Prometheus: `http://<ec2-public-ip>:9090`
- Node Exporter: `http://<ec2-public-ip>:9100/metrics`
- Loki: `http://<ec2-public-ip>:3100`

## Testing

### Test Plan
1. **Verify Setup**:
   - Check services: `sudo systemctl status <service>` (e.g., prometheus, loki, docker).
2. **Simulate Spikes**:
   - CPU: `docker run -d --name stress_test polinux/stress stress --cpu 2 --timeout 300s`
   - Memory: `docker run -d --name stress_test polinux/stress stress --vm 2 --vm-bytes 512M --timeout 300s`
   - Disk: `docker run -d --name stress_test -v /tmp/stress:/stress polinux/stress stress --hdd 2 --hdd-bytes 1G --timeout 300s`
   - Network: `docker run -d --name stress_test appropriate/curl sh -c "while true; do curl -s -o /dev/null http://speedtest.ftp.otenet.gr/files/test1Mb.db; done"`
3. **Validate Detection**:
   - Run `python3 monitor_cpu.py` or `monitor_extended.py` and check for spike detection.
4. **Test Root Cause Analysis**:
   - Add test logs: `echo "ERROR: Infinite loop detected" >> /var/log/test.log`
   - Run `python3 analyze_logs.py` to verify LLM analysis.
5. **Test Remediation**:
   - Run `python3 remediate.py` to confirm container restart and stability check.
6. **Test Notifications**:
   - Run `python3 notify.py` to verify Slack/email alerts.
7. **Test Frontend**:
   - Access Streamlit dashboard and test manual remediation button.
8. **Edge Cases**:
   - Stop Promtail/Docker to simulate failures and verify human intervention requests.

### Cleanup
Stop and remove test containers:
```bash
docker stop stress_test
docker rm stress_test
```

## Project Structure
```
opsbot/
├── setup_infrastructure.sh    # Installs dependencies
├── test_container.sh          # Runs test container
├── monitor_cpu.py             # CPU spike detection
├── monitor_extended.py        # Extended metrics detection
├── analyze_logs.py            # Log retrieval and LLM analysis
├── remediate.py               # Container restart and verification
├── notify.py                  # Slack/email notifications
├── opsbot_agent.py            # LangChain agent orchestration
├── frontend.py                # Streamlit dashboard
└── README.md                  # Project documentation
```

## Known Limitations
- AWS Free Tier limits (750 hours/month for t2.micro).
- OpenAI API costs (use Ollama for local LLM to reduce expenses).
- Basic Loki setup (filesystem storage, not scalable).
- Single-container remediation (extend for multi-container or Kubernetes).
- Network spike simulation requires external connectivity.

## Future Enhancements
- Kubernetes integration for multi-container orchestration.
- Auto-scaling based on spike severity.
- Grafana integration for advanced visualization.
- Support for additional remediation actions (e.g., scale resources, kill processes).
- Enhanced LLM prompts for better root cause accuracy.

## Contributing
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m "Add feature"`
4. Push to branch: `git push origin feature-name`
5. Open a pull request with detailed description.

## License
MIT License. See [LICENSE](LICENSE) for details.
