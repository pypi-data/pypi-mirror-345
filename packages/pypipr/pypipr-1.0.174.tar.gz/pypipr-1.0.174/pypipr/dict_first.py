def dict_first(d: dict, remove=False):
    """
    Mengambil nilai (key, value) pertama dari dictionary dalam bentuk tuple.

    ```python
    d = {
        "key2": "value2",
        "key3": "value3",
        "key1": "value1",
    }
    print(dict_first(d, remove=True))
    print(dict_first(d))
    ```
    """
    for k in d:
        return (k, d.pop(k) if remove else d[k])
