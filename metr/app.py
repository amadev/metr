import matplotlib
import re
import sys
import os
import sqlite3
from doan.dataset import Dataset
from doan.graph import plot_date
from metr.db import get_points, set_point


matplotlib.use('AGG')


DIR = os.path.dirname(__file__) + '/'
DB = DIR + 'db/metr.db'
BASE_URL = '/metr/'


class Response(object):
    pass


def show_metric(metric):
    conn = sqlite3.connect(DB)
    points = get_points(conn, metric)
    conn.close()
    fname = DIR + 'output/%s.jpg' % metric
    d = Dataset([Dataset.DATE, Dataset.FLOAT])
    d.load(points)
    plot_date(d, output=fname, figsize=(14, 7), linestyle='-')

    data = open(fname, 'rb').read()
    r = Response()
    r.body = data
    r.code = '200 OK'
    r.headers = [('content-type', 'image/jpeg'),
                 ('content-length', str(len(r.body)))]
    return r


def update_metric(metric, value, dt):
    conn = sqlite3.connect(DB)
    set_point(conn, metric, value, dt)
    conn.close()

    r = Response()
    r.body = ''
    r.code = '302 Found'
    r.headers = [('Location', '/metr/%s' % metric)]
    return r


def list_metrics():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('select name from metric')

    data = []
    rows = c.fetchall()
    for row in rows:
        data.append('<a href="%s">%s</a>' % (BASE_URL + row[0], row[0]))
    conn.close()

    r = Response()
    r.body = '<br />'.join(data).encode()
    r.code = '200 OK'
    r.headers = [('content-type', 'text/html'),
                 ('content-length', str(len(r.body)))]
    return r


def application(environ, start_response):

    segments = filter(None, environ['PATH_INFO'].split('/'))

    try:
        metric = segments[0]
    except IndexError:
        metric = None

    try:
        value = segments[1]
    except IndexError:
        value = None

    try:
        dt = segments[2]
    except IndexError:
        dt = None

    # TODO: input validation

    #     if re.match('^[a-z\-]{1, 255}', metric):
    #         raise ValueError('invalid metric')
    #     r = show_metric(metric)

    r = Response()
    r.code = '200 OK'
    r.body = 'Metrics'
    r.headers = [('Content-type', 'text/plain'),
                 ('Content-Length', str(len(r.body)))]

    if metric:
        if not value:
            r = show_metric(metric)
        else:
            r = update_metric(metric, value, dt)
    else:
        r = list_metrics()

    # print >> environ['wsgi.errors'], 'ENVIRON', environ

    start_response(r.code, r.headers)
    return [r.body]
