from twisted.internet.defer import DeferredQueue, inlineCallbacks, maybeDeferred
from zope.interface import implementer

from jh_scrapyd.interfaces import IPoller
from jh_scrapyd.utils import get_spider_queues
from jh_scrapyd import get_config


@implementer(IPoller)
class QueuePoller:
    def __init__(self, config):
        self.config = config
        self.update_projects()
        self.dq = DeferredQueue()

    @inlineCallbacks
    def poll(self):
        for project, queue in self.queues.items():
            while (yield maybeDeferred(queue.count)):
                # If the "waiting" backlog is empty (that is, if the maximum number of Scrapy processes are running):
                if not self.dq.waiting:
                    return
                # The message can be None if, for example, two Scrapyd instances share a spider queue database.
                message = yield maybeDeferred(queue.pop)
                if message is not None:
                    message = message.copy()  # 确认非空后再复制

                    # TODO 不同的项目有不同的队列，但是现在是直接使用的redis，所以不需要再次设置项目名称
                    # message["_project"] = project

                    message["_spider"] = message.pop("name")
                    # Pop a dummy item from the "waiting" backlog. and fire the message's callbacks.
                    self.dq.put(message)

    def next(self):
        """
        Add a dummy item to the "waiting" backlog (based on Twisted's implementation of DeferredQueue).
        """
        return self.dq.get()

    def update_projects(self):
        self.queues = get_spider_queues(self.config)

    def get_queues(self) -> dict:
        """Obtain the actual queue"""
        queues = {}
        i = 0
        for project, queue in self.queues.items():
            if get_config(option='is_unified_queue', section='cluster') and i > 0:
                # When unifying the queue, only one calculation is needed
                break
            queues[project] = queue
            i += 1
        return queues

    def get_queues_count(self) -> int:
        """Obtain the actual number of queue tasks"""
        total = 0
        for project, queue in self.get_queues().items():
            total += queue.count()
        return total
