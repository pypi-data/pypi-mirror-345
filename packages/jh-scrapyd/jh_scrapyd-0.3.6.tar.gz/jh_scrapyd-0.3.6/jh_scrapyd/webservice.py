from __future__ import annotations

import functools
import json
import os
import sys
import traceback
import uuid
import zipfile
from collections import defaultdict
from io import BytesIO
from subprocess import PIPE, Popen
from typing import ClassVar
from datetime import datetime
import pytz

from twisted.logger import Logger
from twisted.web import error, http, resource

from jh_scrapyd.exceptions import EggNotFoundError, ProjectNotFoundError, RunnerError
from jh_scrapyd.jh.utils.encryption import ApiSign
from jh_scrapyd import get_config
from twisted.internet import threads

log = Logger()


def param(
    decoded: str,
    *,
    dest: str | None = None,
    required: bool = True,
    default=None,
    multiple: bool = False,
    type=str,  # noqa: A002 like Click
):
    encoded = decoded.encode()
    if dest is None:
        dest = decoded

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, txrequest, *args, **kwargs):
            default_value = default() if callable(default) else default

            if encoded not in txrequest.args:
                if required:
                    raise error.Error(code=http.OK, message=b"'%b' parameter is required" % encoded)

                value = default_value
            else:
                values = (value.decode() if type is str else type(value) for value in txrequest.args.pop(encoded))
                try:
                    value = list(values) if multiple else next(values)
                except (UnicodeDecodeError, ValueError) as e:
                    raise error.Error(code=http.OK, message=b"%b is invalid: %b" % (encoded, str(e).encode())) from e

            kwargs[dest] = value

            return func(self, txrequest, *args, **kwargs)

        return wrapper

    return decorator


class SpiderList:
    cache: ClassVar = defaultdict(dict)

    def get(self, project, version, *, runner):
        """Return the ``scrapy list`` output for the project and version, using a cache if possible."""
        try:
            return self.cache[project][version]
        except KeyError:
            return self.set(project, version, runner=runner)

    def set(self, project, version, *, runner):
        """Calculate, cache and return the ``scrapy list`` output for the project and version, bypassing the cache."""

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "UTF-8"
        env["SCRAPY_PROJECT"] = project
        # If the version is not provided, then the runner uses the default version, determined by egg storage.
        if version:
            env["SCRAPYD_EGG_VERSION"] = version

        args = [sys.executable, "-m", runner, "list", "-s", "LOG_STDOUT=0"]
        process = Popen(args, stdout=PIPE, stderr=PIPE, env=env)
        stdout, stderr = process.communicate()
        if process.returncode:
            raise RunnerError((stderr or stdout or b"").decode())

        spiders = stdout.decode().splitlines()

        # Note: If the cache is empty, that doesn't mean that this is the project's only version; it simply means that
        # this is the first version called in this Scrapyd process.

        # Evict the return value of version=None calls, since we can't determine whether this version is the default
        # version (in which case we would overwrite it) or not (in which case we would keep it).
        self.cache[project].pop(None, None)
        self.cache[project][version] = spiders
        return spiders

    def delete(self, project, version=None):
        if version is None:
            self.cache.pop(project, None)
        else:
            # Evict the return value of version=None calls, since we can't determine whether this version is the
            # default version (in which case we would pop it) or not (in which case we would keep it).
            self.cache[project].pop(None, None)
            self.cache[project].pop(version, None)


spider_list = SpiderList()


# WebserviceResource
class WsResource(resource.Resource):
    """
    .. versionchanged:: 1.1.0
       Add ``node_name`` to the response in all subclasses.
    """

    json_encoder = json.JSONEncoder()

    def __init__(self, root):
        super().__init__()
        self.root = root

    def render(self, txrequest):
        try:
            data = super().render(txrequest)
        except Exception as e:  # noqa: BLE001
            log.failure("")

            if isinstance(e, error.Error):
                txrequest.setResponseCode(int(e.status))

            if self.root.debug:
                return traceback.format_exc().encode()

            message = e.message.decode() if isinstance(e, error.Error) else f"{type(e).__name__}: {e}"
            data = {"status": "error", "message": message}
        else:
            if data is not None:
                data["status"] = "ok"

        if data is None:  # render_OPTIONS
            content = b""
        else:
            data["node_name"] = self.root.node_name
            content = self.json_encoder.encode(data).encode() + b"\n"
            txrequest.setHeader("Content-Type", "application/json")

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#preflighted_requests
        txrequest.setHeader("Access-Control-Allow-Origin", "*")
        txrequest.setHeader("Access-Control-Allow-Methods", self.methods)
        txrequest.setHeader("Access-Control-Allow-Headers", "X-Requested-With")
        txrequest.setHeader("Content-Length", str(len(content)))
        return content

    def render_OPTIONS(self, txrequest):
        txrequest.setHeader("Allow", self.methods)
        txrequest.setResponseCode(http.NO_CONTENT)

    @functools.cached_property
    def methods(self):
        methods = ["OPTIONS", "HEAD"]
        if hasattr(self, "render_GET"):
            methods.append("GET")
        if hasattr(self, "render_POST"):
            methods.append("POST")
        return ", ".join(methods)


