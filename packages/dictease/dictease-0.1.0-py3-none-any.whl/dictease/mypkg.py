import ast
def fetch(data, *keys):
    current = data
    for key in keys:
        # assert isinstance(current, dict), f"Expected dict at {key}, got {type(current).__name__}"
        # assert key in current, f"Key '{key}' not found"
        current = current.get(key, None)
    return current
x=input()
x_tuple=ast.literal_eval(x)
data,*keys=x_tuple
print(fetch(data,*keys))