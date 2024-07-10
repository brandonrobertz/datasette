from .utils import tilde_encode, path_with_format, HASH_LENGTH, PrefixedUrlString
import urllib


class Urls:
    def __init__(self, ds):
        self.ds = ds

    def path_has_base_url(self, path):
        base_url = self.ds.setting("base_url")
        if not base_url:
            return True
        if path.startswith(base_url):
            return True
        base_url_noslash = base_url.strip("/")
        if path.startswith(base_url_noslash):
            return True
        return False

    def path(self, path, format=None):
        if not isinstance(path, PrefixedUrlString):
            if not self.path_has_base_url(path):
                path = self.ds.setting("base_url").rstrip("/") + "/" + path.lstrip("/")
            # if the path here fails to have a leading slash then it sets
            # up a condition for a duplicate base_url prefix to be added
            # downstream by Datasette.absolute_url
            if not path.startswith("/"):
                path = "/" + path
        if format is not None:
            path = path_with_format(path=path, format=format)
        return PrefixedUrlString(path)

    def instance(self, format=None):
        return self.path("", format=format)

    def static(self, path):
        return self.path(f"-/static/{path}")

    def static_plugins(self, plugin, path):
        return self.path(f"-/static-plugins/{plugin}/{path}")

    def logout(self):
        return self.path("-/logout")

    def database(self, database, format=None):
        db = self.ds.get_database(database)
        return self.path(tilde_encode(db.route), format=format)

    def table(self, database, table, format=None):
        path = f"{self.database(database)}/{tilde_encode(table)}"
        if format is not None:
            path = path_with_format(path=path, format=format)
        return PrefixedUrlString(path)

    def query(self, database, query, format=None):
        path = f"{self.database(database)}/{tilde_encode(query)}"
        if format is not None:
            path = path_with_format(path=path, format=format)
        return PrefixedUrlString(path)

    def row(self, database, table, row_path, format=None):
        path = f"{self.table(database, table)}/{row_path}"
        if format is not None:
            path = path_with_format(path=path, format=format)
        return PrefixedUrlString(path)

    def row_blob(self, database, table, row_path, column):
        return self.table(database, table) + "/{}.blob?_blob_column={}".format(
            row_path, urllib.parse.quote_plus(column)
        )
