
from os import path
import sqlite3

__version__ = "0.0.1a2"
__version_info__ = tuple(__version__.split("."))

def loadable_path():
  """ Returns the full path to the sqlite-jiff loadable SQLite extension bundled with this package """

  loadable_path = path.join(path.dirname(__file__), "jiff0")
  return path.normpath(loadable_path)

def load(conn: sqlite3.Connection)  -> None:
  """ Load the sqlite-jiff SQLite extension into the given database connection. """

  conn.load_extension(loadable_path())

