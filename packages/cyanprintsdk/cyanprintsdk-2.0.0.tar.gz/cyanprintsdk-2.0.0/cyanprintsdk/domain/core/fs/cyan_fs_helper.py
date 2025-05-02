import glob
import shutil
from pathlib import Path
from typing import List

from cyanprintsdk.domain.core.cyan import CyanGlob, GlobType
from cyanprintsdk.domain.core.fs.virtual_file import VirtualFile, VirtualFileReference


class CyanFileHelper:
    def __init__(self, read_dir: str, write_dir: str, globs: List[CyanGlob]):
        self._read_dir = read_dir
        self._write_dir = write_dir
        self.globs = globs

    @property
    def read_dir(self) -> str:
        return str(Path(self._read_dir).resolve())

    @property
    def write_dir(self) -> str:
        return str(Path(self._write_dir).resolve())

    def _glob_dir(self, g: CyanGlob) -> str:
        return str(Path(self.read_dir, g.root or ".").resolve())

    def _copy_file(self, from_path: str, to_path: str) -> None:
        parent = Path(to_path).parent
        parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(from_path, to_path)

    def resolve_all(self) -> List[VirtualFile]:
        copy = [x for x in self.globs if x.type.value == GlobType.Copy.value]
        template = [x for x in self.globs if x.type.value == GlobType.Template.value]

        for c in copy:
            self.copy(c)

        return [file for t in template for file in self.read(t)]

    def get(self, g: CyanGlob) -> List[VirtualFileReference]:
        gr: str = self._glob_dir(g)
        includes = set(glob.glob(g.glob, recursive=True, root_dir=gr))
        excludes = set.union(
            *[set(glob.glob(ex, recursive=True, root_dir=gr)) for ex in g.exclude]
        )
        matched = [Path(gr, x) for x in list(includes - excludes)]

        return [
            VirtualFileReference(gr, self.write_dir, str(Path(x).relative_to(gr)))
            for x in matched
        ]

    def read(self, g: CyanGlob) -> List[VirtualFile]:
        return [ref.read_file() for ref in self.get(g)]

    def copy(self, copy: CyanGlob) -> None:
        glob_root = self._glob_dir(copy)
        includes = set(glob.glob(copy.glob, recursive=True, root_dir=glob_root))
        excludes = set.union(
            *[
                set(glob.glob(ex, recursive=True, root_dir=glob_root))
                for ex in copy.exclude
            ]
        )
        files = list(includes - excludes)

        for read in files:
            read_path = Path(glob_root, read)
            write_path = Path(self.write_dir, read_path.relative_to(glob_root))
            print(f"copy: {read_path} -> {write_path}")
            self._copy_file(str(read_path), str(write_path))
