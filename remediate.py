#!/bin/bash
# Run a CPU-intensive container for testing
docker run -d --name stress_test \
  polinux/stress \
  stress --cpu 2 --timeout 600s
ubuntu@ip-172-31-32-208:~$ ^C
ubuntu@ip-172-31-32-208:~$ cat remediate.py
import subprocess
from monitor_cpu import check_cpu_spike
import time

def restart_container(container_name="stress_test"):
    try:
        subprocess.run(["docker", "restart", container_name], check=True)
        print(f"Restarted container: {container_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart container: {e}")
        return False

def verify_stability(threshold=80.0, check_duration=2):
    time.sleep(30)  # Wait for container to stabilize
    spike_detected, cpu_usage = check_cpu_spike(threshold, check_duration)
    if not spike_detected:
        print(f"System stable after remediation: CPU at {cpu_usage}%")
        return True
    print(f"System still unstable: CPU at {cpu_usage}%")
    return False

def main():
    if restart_container():
        if verify_stability():
            print("Remediation successful.")
        else:
            print("Remediation failed. Requesting human intervention.")
    else:
        print("Remediation failed. Requesting human intervention.")

if __name__ == "__main__":
    main()
