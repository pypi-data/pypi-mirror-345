# Database Library

A Python-based database management library that supports both MySQL and SQLite. It provides an easy-to-use interface for defining tables, inserting data, searching records, updating, deleting, and more.

## Features
- Supports MySQL (via PyMySQL) and SQLite.
- Table creation, modification, and deletion.
- Data insertion, updating, and querying.
- Bulk insert operations.
- Pagination support.
- Schema introspection.
- Data replication between SQLite and MySQL.

## Installation

```sh
pip install deamstools
```

## Usage

### Initialize Database

```python
from database import Database, LocalDatabase

# MySQL Database Connection
mysql_db = Database(username='root', password='password', host='localhost', port=3306, database='testdb')

# SQLite Local Database
sqlite_db = LocalDatabase(db_path='local.db')
```

---

### Define a Table

```python
table = mysql_db.define_table("users", id=Integer, name=Text, age=Integer)
```

---

### Insert Data

```python
mysql_db.insert("users", id=1, name="Alice", age=25)
```

---

### Bulk Insert

```python
data = [
    {"id": 2, "name": "Bob", "age": 30},
    {"id": 3, "name": "Charlie", "age": 22}
]
mysql_db.bulk_insert("users", data)
```

---

### Search Data

```python
users = mysql_db.search("users")
print(users)  # List of all users
```

Search with filters:

```python
alice = mysql_db.search("users", id=1)
print(alice)
```

---

### Get a Single Record

```python
user = mysql_db.get("users", id=1)
print(user)
```

---

### Update Data

```python
mysql_db.update("users", {"id": 1}, {"age": 26})
```

---

### Delete Data

```python
mysql_db.delete("users", id=3)
```

---

### List All Tables

```python
tables = mysql_db.list_tables()
print(tables)
```

---

### Count Rows

```python
user_count = mysql_db.count_rows("users")
print(user_count)
```

---

### Get Distinct Column Values

```python
distinct_ages = mysql_db.distinct_values("users", "age")
print(distinct_ages)
```

---

### Search with Pagination

```python
users_page1 = mysql_db.search_paginated("users", page=1, page_size=2)
print(users_page1)
```

---

### Get Table Schema

```python
schema = mysql_db.get_table_schema("users")
print(schema)
```

---

### Rename Table

```python
mysql_db.rename_table("users", "members")
```

---

### Add a Column

```python
mysql_db.add_column("members", "email", "TEXT")
```

---

### Drop a Column

```python
mysql_db.drop_column("members", "email")
```

---

### Delete Table

```python
mysql_db.delete_table("members")
```

---

### Replicate SQLite to MySQL

```python
mysql_db.replicate_local_to_online(sqlite_db)
```

### Replicate MySQL to SQLite

```python
sqlite_db.replicate_online_to_local(mysql_db)
```

### Get column type

```python
print(sqlite_db.get_column_type("users", "age"))
print(my_sql.get_column_type("users", "age"))
```

### Edit column type

```python
sqlite_db.edit_column_type("users", "age", "VARCHAR(10)")
mysql_db.edit_column_type("users", "age", "TEXT")
```
---

## License
This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