class DaemonStatus(WsResource):
    """
    .. versionadded:: 1.2.0
    """

    def render_GET(self, txrequest):
        return {
            "pending": sum(queue.count() for queue in self.root.poller.queues.values()),
            "running": len(self.root.launcher.processes),
            "finished": len(self.root.launcher.finished),
        }


class Schedule(WsResource):
    """
    .. versionchanged:: 1.2.0
       Add ``_version`` and ``jobid`` parameters.
    .. versionchanged:: 1.3.0
       Add ``priority`` parameter.
    """

    @param("project")
    @param("spider")
    @param("_version", dest="version", required=False, default=None)
    # See https://github.com/scrapy/scrapyd/pull/215
    @param("jobid", required=False, default=lambda: uuid.uuid1().hex)
    @param("priority", required=False, default=0, type=float)
    @param("setting", required=False, default=list, multiple=True)
    def render_POST(self, txrequest, project, spider, version, jobid, priority, setting):
        if project not in self.root.poller.queues:
            raise error.Error(code=http.OK, message=b"project '%b' not found" % project.encode())

        if version and self.root.eggstorage.get(project, version) == (None, None):
            raise error.Error(code=http.OK, message=b"version '%b' not found" % version.encode())

        spiders = spider_list.get(project, version, runner=self.root.runner)
        if spider not in spiders:
            raise error.Error(code=http.OK, message=b"spider '%b' not found" % spider.encode())

        args = {key.decode(): values[0].decode() for key, values in txrequest.args.items()}
        if version is not None:
            args["_version"] = version

        # 验证请求签名
        self._vers_sign(args, project, spider, priority)

        self.root.scheduler.schedule(
            project,
            spider,
            priority=priority,
            settings=dict(s.split("=", 1) for s in setting),
            _job=jobid,
            **args,
        )
        return {"jobid": jobid}

    def _vers_sign(self, args, project, spider, priority):
        """ 签名验证 """
        api_conf = get_config(section='api')
        signature_key = api_conf.get("signature_key", None)
        if not signature_key:
            # 不验证签名
            return True

        if "timestamp" not in args or "sign" not in args:
            # 参数错误
            raise error.Error(code=http.OK, message=b"Signature parameter error")

        # 验证时间
        timestamp = args["timestamp"]
        now_timestamp = self._get_timestamp()
        diff_time = abs(now_timestamp - float(timestamp))
        signature_expired_time = int(api_conf.get("signature_expired_time", (10 * 60)))
        if diff_time > signature_expired_time:
            # 请求超时
            raise error.Error(code=http.OK, message=b"Request timeout")

        # 生成签名
        append_params = {"project": project, "spider": spider, "priority": float(priority)}
        sign = args.pop("sign", None)
        params = {**args, **append_params}

        # 验证签名
        if ApiSign.create_sign(params) != sign:
            raise error.Error(code=http.OK, message=b"Signature verification failed")

        return True

    @classmethod
    def _get_timestamp(cls):
        """ 获取时间戳 """
        dt = datetime.now()
        tz = pytz.timezone("Asia/Shanghai")
        dt_with_tz = tz.localize(dt)
        return dt_with_tz.timestamp()



class Cancel(WsResource):
    @param("project")
    @param("job")
    # Instead of os.name, use sys.platform, which disambiguates Cygwin, which implements SIGINT not SIGBREAK.
    # https://cygwin.com/cygwin-ug-net/kill.html
    # https://github.com/scrapy/scrapy/blob/06f9c28/tests/test_crawler.py#L886
    @param("signal", required=False, default="INT" if sys.platform != "win32" else "BREAK")
    @param("is_forcibly", required=False, default=False, type=bool)
    def render_POST(self, txrequest, project, job, signal, is_forcibly):
        if project not in self.root.poller.queues:
            raise error.Error(code=http.OK, message=b"project '%b' not found" % project.encode())

        # 获取当前队列
        queue = self.root.poller.queues[project]

        if queue.has(job):
            # 当前任务为pending，直接清除任务队列数据
            prevstate = "pending"
            queue.remove_one(job)
        else:
            # 存在running的任务，先平滑在强制
            prevstate = "running"
            for process in list(self.root.launcher.processes.values()):
                if process.project == project and process.job == job:
                    # 重启进程
                    self._restart_process(process, signal, is_forcibly)

        return {"prevstate": prevstate}


    def _restart_process(self, process, signal, is_forcibly):
        # 是否成功
        if is_forcibly:
            try:
                # 强制重启，修改成异步
                threads.deferToThread(self.root.launcher.restart, process)

                # self.root.launcher.restart(process)
            except Exception as e:
                log.info(f"Unable to forcefully terminate process {process.pid}: {e}")
        else:
            # 优雅终止
            process.transport.signalProcess(signal)


