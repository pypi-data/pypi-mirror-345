import pkgutil
import sys

from jh_scrapyd.config import Config
from jh_scrapyd.exceptions import ConfigError
from jh_scrapyd.utils import initialize_component

__version__ = pkgutil.get_data(__package__, "VERSION").decode().strip()
version_info = tuple(__version__.split(".")[:3])
jh_config = Config()



def get_application(config=None):
    if config is None:
        config = Config()
    try:
        return initialize_component(config, "application", "jh_scrapyd.app.application")
    except ConfigError as e:
        sys.exit(str(e))


def get_config(option=None, default=None, section: str = "jh_scrapyd"):
    configs = dict(jh_config.items(section))
    if not option:
        return configs
    return configs.get(option, default)


def is_debug() -> bool:
    if str(get_config(option="debug", default="off")).lower() == "on":
        return True
    else:
        return False


def debug_log(*kwargs, title: str = "start"):
    if is_debug():
        print("=" * 60, title, "=" * 60)
        print(*kwargs)
        print("\n")