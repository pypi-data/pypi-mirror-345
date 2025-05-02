## MongoApiClient Python Client

### Description

`MongoApiClient` is a Python library for interacting with a RESTful MongoDB API. It provides a fluent interface for building queries, performing CRUD operations, and running custom or aggregation pipelines. All responses are wrapped in a consistent `MongoApiReponse` envelope.

---

### Installation

```bash
pip install mongo-api-client
```

### Usage
```python
from mongo_api_client import MongoApiClient, MongoApiReponse
```

---

### Quick Start

```python
client = MongoApiClient(
    server_url="localhost",
    server_port=9776,
    api_key="YOUR_API_KEY",  # optional
)
```

### Under the Hood: Core Classes & Flow

Every client operation ultimately returns a **`MongoApiReponse`** instance. Here’s how the classes collaborate:

1. **Fluent Builder (`MongoApiClient`)**
   - You chain methods (`where()`, `sort_by()`, `page()`, etc.) to construct query parameters.
   - CRUD and utility methods (`find()`, `insert()`, `delete()`, etc.) trigger an HTTP call.

2. **Request Execution**
   - **`_request`** builds the final URL and headers, then calls **`_send_request`** (wrapped by `@retry`).
   - On error, `_request` catches exceptions and returns a raw payload with `status=False`.

3. **Response Wrapping**
   - **`_wrap_response`** takes the raw `dict` payload and instantiates a **`MongoApiReponse`**, normalizing `status`, `code`, `data`, `error`, and utility fields (`databases`, `tables`, `message`).

4. **Using `MongoApiReponse`**
   - Once received, you simply call its accessor methods:
     ```python
     resp = client.find()
     if resp.get_status():
         data = resp.get_data()
         print(data)
     else:
         print(f"Error {resp.get_status_code()}: {resp.get_error()}")
     ```

This separation of concerns ensures your calling code never deals with raw JSON or HTTP details—just fluent queries and wrapped responses.

```python
# Example: find + response handling
resp = (
    client
    .from_db("mydb")
    .from_table("users")
    .where("age", ">=", 21)
    .find()
)
if resp.get_status():
    print(resp.get_data())
else:
    print(resp.get_error())
```
### Example Retriving and processing results
```python
client = MongoApiClient(
    server_url="localhost",
    server_port=9776,
    api_key="YOUR_API_KEY",  # optional
)

# Simple find example
resp = (
    client
    .from_db("mydb")
    .from_table("users")
    .where("age", ">=", 21)
    .sort_by("name", "asc")
    .page(1)
    .per_page(10)
    .find()
)

if resp.get_status():
    for doc in resp.get_data():
        print(doc)
else:
    print("Error:", resp.get_error())
```

---

## 1. Building Queries

Define your database and collection, then chain filters, sorting, grouping, and pagination.

```python
# Start with client, select DB and collection
q = (
    client
    .from_db("mydb")             # select database
    .from_table("people")         # select collection
)

# Add filters
q = q.where("age", ">=", 18)    # AND filter
q = q.or_where("status", "=", "inactive")  # OR filter

# Sort and pagination
q = q.sort_by("created_at", "desc")
q = q.page(2).per_page(5)

# Optional grouping
q = q.group_by("country")
```

## 2. Retrieving Data

| Method            | Description                                 |
| ----------------- | ------------------------------------------- |
| `all()`           | Fetch all matching documents                |
| `get_all()`       | Alias for `all()`                           |
| `find()`          | Same as `all()`                             |
| `first()`         | Fetch single document (page=1, per\_page=1) |
| `one()`           | Alias for `first()`                         |
| `first_or_none()` | Alias for `first()`                         |
| `find_by_id(id)`  | Fetch a document by its `_id`               |

```python
# Fetch multiple\

resp = q.find()
# Instead of print(resp), use the response wrapper
if resp.get_status():
    data = resp.get_data()
    print(f"Found {resp.get_total_count()} documents:", data)
else:
    print(f"Error {resp.get_status_code()}: {resp.get_error()}")
```

## 3. Inserting Data

| Method            | Description                                 |
| ----------------- | ------------------------------------------- |
| `insert(docs)`    | Insert one or more documents                |
| `insert_if(docs)` | Conditional insert if filters did not match |

```python
# Bulk insert
docs = [{"name":"Alice"}, {"name":"Bob"}]
resp = (
    client
    .into_db("mydb")
    .into_table("people")
    .insert(docs)
)

# Conditional insert
resp = (
    client
    .from_db("mydb")
    .from_table("people")
    .where("name", "=", "Charlie")
    .insert_if(docs)
)
```

## 4. Updating Data

| Method                   | Description                       |
| ------------------------ | --------------------------------- |
| `update(data)`           | Update documents matching filters |
| `update_by_id(id, data)` | Update a single document by ID    |

```python
# Update matching docs
resp = (
    client
    .from_db("mydb")
    .from_table("people")
    .where("name", "=", "Alice")
    .update({"age":30})
)

# Update by ID
resp = client.update_by_id(
    "507f1f77bcf86cd799439011",
    {"age":25}
)
```

## 5. Deleting Data

| Method             | Description                       |
| ------------------ | --------------------------------- |
| `delete()`         | Delete documents matching filters |
| `delete_by_id(id)` | Delete a document by ID           |

```python
# Delete matching docs
resp = (
    client
    .from_db("mydb")
    .from_table("people")
    .or_where("age", "<", 18)
    .delete()
)
# Check deletion result
if resp.get_status():
    print(f"Deleted {resp.get_total_count()} documents.")
else:
    print(f"Error {resp.get_status_code()}: {resp.get_error()}")
```

## 6. Utilities: Databases & Tables

| Method                  | Description                     |
| ----------------------- | ------------------------------- |
| `list_databases()`      | List all databases              |
| `list_tables_in_db(db)` | List collections in a database  |
| `delete_database(db)`   | Drop a database                 |
| `delete_table(db, tbl)` | Drop a collection in a database |

```python
# List
resp = client.list_databases()
resp = client.list_tables_in_db("mydb")

# Drop
resp = client.delete_database("old_db")
resp = client.delete_table("mydb", "old_table")
```

## 7. Custom Queries & Aggregation

| Method                                   | Description                            |
| ---------------------------------------- | -------------------------------------- |
| `execute_custom_query(query, aggregate)` | Run raw filter or aggregation pipeline |

```python
# Simple filter via POST /custom-query
resp = client.execute_custom_query(
    custom_query={"stats.timePlayed": {"$gte": 10000}},
    aggregate=False
)

# Aggregation pipeline
pipeline = [
    {"$match": {"stats.timePlayed": {"$gte": 10000}}},
    {"$group": {"_id": "$country", "total": {"$sum": "$stats.timePlayed"}}},
    {"$sort": {"total": -1}},
    {"$limit": 5},
]
resp = client.execute_custom_query(pipeline, aggregate=True)
```