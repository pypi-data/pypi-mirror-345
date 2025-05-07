import base64
import zlib
import pickle
import pandas as pd


def serialize_data(obj, compression_level=9):
    """Convert a Python object to a compressed, base64-encoded string."""
    pickled = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    compressed = zlib.compress(pickled, compression_level)
    encoded = base64.b64encode(compressed)
    return encoded.decode('ascii')


if __name__ == "__main__":
    # ser_str = "eNprYJ3KxwABPVz6iQUF+nplqXllU/QAPmgGDQ=="
    args = []
    kwargs = {
        "data_df": pd.DataFrame({
            "customer_id": [101, 102, 103, 104, 105],
            "name": ["Alice", "Bob", "Charlie", "David", "Eva"],
            "age": [25, 30, 35, 40, 45],
            "ones": [1, 2, 3, 4, 5],
            "tens": [10, 20, 30, 40, 50],
            "hundreds": [100, 200, 300, 400, 500],
            "purchase_amount": [150.75, 200.5, 300.0, 400.25, 500.0],
            "membership_status": ["gold", "silver", "gold", "platinum", "silver"]
            }),
        "extra_params": {
            "max_amount" : 300
        }
    }
    serialized_params = serialize_data({
        "function_args": args,
        "function_kwargs": kwargs
    })
    print(serialized_params)