import requests
from cortexutil.prometheus_metric import PrometheusMetric

from structlog import get_logger

log = get_logger()

def get_metrics(endpoint):
    headers = {
        'Content-Type': 'text/plain'
    }
    return requests.get(endpoint, headers=headers).text

def is_helper(line):
    return line.startswith('# HELP')

def is_type(line):
    return line.startswith("# TYPE")

def split_comment(line):
    split = line.split(" ")
    return (split[2], " ".join(split[3:]))

def to_summary(text):
    summaries = {}
    for line in text.split('\n'):
        if is_helper(line):
            (metric, help) = split_comment(line)
            time_series = summaries.get(metric, {})
            time_series["help"] = help
            summaries[metric] = time_series
        
        elif is_type(line):
            (metric, type) = split_comment(line)
            time_series = summaries.get(metric, {})
            time_series["type"] = type
            summaries[metric] = time_series
            
        
    return_list = []
    for metric in summaries.keys():
        return_list.append({"metric": metric, 
                            "help": summaries.get(metric).get("help"), 
                            "type": summaries.get(metric).get("type")
                            })
        
    return return_list


# def process_results(raw_results):
#     results = {}
#     for line in raw_results.split("\n"):
#         if "#" in line:
#             header = split_comment(line)
#             name = header.get("name")
#             kind = header.get("kind")
#             value = header.get("value")
#             if name not in results.keys():
#                 results[name] =  PrometheusMetric(name=name)
                
            
#             getattr(results[name], kind) = value
                
#     return results
            
