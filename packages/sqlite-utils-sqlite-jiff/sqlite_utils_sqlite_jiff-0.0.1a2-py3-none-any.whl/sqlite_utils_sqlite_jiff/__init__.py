
from sqlite_utils import hookimpl
import sqlite_jiff

__version__ = "0.0.1a2"
__version_info__ = tuple(__version__.split("."))

@hookimpl
def prepare_connection(conn):
  conn.enable_load_extension(True)
  sqlite_jiff.load(conn)
  conn.enable_load_extension(False)
