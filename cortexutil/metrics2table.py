#!/usr/bin/env python

import luigi
from structlog import get_logger
import cortexutil.fetcher as fetcher
from jinja2 import Template
import json
from datetime import datetime 

log = get_logger()

def fix_name(host):
    return host.replace("http://", "").replace("https://", "").replace(":", "_").replace("/", "_")

class GatherMetrics(luigi.WrapperTask):    
    
    host = luigi.Parameter()
    host_type = luigi.Parameter()
    
    def requires(self):
        yield Metrics2Raw(self.host, self.host_type)
        yield Metrics2Json(self.host, self.host_type)
        yield Metrics2Table(self.host, self.host_type)
        yield GetConfigDiff(self.host, self.host_type)
        yield Metrics2NonZeros(self.host, self.host_type)
        yield ProcessNonZeros(self.host, self.host_type)

class GetConfigDiff(luigi.Task):
    
    host = luigi.Parameter()
    host_type = luigi.Parameter()
    
    def output(self):
        return luigi.LocalTarget(f"results/{fix_name(self.host)}_{self.host_type}.config.diff")
    
    def run(self):
        endpoint = self.host.replace("/metrics", "/config?mode=diff")
        log.info(F"Config diff from here: {endpoint}")
        result = fetcher.get_config_diff(endpoint)
        with self.output().open("w") as output:
            output.write(result)
        
class Metrics2NonZeros(luigi.Task):
    """ Separates all metrics out from nulls and non-zeros"""    
    host = luigi.Parameter()
    host_type = luigi.Parameter()
    
    def requires(self):
        return Metrics2Raw(self.host, self.host_type)
    
    def output(self):
        return luigi.LocalTarget(f"results/{fix_name(self.host)}_{self.host_type}.raw.non-zero")
    
    def run(self):
        log.info(f"Parsing out all non-zero values ...")
        log.info(f"last input: {self.input()}")
        non_zero_metrics = []
        for line in self.input().open():
            if "#" in line:
                continue
            (metric, value) = fetcher.get_value(line)
            if metric is not None and value is not None:
                if metric not in non_zero_metrics:
                    non_zero_metrics.append(metric)
        log.info(f"{len(non_zero_metrics)} found. Writing.")
        with self.output().open("w") as output:
            output.write("\n".join(non_zero_metrics))
        

def string_to_dict(string, seperator="_"):
    data = string.split(seperator)
    

class Metrics2Geneology(luigi.Task):
    """ Gets all metrics and separates out geneology family """    
    host = luigi.Parameter()
    host_type = luigi.Parameter()
    
    def requires(self):
        return Metrics2Raw(self.host, self.host_type)
    
    def output(self):
        return luigi.LocalTarget(f"results/{fix_name(self.host)}_{self.host_type}.geneology.json")
    
    def run(self):
        log.info(f"Parsing out all non-zero values ...")
        log.info(f"last input: {self.input()}")
        non_zero_metrics = []
        for line in self.input().open():
            if "#" in line:
                continue
            (metric, value) = fetcher.get_value(line)
            if metric is not None and value is not None:
                if metric not in non_zero_metrics:
                    non_zero_metrics.append(metric)
        log.info(f"{len(non_zero_metrics)} found. Writing.")
        with self.output().open("w") as output:
            output.write("\n".join(non_zero_metrics))
        
        
class Metrics2Raw(luigi.Task):
    """ Downloads ever metric """
    host = luigi.Parameter()
    host_type = luigi.Parameter()
    
    
    def output(self):
        return luigi.LocalTarget(f"results/{fix_name(self.host)}_{self.host_type}.raw")
    
    def run(self):
        result = fetcher.get_metrics(self.host)
        with self.output().open("w") as output:
            output.write(result)


class ProcessNonZeros(luigi.Task):
    
    host = luigi.Parameter()
    host_type = luigi.Parameter()
    
    
    def requires(self):
        return Metrics2NonZeros(self.host, self.host_type)
    
    def output(self):
        return luigi.LocalTarget(f"results/{fix_name(self.host)}_{self.host_type}.raw.non-zero.processed")
    
    def run(self):
        log.info(self.input())
        metrics = self.input().open().read().split("\n")
        results = {}
        
        for metric in metrics:
            current = metric.split("_")
            
        with self.output().open("w") as out:
            out.write("\n".join(set(metrics)))
        
    
    
class Metrics2Json(luigi.Task):
    
    host = luigi.Parameter()
    host_type = luigi.Parameter()
    
    def requires(self):
        Metrics2Raw(self.host, self.host_type)
    
    
    def output(self):
        return luigi.LocalTarget(f"results/{fix_name(self.host)}_{self.host_type}.json")

    def run(self):
        summary = fetcher.to_summary(open(f"results/{fix_name(self.host)}_{self.host_type}.raw").read())
        
        import json
        with self.output().open("w") as outfile:
            outfile.write(json.dumps({"host": self.host, "metrics": summary, "host_type": self.host_type}, indent=4))
            
class Metrics2Table(luigi.Task):
    
    host = luigi.Parameter()
    host_type = luigi.Parameter() 
    
    
    def requires(self):
        return Metrics2Json(self.host, self.host_type)
    

    def output(self):
        return luigi.LocalTarget(f'results/{fix_name(self.host)}_{self.host_type}.html')

    def run(self):
        log.info(f"Parsing the raw file {self.host}")
        
        result = json.loads(open(f"results/{fix_name(self.host)}_{self.host_type}.json").read())
        
        t = Template(open("templates/metrics_table.jinja2").read())
        with self.output().open("w") as outfile:
            outfile.write(t.render(metrics=result.get('metrics'), 
                                   host=self.host, 
                                   type=self.host_type,
                                   date=datetime.now().isoformat()))
            
            
if __name__ == "__main__":
    luigi.run()