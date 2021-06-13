from typing import Optional

__all__ = ["File", "FileSocket"]


class File:
    def __init__(self, path: str):
        self.path = path

    def save(self, content: str):
        """Save content into the file"""
        with open(self.path, mode='w', encoding='utf-8') as file:
            file.write(content)

    def load(self) -> str:
        """Load the content of the file"""
        with open(self.path, mode='r', encoding='utf-8') as file:
            return file.read()


class FileSocket:
    """This represent a file socket"""

    def __init__(self):
        self.file: Optional[File] = None

    @property
    def is_empty(self) -> bool:
        return self.file is None

    def bind(self, filepath: str):
        """Bind to a file"""
        assert self.is_empty, "cannot bind if there's a binded file"
        self.file = File(filepath)

    def unbind(self) -> File:
        """Unbind from the file"""
        assert not self.is_empty, "cannot unbind if there's no binded file"
        file = self.file
        self.file = None
        return file

    def save(self, content: str):
        """Save content into the binded file"""
        self.file.save(content)

    def load(self) -> str:
        """Load the content of the binded file"""
        return self.file.load()
