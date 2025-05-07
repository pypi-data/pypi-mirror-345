# from code_executor_py import RemoteExecutorServer

# res = RemoteExecutorServer(host="0.0.0.0", port=8099)
# res.run()

from code_executor_py import RemoteExecutor
import pandas as pd

executor = RemoteExecutor("http://localhost:8099")

# Test function code
func_code = """
import toml
from yaml import safe_load
import requests as req
# import pathlib.Path as pth
from itertools import chain, combinations
import tomli, pytz, click

def add_numbers(a: int, b: int) -> int:
    return a + b
    """


# Create executable function
add_numbers = executor.create_executable(func_code)

# Test with positional arguments
result1 = add_numbers(5, 3)
assert result1 == 8, f"Expected 8, got {result1}"

# Test with keyword arguments
result2 = add_numbers(a=2, b=7)
assert result2 == 9, f"Expected 9, got {result2}"


print("All remote executor tests passed!")

function_code = "import pandas as pd\n\n\ndef filter_gold_customers(data_df, extra_params):\n    '''\n    Filters the dataframe to keep only customers with gold membership and purchased less than a specified maximum USD amount.\n    '''\n    max_amount = extra_params[\"max_amount\"]\n    filtered_df = data_df[(data_df['membership_status'] == 'gold') & (data_df['purchase_amount'] < max_amount)]\n    return filtered_df\n"
filter_gold_customers = executor.create_executable(function_code)


result_df = filter_gold_customers(
        data_df=pd.DataFrame({
            "customer_id": [101, 102, 103, 104, 105],
            "name": ["Alice", "Bob", "Charlie", "David", "Eva"],
            "age": [25, 30, 35, 40, 45],
            "ones": [1, 2, 3, 4, 5],
            "tens": [10, 20, 30, 40, 50],
            "hundreds": [100, 200, 300, 400, 500],
            "purchase_amount": [150.75, 200.5, 300.0, 400.25, 500.0],
            "membership_status": ["gold", "silver", "gold", "platinum", "silver"]
            }),
        extra_params={
            "max_amount": 300
        }
)

print(result_df)

