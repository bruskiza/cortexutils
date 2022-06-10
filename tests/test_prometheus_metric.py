from cortexutils.prometheus_metric import PrometheusMetric

def test_prometheus_metric():
    assert PrometheusMetric() is not None