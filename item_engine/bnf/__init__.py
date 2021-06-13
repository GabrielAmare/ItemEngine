from .constants import *

try:
    # try to import the ``grammar`` module
    from .grammar import *
except ImportError as e:
    from .functions import reload_latest_version
    reload_latest_version()
    # # if not found, load the latest version available in the ``grammars`` package
    # from .grammars import load_latest_version, get_version_name
    #
    # latest_version = load_latest_version(lang='bnf', dst='grammar')
    # from .grammar import *
    # print(f"successfully loaded {get_version_name('bnf', *latest_version)}")

from .build import *
