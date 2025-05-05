import json

from pydbcx_mcp.server import get, post


def test_get():
    assert get("config") != ""
    assert json.loads(get("config/db")) != []
    assert json.loads(get("config/db/duckdb-local")) != {}


def test_post():
    assert post("query", "SELECT 1") == "1\n1"
    assert post("query", "select * from {{ table.db.duckdb-local: SELECT 1 }}") == "1\n1"
