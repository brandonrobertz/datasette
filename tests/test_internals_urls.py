from datasette import Request
from datasette.app import Datasette
from datasette.utils import PrefixedUrlString
import pytest


@pytest.fixture(scope="module")
def ds():
    return Datasette([], memory=True)


@pytest.mark.parametrize(
    "base_url,path,expected",
    [
        ("/", "/", "/"),
        ("/", "/foo", "/foo"),
        ("/", "db", "/db"),
        ("/prefix/", "/", "/prefix/"),
        ("/prefix/", "/foo", "/prefix/foo"),
        ("/prefix/", "foo", "/prefix/foo"),
    ],
)
def test_path(ds, base_url, path, expected):
    ds._settings["base_url"] = base_url
    actual = ds.urls.path(path)
    assert actual == expected
    assert isinstance(actual, PrefixedUrlString)


@pytest.mark.parametrize(
    "base_url,path,expected_path",
    [
        ("/prefix/", "/", "/prefix/"),
        ("/prefix/", "", "/prefix/"),
        ("/prefix/", "/prefix/", "/prefix/"),
        ("/prefix/", "/prefix/table/1", "/prefix/table/1"),
        ("/prefix/", "prefix/table/1", "/prefix/table/1"),
        ("/prefix/", "-/static/app.css", "/prefix/-/static/app.css"),
        ("/prefix/", "/table/1", "/prefix/table/1"),
        ("/prefix/", "table/1", "/prefix/table/1"),
    ],
)
def test_path_applied_twice_does_not_double_prefix(ds, base_url, path, expected_path):
    ds._settings["base_url"] = base_url
    actual_path = ds.urls.path(path)
    assert actual_path == expected_path


@pytest.mark.parametrize(
    "base_url,expected",
    [
        ("/", "/"),
        ("/prefix/", "/prefix/"),
    ],
)
def test_instance(ds, base_url, expected):
    ds._settings["base_url"] = base_url
    actual = ds.urls.instance()
    assert actual == expected
    assert isinstance(actual, PrefixedUrlString)


@pytest.mark.parametrize(
    "base_url,file,expected",
    [
        ("/", "foo.js", "/-/static/foo.js"),
        ("/prefix/", "foo.js", "/prefix/-/static/foo.js"),
    ],
)
def test_static(ds, base_url, file, expected):
    ds._settings["base_url"] = base_url
    actual = ds.urls.static(file)
    assert actual == expected
    assert isinstance(actual, PrefixedUrlString)


@pytest.mark.parametrize(
    "base_url,plugin,file,expected",
    [
        (
            "/",
            "datasette_cluster_map",
            "datasette-cluster-map.js",
            "/-/static-plugins/datasette_cluster_map/datasette-cluster-map.js",
        ),
        (
            "/prefix/",
            "datasette_cluster_map",
            "datasette-cluster-map.js",
            "/prefix/-/static-plugins/datasette_cluster_map/datasette-cluster-map.js",
        ),
    ],
)
def test_static_plugins(ds, base_url, plugin, file, expected):
    ds._settings["base_url"] = base_url
    actual = ds.urls.static_plugins(plugin, file)
    assert actual == expected
    assert isinstance(actual, PrefixedUrlString)


@pytest.mark.parametrize(
    "base_url,expected",
    [
        ("/", "/-/logout"),
        ("/prefix/", "/prefix/-/logout"),
    ],
)
def test_logout(ds, base_url, expected):
    ds._settings["base_url"] = base_url
    actual = ds.urls.logout()
    assert actual == expected
    assert isinstance(actual, PrefixedUrlString)


@pytest.mark.parametrize(
    "base_url,format,expected",
    [
        ("/", None, "/_memory"),
        ("/prefix/", None, "/prefix/_memory"),
        ("/", "json", "/_memory.json"),
    ],
)
def test_database(ds, base_url, format, expected):
    ds._settings["base_url"] = base_url
    actual = ds.urls.database("_memory", format=format)
    assert actual == expected
    assert isinstance(actual, PrefixedUrlString)


@pytest.mark.parametrize(
    "base_url,name,format,expected",
    [
        ("/", "name", None, "/_memory/name"),
        ("/prefix/", "name", None, "/prefix/_memory/name"),
        ("/", "name", "json", "/_memory/name.json"),
        ("/", "name.json", "json", "/_memory/name~2Ejson.json"),
    ],
)
def test_table_and_query(ds, base_url, name, format, expected):
    ds._settings["base_url"] = base_url
    actual1 = ds.urls.table("_memory", name, format=format)
    assert actual1 == expected
    assert isinstance(actual1, PrefixedUrlString)
    actual2 = ds.urls.query("_memory", name, format=format)
    assert actual2 == expected
    assert isinstance(actual2, PrefixedUrlString)


@pytest.mark.parametrize(
    "base_url,format,expected",
    [
        ("/", None, "/_memory/facetable/1"),
        ("/prefix/", None, "/prefix/_memory/facetable/1"),
        ("/", "json", "/_memory/facetable/1.json"),
    ],
)
def test_row(ds, base_url, format, expected):
    ds._settings["base_url"] = base_url
    actual = ds.urls.row("_memory", "facetable", "1", format=format)
    assert actual == expected
    assert isinstance(actual, PrefixedUrlString)


@pytest.mark.parametrize(
    "base_url,request_url,path",
    [
        ("/base_url", "/base_url", "/base_url/_memory/facetable/1"),
        ("/base_url/", "/base_url/_memory/facetable", "/base_url/_memory/facetable/1"),
        ("/base_url/", "/base_url/", "base_url/_memory/facetable/1"),
    ],
)
def test_absolute_url_no_dupes_base_url(ds, base_url, request_url, path):
    ds._settings["base_url"] = base_url
    request = Request.fake(request_url, method="GET")
    resolved = ds.absolute_url(request, path)
    print("resolved", resolved)
    assert resolved.count("base_url") == 1, f"Duplicate base_url detected: {resolved}"
