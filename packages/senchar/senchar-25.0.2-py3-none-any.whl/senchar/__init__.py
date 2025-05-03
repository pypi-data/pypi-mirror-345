"""
Scientific image sensor characterization package.
"""

import typing
import importlib.metadata
from senchar.database import Database

# senchar version, from pyproject.toml
__version__ = importlib.metadata.version("senchar")

# senchar.db is used everywhere
db = Database()
db.version = __version__

# senchar.log() is used everywhere, initially just print()
log = print

# cleanup namespace
del typing
del Database
del importlib
