import os

class BytesPatch:
    def __init__(self, offset: int, data: bytes):
        self.offset = offset
        self.data = data

class IPS:
    def __init__(self, path: str):
        self.path = path
        self.patches = []
        if not path.endswith('.ips'):
            raise ValueError("File must have a .ips extension")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")

        self._file = open(path, 'rb')

        self.header = self._file.read(5)
        if self.header != b'PATCH':
            raise ValueError("Invalid IPS file format")
        
        while True:
            if self._file.tell() == os.path.getsize(path) - 3:
                break
            
            offset_bytes = self._file.read(3)
            if len(offset_bytes) < 3:
                break
            offset = int.from_bytes(offset_bytes, 'big')
            data_length_bytes = self._file.read(2)
            data_length = int.from_bytes(data_length_bytes, 'big')
            if data_length == 0:
                break
            data = self._file.read(data_length)
            self.patches.append(BytesPatch(offset, data))

    def __del__(self):
        if self._file:
            self._file.close()

    def extract_offsets(self):
        for patch in self.patches:
            for i in range(len(patch.data)):
                yield patch.offset + i
        
        
    def has_conflict(self, other: 'IPS') -> bool:
        """Find conflicting patches between this IPS and another."""
        offsets = set(self.extract_offsets())
        other_offsets = set(other.extract_offsets())
        return not offsets.isdisjoint(other_offsets)
        

