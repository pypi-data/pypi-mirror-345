import os
import tempfile
from dektools.file import write_file, remove_path, sure_dir
from ..artifacts.staticfiles import StaticfilesArtifact
from .base import AllInOneBase


class StaticfilesAllInOne(AllInOneBase):
    artifact_src_cls = StaticfilesArtifact

    def build(self, item, image):
        path_file_raw = self.artifact_src.pull(item)
        path_file = write_file(None, t=True, m=path_file_raw)
        path_dir = os.path.dirname(path_file)
        path_docker = os.path.join(path_dir, 'Dockerfile')
        write_file(
            path_docker,
            s=f'FROM scratch\nCMD ["sh"]\nCOPY {os.path.basename(path_file)} '
              f"{self.artifact_src.path_keep_dir('/staticfiles', path_file_raw)}"
        )
        self.artifact_all_in_one.build(image, path_dir)
        remove_path(path_docker)
        remove_path(path_file)

    def fetch(self, items, path, each=None):
        sure_dir(path)
        tags = self.artifact_all_in_one.remote_tags(self.rr_all_in_one)
        for item in items:
            tag = self.artifact_src.url_to_docker_tag(item)
            if tags is None or tag in tags:
                image = self.artifact_all_in_one.pull(self.url_mage(item))
                pt = tempfile.mkdtemp()
                self.artifact_all_in_one.cp(image, '/staticfiles/.', pt)
                self.artifact_all_in_one.remove(image)
                pz = os.path.join(pt, os.listdir(pt)[0])
                path_object = self.artifact_src.imports(pz, pt, clone=False)
                remove_path(pt)
            else:
                path_object = self.artifact_src.pull(item)
            if each:
                each(path_object, item)
            write_file(self.artifact_src.path_keep_dir(path, path_object), m=path_object)
