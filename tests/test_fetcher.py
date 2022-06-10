from cortexutils.fetcher import *
from cortexutils.prometheus_metric import PrometheusMetric

dummy_statistic = """
# HELP go_gc_duration_seconds A summary of the pause duration of garbage collection cycles.
# TYPE go_gc_duration_seconds summary
go_gc_duration_seconds{quantile="0"} 5.0379e-05"""

def test_fetcher(requests_mock):
    requests_mock.get(
        "http://localhost:9090/metrics",
        text=dummy_statistic,
    )
    results = get_metrics("http://localhost:9090/metrics")
    assert results is not None
    print(results)
    assert len(results) == 178


def test_is_help():
    assert is_helper("# HELP something") is True
    assert is_helper("# NOTHELP ") is False
    assert is_helper("counter 1") is False


def test_is_type():
    assert is_type("# HELP something") is False
    assert is_type("# TYPE ") is True
    assert is_type("counter 1") is False


def test_split_comment():
    assert split_comment("# TYPE go_gc_duration_seconds summary") == ("go_gc_duration_seconds", "summary")


def test_summary():
    text = """# HELP cortex_blocks_meta_sync_consistency_delay_seconds Configured consistency delay in seconds.
# TYPE cortex_blocks_meta_sync_consistency_delay_seconds gauge
cortex_blocks_meta_sync_consistency_delay_seconds{component="querier"} 0"""

    assert to_summary(text) == [{'metric': 'cortex_blocks_meta_sync_consistency_delay_seconds', 'help': 'Configured consistency delay in seconds.', 'type': 'gauge'}]
# def test_process_results():
#     assert process_results(dummy_statistic) is not None