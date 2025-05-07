import base64
import zlib
import pickle


def deserialize_data(string):
    """Convert a compressed, base64-encoded string back to a Python object."""
    encoded = string.encode('ascii')
    compressed = base64.b64decode(encoded)
    pickled = zlib.decompress(compressed)
    return pickle.loads(pickled)


if __name__ == "__main__":
    ser_str = "eNprYJ3KxwABPVz6iQUF+nplqXllU/QAPmgGDQ=="
    print(deserialize_data(ser_str))