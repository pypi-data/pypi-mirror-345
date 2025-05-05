# min_dotenv

Experimental dotenv loader

## Usage

Given an arbitrary environmental file
```
variable_name = "variable_content"
# Comments in your .env file are allowed
another_var_name=123
```

**Hydrate** your `os` module with the new environmental variables

```python
import os
from min_dotenv import hyd_env
hyd_env('.env')

for name, val in os.environ.items()
    print(f"{name}: {val}")
```

Outputs
```
... all your existing environmental variables
variable_name: variable_content
another_var_name: 123
```

## Installation

TBD
