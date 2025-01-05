## ProxmoxAPI Class. Filtering Results.

The API supports filtering the response to return only the desired keys. The behavior of the `filter_keys` parameter depends on the structure of the result.

### Behavior of `filter_keys`

1. **If the result is a dictionary (`dict`):**
   - `filter_keys="key"`: Returns the plain string value associated with the key.
   - `filter_keys=["key1", "key2"]`: Returns a new dictionary containing only the specified keys and their values.

2. **If the result is a list of dictionaries (`list[dict]`):**
   - `filter_keys=["key1", "key2"]`: Filters each dictionary in the list to include only the specified keys.

3. **For nested dictionaries:**
   - Use dot notation in `filter_keys` to specify keys within nested dictionaries.  
     For example, `filter_keys=["parent.child", "parent.another_child"]` will retrieve the nested values within the parent dictionary.

### Examples

#### Filtering a Dictionary
```python
response = {
    "version": "7.4",
    "release_date": "2023-10-01",
    "features": ["feature1", "feature2"]
}

# Example 1: Single key
print(api._response_analyze(response, filter_keys="version"))
# Output: "7.4"

# Example 2: Multiple keys
print(api._response_analyze(response, filter_keys=["version", "release_date"]))
# Output: {"version": "7.4", "release_date": "2023-10-01"}
```
#### Filtering a List of Dictionaries
```python
response = [
    {"node": "node1", "status": "online", "cpu": "8 cores"},
    {"node": "node2", "status": "offline", "cpu": "4 cores"},
]

# Filter specific keys
print(api._response_analyze(response, filter_keys=["node", "status"]))
# Output: [{"node": "node1", "status": "online"}, {"node": "node2", "status": "offline"}]
```
#### Filtering Nested Dictionaries
```python
response = {
    "cluster": {
        "name": "cluster1",
        "status": {"online_nodes": 3, "offline_nodes": 1},
    }
}

# Filter nested keys using dot notation
print(api._response_analyze(response, filter_keys=["cluster.name", "cluster.status.online_nodes"]))
# Output: {"cluster.name": "cluster1", "cluster.status.online_nodes": 3}
```
By specifying the desired keys with filter_keys, you can efficiently retrieve only the data you need.

This section clearly outlines how filtering works with examples for different data structures, including nested dictionaries.



