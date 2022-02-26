from structlog import get_logger


log = get_logger()

# data = json.load(open("localhost_9090_every_metric.json"))

INSTANCE = "instance"
JOB = "job"

def get_values(timeseries, value):
    values = []
    for record in timeseries:
        log.info(record)
        metric = record.get('metric')
        
        instance = metric.get(value)
        if instance not in values:
            values.append(instance)
    return values

def get_jobs(timeseries):
    return get_values(timeseries, JOB)

def get_instances(timeseries):
    return get_values(timeseries, INSTANCE)

