import streamlit as st
from prometheus_api_client import PrometheusConnect
from analyze_logs import fetch_logs_from_loki
from remediate import restart_container, verify_stability
from datetime import datetime, timedelta

st.title("OpsBot Dashboard")

prom = PrometheusConnect(url="http://34.214.175.254:9090", disable_ssl=True)

def fetch_cpu_usage():
    query = '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    metric_data = prom.get_current_metric_value(query)
    return metric_data[0]['value'] if metric_data else 0

st.header("Live Metrics")
cpu_usage = fetch_cpu_usage()
st.metric("CPU Usage", f"{cpu_usage:.2f}%")

st.header("Recent Logs")
logs = fetch_logs_from_loki(datetime.now() - timedelta(minutes=5), datetime.now())
st.text_area("Logs", logs, height=200)

st.header("Manual Remediation")
if st.button("Restart Container"):
    if restart_container():
        if verify_stability():
            st.success("Remediation successful. System stable.")
        else:
            st.error("Remediation failed. System unstable.")
    else:
        st.error("Failed to restart container.")

if __name__ == "__main__":
    st.write("Run with: streamlit run frontend.py")
