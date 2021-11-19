class PrometheusMetric():
    def __init__(self, name='', kind='', summary='',labels=[]):
        self.name = name,
        self.kind = kind,
        self.summary = summary,
        self.labels = labels
        