class AddVersion(WsResource):
    @param("project")
    @param("version")
    @param("egg", type=bytes)
    def render_POST(self, txrequest, project, version, egg):
        if not zipfile.is_zipfile(BytesIO(egg)):
            raise error.Error(
                code=http.OK, message=b"egg is not a ZIP file (if using curl, use egg=@path not egg=path)"
            )

        self.root.eggstorage.put(BytesIO(egg), project, version)
        self.root.update_projects()

        spiders = spider_list.set(project, version, runner=self.root.runner)
        return {"project": project, "version": version, "spiders": len(spiders)}


class ListProjects(WsResource):
    def render_GET(self, txrequest):
        return {"projects": self.root.scheduler.list_projects()}


class ListVersions(WsResource):
    @param("project")
    def render_GET(self, txrequest, project):
        return {"versions": self.root.eggstorage.list(project)}


class ListSpiders(WsResource):
    """
    .. versionchanged:: 1.2.0
       Add ``_version`` parameter.
    """

    @param("project")
    @param("_version", dest="version", required=False, default=None)
    def render_GET(self, txrequest, project, version):
        if project not in self.root.poller.queues:
            raise error.Error(code=http.OK, message=b"project '%b' not found" % project.encode())

        if version and self.root.eggstorage.get(project, version) == (None, None):
            raise error.Error(code=http.OK, message=b"version '%b' not found" % version.encode())

        return {"spiders": spider_list.get(project, version, runner=self.root.runner)}


class Status(WsResource):
    """
    .. versionadded:: 1.5.0
    """

    @param("job")
    @param("project", required=False)
    def render_GET(self, txrequest, job, project):
        queues = self.root.poller.queues
        if project is not None and project not in queues:
            raise error.Error(code=http.OK, message=b"project '%b' not found" % project.encode())

        result = {"currstate": None}

        for finished in self.root.launcher.finished:
            if (project is None or finished.project == project) and finished.job == job:
                result["currstate"] = "finished"
                return result

        for process in self.root.launcher.processes.values():
            if (project is None or process.project == project) and process.job == job:
                result["currstate"] = "running"
                return result

        for queue_name in queues if project is None else [project]:
            for message in queues[queue_name].list():
                if message["_job"] == job:
                    result["currstate"] = "pending"
                    return result

        return result


class ListJobs(WsResource):
    """
    .. versionchanged:: 1.1.0
       Add ``start_time`` to running jobs in the response.
    .. versionchanged:: 1.2.0
       Add ``pid`` to running jobs in the response.
    .. versionchanged:: 1.3.0
       The ``project`` parameter is optional. Add ``project`` to all jobs in the response.
    .. versionchanged:: 1.4.0
       Add ``log_url`` and ``items_url`` to finished jobs in the response.
    .. versionchanged:: 1.5.0
       Add ``version``, ``settings`` and ``args`` to pending jobs in the response.
    """

    @param("project", required=False)
    def render_GET(self, txrequest, project):
        queues = self.root.poller.queues
        if project is not None and project not in queues:
            raise error.Error(code=http.OK, message=b"project '%b' not found" % project.encode())

        return {
            "pending": [
                {
                    "id": message["_job"],
                    "project": queue_name,
                    "spider": message["name"],
                    "version": message.get("_version"),
                    "settings": message.get("settings", {}),
                    "args": {k: v for k, v in message.items() if k not in ("name", "_job", "_version", "settings")},
                }
                for queue_name in (queues if project is None else [project])
                for message in queues[queue_name].list()
            ],
            "running": [
                {
                    "id": process.job,
                    "project": process.project,
                    "spider": process.spider,
                    "pid": process.pid,
                    "start_time": str(process.start_time),
                    "log_url": self.root.get_log_url(process),
                    "items_url": self.root.get_item_url(process),
                }
                for process in self.root.launcher.processes.values()
                if project is None or process.project == project
            ],
            "finished": [
                {
                    "id": finished.job,
                    "project": finished.project,
                    "spider": finished.spider,
                    "start_time": str(finished.start_time),
                    "end_time": str(finished.end_time),
                    "log_url": self.root.get_log_url(finished),
                    "items_url": self.root.get_item_url(finished),
                }
                for finished in self.root.launcher.finished
                if project is None or finished.project == project
            ],
        }


class DeleteProject(WsResource):
    @param("project")
    def render_POST(self, txrequest, project):
        self._delete_version(project)
        spider_list.delete(project)
        return {}

    def _delete_version(self, project, version=None):
        try:
            self.root.eggstorage.delete(project, version)
        except ProjectNotFoundError as e:
            raise error.Error(code=http.OK, message=b"project '%b' not found" % project.encode()) from e
        except EggNotFoundError as e:
            raise error.Error(code=http.OK, message=b"version '%b' not found" % version.encode()) from e
        else:
            self.root.update_projects()


class DeleteVersion(DeleteProject):
    @param("project")
    @param("version")
    def render_POST(self, txrequest, project, version):
        self._delete_version(project, version)
        spider_list.delete(project, version)
        return {}
