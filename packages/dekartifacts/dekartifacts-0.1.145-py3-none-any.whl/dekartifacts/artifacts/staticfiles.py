import os
from urllib.parse import urlparse
from dektools.file import write_file
from dektools.download import download_tree_from_http, download_http_exist
from .base import ArtifactBase


class StaticfilesArtifact(ArtifactBase):
    typed = 'staticfiles'

    @classmethod
    def url_to_docker_tag(cls, url):
        tag = urlparse(url).path[1:].replace('/', '-')
        return cls.normalize_docker_tag(url, tag)

    def login(self, registry='', username='', password=''):
        self.login_auth(registry, username=username, password=password)

    def imports(self, path_file, path_dir, clone=True):
        path_object = os.path.join(self.path_objects, path_file[len(path_dir) + 1:])
        write_file(path_object, **{'c' if clone else 'm': path_file})
        return path_object

    def pull(self, url):
        auth = self.get_auth(urlparse(url).netloc) or {}
        return os.path.join(
            self.path_objects, download_tree_from_http(
                self.path_objects, [url], **auth
            )[url]
        )

    def exist(self, url):
        auth = self.get_auth(urlparse(url).netloc) or {}
        return download_http_exist(url, **auth)
