import sqlite3

def fetch(DB_PATH: str, query: str) -> list[tuple[str]]:
  """
    Fetch the data with given query from the given database.
    Return a list of rows. Each row is a tuple.

    DB_PATH: the path to the .sqlite db

    query: user query
  """
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute(query)
  rows = cursor.fetchall()
  conn.close()

  return rows