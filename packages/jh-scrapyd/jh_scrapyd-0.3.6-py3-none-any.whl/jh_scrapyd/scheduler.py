from zope.interface import implementer

from jh_scrapyd.interfaces import ISpiderScheduler
from jh_scrapyd.utils import get_spider_queues


@implementer(ISpiderScheduler)
class SpiderScheduler:
    def __init__(self, config):
        self.config = config
        self.update_projects()

    def schedule(self, project, spider_name, priority=0.0, **spider_args):
        self.queues[project].add(spider_name, priority=priority, **spider_args)

    def list_projects(self):
        return list(self.queues)

    def update_projects(self):
        self.queues = get_spider_queues(self.config)
