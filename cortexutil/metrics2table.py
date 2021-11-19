import luigi
from structlog import get_logger
import cortexutil.fetcher as fetcher
from jinja2 import Template

log = get_logger()

def fix_name(host):
    return host.replace("http://", "").replace("https://", "").replace(":", "_").replace("/", "_")

class Metrics2Table(luigi.Task):
    
    host = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(f'results/{fix_name(self.host)}.html')

    def run(self):
        log.info(f"Fetching {self.host}")
        result = fetcher.get_metrics(self.host)
        summary = fetcher.to_summary(result)
        
        
        t = Template(open("templates/metrics_table.jinja2").read())
        with self.output().open("w") as outfile:
            outfile.write(t.render(metrics=summary))
            
if __name__ == "__main__":
    luigi.run()