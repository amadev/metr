import os
import uuid
import pytest
import sqlite3
from metr.db import migrate, get_points, set_point


TEST_DB = '/tmp/test-db-' + str(uuid.uuid4()) + '.sqlite'


@pytest.fixture()
def conn():
    conn = sqlite3.connect(TEST_DB)
    migrate(conn)
    yield conn
    print("teardown db")
    conn.close()
    os.remove(TEST_DB)


def test_get_points(conn):
    assert [] == get_points(conn, 'unknown')
    metric = 'test_get_points'
    with conn:
        conn.execute('insert into metric values (null, ?)', [metric])
    assert [] == get_points(conn, metric)
    with conn:
        conn.execute('insert into point values (null, 1, 1, "2017-01-01")')
        conn.execute('insert into point values (null, 1, 2, "2017-01-01")')
        conn.execute('insert into point values (null, 1, 3, "2017-01-01")')
    points = get_points(conn, metric)
    assert 3 == len(points)
    assert ['1', '2', '3'] == [p[1] for p in points]
    assert ['2017-01-01'] * 3 == [p[0] for p in points]


def test_set_point(conn):
    metric = 'abc'
    with conn:
        cur = conn.execute('select * from metric where name = ?', [metric])
        assert cur.fetchone() is None
    set_point(conn, metric, '1', '2017-01-01')
    with conn:
        cur = conn.execute('select name from metric where name = ?', [metric])
        assert (metric,) == cur.fetchone()
        cur = conn.execute('select value, created '
                           'from point where metric_id = 1')
        assert [('1', '2017-01-01 00:00:00')] == cur.fetchall()
