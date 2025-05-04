import inspect

def log_with_func_name(message):
    func_name = inspect.stack()[1].function
    print(f"[{func_name}] {message}")
