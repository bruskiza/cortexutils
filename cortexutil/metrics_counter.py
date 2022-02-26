#!/usr/bin/env python

import luigi
from structlog import get_logger
import cortexutil.fetcher as fetcher
import cortexutil.counter as counter
from jinja2 import Template
import json
from datetime import datetime 

from luigi.contrib import sqla

from sqlalchemy import String

from structlog import get_logger

log = get_logger()

from prometheus_api_client import PrometheusConnect

log = get_logger()

def fix_name(host):
    """Make a file-friendly name of the host. """
    return host.replace("http://", "").replace("https://", "").replace(":", "_").replace("/", "_")


class GetAllMetrics(luigi.Task):
    """ Connects to a prom and gets all the metrics ands saves it to a file. """
    host = luigi.Parameter()
        
    def output(self):
        return luigi.LocalTarget(f"results/{fix_name(self.host)}_all_metrics.txt")
    
    def run(self):
        prom = PrometheusConnect(url=self.host)
        with self.output().open("w") as out:
            out.write("\n".join(prom.all_metrics()))
        

def get_metric(metric, prom):
    """Gets the metric from a prom provided. """
    data = prom.custom_query(query=metric)
    return data


class Metrics2DB(sqla.CopyToTable):
    """ Attempting to test out the CopyToTable task. 
    
    This will: 
    
    - iterate through every metric
    - Find the instances
    - Write it to a metrics_senders table
    
    """
    
    
    host = luigi.Parameter()
    
    connection_string = "sqlite:///metrics.db"
    table = "metrics_senders"
    
    columns = [
        (["id", String(50)], {"primary_key": True}), 
        (["source", String(255)], {}),
        (["sender", String(255)], {}), 
        (["job", String(255)], {}), 
        (["metric", String(255)], {})
    ]
    
    
    def requires(self):
        return FetchEveryMetric(self.host)    
    

    def prepare(self):
        file_name = f"{fix_name(self.requires().host)}"
        # log.info(f"Setting new table name: {file_name}")
        # self.table = file_name
        

        log.info(self.requires().output().open())
    
        data = json.load(self.requires().output().open())
        # for metric in data["metrics"]:
            # instances = data["metrics"].get(metric)
            # log.info(f"{metric}: {len(instances)}")
        #     # for instance in data["metrics"].get(metric):
        results = []
        count = 0
        for metric in data.get("metrics"):
            # log.info(metric)
            
            current_metrics = data.get("metrics").get(metric)
            for instance in current_metrics:
                # log.info(instance)
                cm = instance.get("metric")
                current_instance = cm.get("instance")
                current_job = cm.get("job")
                results.append((count, self.requires().host, current_instance, current_job, metric))
                count+=1
        
        # log.info(results)
        return results
    
    def rows(self):
        for row in self.prepare():
            yield row
                
    
    
    
class SummarizeEveryMetric(luigi.Task):
    """Writes out a summary of every metric"""
    host = luigi.Parameter()
    
    def requires(self):
        return FetchEveryMetric(self.host)    
    
    def output(self):
        return luigi.LocalTarget(f"results/{fix_name(self.host)}_every_metric_summary.json")
    
    def run(self):
        data = json.load(self.input().open())
        summary = {
            "null": len(data.get("null")),
            "summary": len(data.get("metrics"))
        }
        with self.output().open("w") as out:
            out.write(json.dumps(summary, indent=4))
            
class instances2timeseries(luigi.Task):
    """Writes out a summary of every metric"""
    host = luigi.Parameter()
    
    def requires(self):
        return FetchEveryMetric(self.host)    
    
    def output(self):
        return luigi.LocalTarget(f"results/{fix_name(self.host)}_instances_with_timeseries.json")
    
    def run(self):
        data = json.load(self.input().open())
        metrics = data.get('metrics')
        hosts = {}
        for metric in metrics:
            for instance in counter.get_instances(metrics.get(metric)):
                if instance not in hosts:
                    hosts[instance] = []
                if metric not in hosts[instance]:
                    hosts[instance].append(metric)
                    
        with self.output().open("w") as out:
            out.write(json.dumps(hosts, indent=4))
        

class FetchEveryMetric(luigi.Task):
    """ Fetches every metric for a given host """
    host = luigi.Parameter()
            
    def requires(self):
        return GetAllMetrics(self.host)
    
    def output(self):
        return luigi.LocalTarget(f"results/{fix_name(self.host)}_every_metric.json")
    
    def run(self):
        prom = PrometheusConnect(url=self.host)
        null_metrics = []
        metrics = {}
        for line in self.input().open().read().split("\n"):
            data = get_metric(line, prom)
            if data is None or data == []:
                null_metrics.append(line)
            else:
                metrics[line] = data
                
        with self.output().open("w") as out:
            out.write(json.dumps({"metrics": metrics, "null": null_metrics, }, indent=4))
                
            
            
if __name__ == "__main__":
    luigi.run()