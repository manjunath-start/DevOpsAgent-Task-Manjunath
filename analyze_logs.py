import requests
import os
from datetime import datetime, timedelta
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# Fetch logs from Loki for the given time range
def fetch_logs_from_loki(start_time, end_time):
    loki_url = "http://34.214.175.254:3100/loki/api/v1/query_range"
    query = '{job="varlogs"}'
    params = {
        "query": query,
        "start": int(start_time.timestamp() * 1e9),  # nanoseconds
        "end": int(end_time.timestamp() * 1e9),
        "limit": 1000
    }

    response = requests.get(loki_url, params=params)
    if response.status_code == 200:
        logs = response.json().get('data', {}).get('result', [])
        return "\n".join([entry[1] for stream in logs for entry in stream['values']])
    else:
        print("Error fetching logs:", response.status_code, response.text)
    return ""

# Analyze logs using OpenAI via LangChain
def analyze_logs(logs):
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        openai_api_key=os.environ["OPENAI_API_KEY"]
    )

    prompt = PromptTemplate(
        input_variables=["logs"],
        template="""
Analyze the following logs to identify the possible cause of high CPU usage.
Provide a clear, concise reason if identifiable, or state if the cause is unclear.

Logs:
{logs}
        """
    )

    response = llm.predict(prompt.format(logs=logs))
    return response

# Main script logic
def main():
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=5)

    logs = fetch_logs_from_loki(start_time, end_time)

    if logs:
        cause = analyze_logs(logs)
        print(f"\n🔍 Root Cause Analysis:\n{cause}")
    else:
        print("⚠️ No logs retrieved for analysis.")

if __name__ == "__main__":
    main()
