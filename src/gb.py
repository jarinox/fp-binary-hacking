import os

class GBFile:
    def __init__(self, path: str):
        self.path = path
        if not path.endswith('.gb'):
            raise ValueError("File must have a .gb extension")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")

        self._file = open(path, 'rb+')

    def __del__(self):
        if self._file:
            self._file.close()
    
    def read(self, position: int, size: int) -> bytes:
        """Read a specific number of bytes from the file at a given position."""
        self._file.seek(position)
        return self._file.read(size)

    def write(self, position: int, data: bytes):
        """Write data to the file at a given position."""
        if not isinstance(data, bytes):
            raise TypeError("Data must be of type bytes")
        self._file.seek(position)
        self._file.write(data)
