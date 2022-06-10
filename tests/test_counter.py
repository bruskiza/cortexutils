from cortexutils.counter import *
import json

test_prometheus_record = {
    "metrics": {
        "timeseries1": [
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
}
}

def test_get_jobs():
    assert get_jobs(test_prometheus_record.get('metrics').get('timeseries1')) == ["job1", "job2"]

def test_get_instances():
    assert get_instances(test_prometheus_record.get('metrics').get('timeseries1')) == ["instance1", "instance2"]
    
    
def test_process_instances():
    assert len(process_instances(test_prometheus_record).keys()) == 2
    assert len(process_jobs(test_prometheus_record).keys()) == 2
