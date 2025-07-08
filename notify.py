from slack_sdk import WebClient
import smtplib
from email.mime.text import MIMEText

def send_slack_notification(message, slack_token="", channel="#devops-alerts"):
    client = WebClient(token=slack_token)
    try:
        client.chat_postMessage(channel=channel, text=message)
        print("Slack notification sent.")
    except Exception as e:
        print(f"Failed to send Slack notification: {e}")

def send_email_notification(message, sender="cloudopscommunity@gmail.com", recipient="manjunath.dc1995@gmail.com", smtp_server="smtp.gmail.com", smtp_port=587, smtp_user="cloudopscommunity@gmail.com", smtp_password="cloudopscommunity@2025"):
    msg = MIMEText(message)
    msg['Subject'] = "OpsBot Incident Report"
    msg['From'] = sender
    msg['To'] = recipient
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender, recipient, msg.as_string())
        print("Email notification sent.")
    except Exception as e:
        print(f"Failed to send email notification: {e}")

def create_notification(cpu_usage, root_cause, action_taken, status):
    return f"""
    OpsBot Incident Report
    ---------------------
    CPU Spike Detected: {cpu_usage}%
    Root Cause: {root_cause}
    Action Taken: {action_taken}
    System Status: {status}
    """

def main():
    notification = create_notification(
        cpu_usage=85.5,
        root_cause="Identified infinite loop in application code.",
        action_taken="Restarted container 'stress_test'.",
        status="System stable."
    )
    send_slack_notification(notification)
    send_email_notification(notification)

if __name__ == "__main__":
    main()
