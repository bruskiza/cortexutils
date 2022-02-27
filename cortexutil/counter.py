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

def process_instances(prometheus_record):
    instances = {}
    for timeseries in prometheus_record.get('metrics'):
        for record in  prometheus_record.get('metrics').get(timeseries):
            instance = record.get('metric').get('instance')
            job = record.get('metric').get('job')
            if instance not in instances.keys():
                instances[instance] = {"jobs": {}}
            if job not in instances.get(instance).get('jobs'):
                instances[instance]["jobs"][job] = []
            instances[instance]["jobs"][job].append(timeseries)
            
    return instances

def process_jobs(prometheus_record):
    jobs = {}
    for timeseries in prometheus_record.get('metrics'):
        for record in  prometheus_record.get('metrics').get(timeseries):
            instance = record.get('metric').get('instance')
            job = record.get('metric').get('job')
            if job not in jobs.keys():
                jobs[job] = {"instances": {}}
            if instance not in jobs.get(job).get('instances'):
                jobs[job]["instances"][instance].append(timeseries)
            
    return jobs
