from cortexutil.counter import *

test_timeseries = [
        {
            "metric": {
                "job": "job1",
                "instance": "instance1",
            }
        },
        {
            "metric": {
                "job": "job2",
                "instance": "instance2",
            }
        }
    ]

def test_get_jobs():
    assert get_jobs(test_timeseries) == ["job1", "job2"]

def test_get_instances():
    assert get_instances(test_timeseries) == ["instance1", "instance2"]
    