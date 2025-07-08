from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
from monitor_cpu import check_cpu_spike
from analyze_logs import fetch_logs_from_loki, analyze_logs
from remediate import restart_container, verify_stability
from notify import create_notification, send_slack_notification, send_email_notification
from datetime import datetime, timedelta
import time
import os

# Load API key from environment
llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))

# Define tools (exclude Notify for now)
tools = [
    Tool(
        name="MonitorCPU",
        func=lambda x: check_cpu_spike(threshold=80.0, duration_minutes=2)[1],
        description="Check for CPU spikes exceeding 80% for 2 minutes."
    ),
    Tool(
        name="AnalyzeLogs",
        func=lambda x: analyze_logs(fetch_logs_from_loki(datetime.now() - timedelta(minutes=5), datetime.now())),
        description="Fetch and analyze logs to identify root cause of CPU spike."
    ),
    Tool(
        name="Remediate",
        func=lambda x: restart_container() and verify_stability(),
        description="Restart container and verify system stability."
    )
]

agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

def main():
    while True:
        spike_detected, cpu_usage = check_cpu_spike()
        if spike_detected:
            print(f"CPU spike detected at {cpu_usage}%. Taking action...")

            # Run the AI agent
            root_cause = agent.run(f"CPU spike detected at {cpu_usage}%. Analyze logs and remediate.")

            # Notify the team
            message = create_notification(
                cpu_usage=cpu_usage,
                root_cause=root_cause,
                action_taken="Restarted container",
                status="System stable"
            )
            send_slack_notification(message)
            # Optionally:
            # send_email_notification(message)

            print("Notification sent.")
        else:
            print(f"CPU usage normal: {cpu_usage}%")

        time.sleep(60)

if __name__ == "__main__":
    main()
