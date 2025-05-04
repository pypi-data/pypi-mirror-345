from pathlib import Path


class VirtualFileReference:
    def __init__(self, base_read: str, base_write: str, relative: str):
        self.base_read = base_read
        self.base_write = base_write
        self.relative = relative

    @property
    def read(self) -> str:
        return str(Path(self.base_read) / self.relative)

    @property
    def write(self) -> str:
        return str(Path(self.base_write) / self.relative)

    def read_file(self):
        with open(self.read, "r", encoding="utf-8") as file:
            content = file.read()
        return VirtualFile(self.base_read, self.base_write, self.relative, content)


class VirtualFile:
    def __init__(self, base_read: str, base_write: str, relative: str, content: str):
        self.base_read = base_read
        self.base_write = base_write
        self.relative = relative
        self.content = content

    @property
    def read(self) -> str:
        return str(Path(self.base_read) / self.relative)

    @property
    def write(self) -> str:
        return str(Path(self.base_write) / self.relative)

    def write_file(self):
        parent_directory = Path(self.write).parent
        parent_directory.mkdir(parents=True, exist_ok=True)
        with open(self.write, "w", encoding="utf-8") as file:
            file.write(self.content)
