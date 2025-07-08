from prometheus_api_client import PrometheusConnect
from datetime import datetime, timedelta

prom = PrometheusConnect(
    url="http://34.214.175.254:9090",  # Your Prometheus server IP
    disable_ssl=True
)

def check_cpu_spike(threshold=80.0, duration_minutes=2):
    query = '100 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100'
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=duration_minutes)

    result = prom.custom_query_range(
        query=query,
        start_time=start_time,
        end_time=end_time,
        step='30s'
    )

    if not result or 'values' not in result[0]:
        return False, None

    # Extract values and compute average
    values = [float(val[1]) for val in result[0]['values']]
    avg_cpu = sum(values) / len(values)

    if avg_cpu > threshold:
        return True, avg_cpu
    return False, avg_cpu
