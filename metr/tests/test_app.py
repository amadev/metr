import mock
from metr import app


def test_get_handler():
    assert (app.list_metrics, [], {}) == app.get_handler({})
    assert (app.list_metrics, [], {}) == app.get_handler(
        {'PATH_INFO': '/metr/'})
    assert (app.list_metrics, [], {}) == app.get_handler(
        {'PATH_INFO': '/metr/example/'})
    assert (app.show_metric, ('example',), {}) == app.get_handler(
        {'PATH_INFO': '/metr/example'})
    assert (app.update_metric, ('metr_1-1', '100.1'), {}) == app.get_handler(
        {'PATH_INFO': '/metr/metr_1-1/100.1'})
    assert (app.update_metric, ('metr_1-1', '100.1', '2017-01-01'), {}) == \
        app.get_handler({'PATH_INFO': '/metr/metr_1-1/100.1/2017-01-01'})


@mock.patch('sqlite3.connect')
def test_list_metrics(db):
    app.application({}, lambda status, headers: 1)


@mock.patch('__builtin__.open')
@mock.patch('matplotlib.pyplot.savefig')
@mock.patch('os.makedirs')
@mock.patch('sqlite3.connect')
def test_show_metric(db, mkdir, savefig, open):
    app.application({'PATH_INFO': '/metr/meric-1'}, lambda status, headers: 1)


@mock.patch('sqlite3.connect')
def test_update_metric(db):
    app.application(
        {'PATH_INFO': '/metr/meric-2/10'}, lambda status, headers: 1)
    app.application(
        {'PATH_INFO': '/metr/meric-2/10/2017-01-01'},
        lambda status, headers: 1)
