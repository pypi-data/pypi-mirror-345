pad # MySQL Connection Library

The Connection class provides a simple wrapper around `mysql.connector` to manage database connections.
Below is a basic guide on how to use the class, along with sample use cases for each function:

## Prerequisites

- Python 3.x
- mysql-connector-python: Install via pip using `pip install mysql-connector-python`
- `.env` file: This should contain your MySQL credentials.
  Example:

```
RDS_HOSTNAME=db.dvlp1.circ.zone
# Your database user without @circ.zone
RDS_USERNAME=mydbuser
# Your database password
RDS_PASSWORD=mysecretpassword
# Not mandatory
RDS_DATABASE=mydatabase
LOGZIO_TOKEN=cXNHuVkkffkilnkKzZlWExECRlSKqopE
```

## Classes
GenericMapping is for mapping tables which include mostly two id's of two entities.
GenericCrudMl is for parent table and child table with Multi-Language (ML) titles

## Usage

**Connection Class:**

```py
from database_mysql_local.connector import Connector

# Initialization:
connection = Connector.connect("your_database")

# Create a Cursor for Database Connection: #these are examples of usage
cursor = connection.cursor()
cursor.execute("SELECT * FROM my_table")
results = cursor.fetchall()

# Execute a Query.
cursor.execute("INSERT INTO my_table (column1, column2) VALUES (%s, %s)", ("value1", "value2"))

# Commit Changes:
connection.commit()

# Fetch All Rows:
cursor.execute("SELECT * FROM my_table")
rows = cursor.fetchall()

# Fetch One Row:
cursor.execute("SELECT * FROM my_table WHERE column_name='some_value'")
row = cursor.fetchone()

# Get Columns Description:
cursor.description()

# Get Last Inserted ID:
cursor.get_lastrowid()

# Close Connection:
connection.close()
```

# GenericCRUD Class

The GenericCRUD class is a Python utility for simplifying common SQL database operations. It provides an easy-to-use
interface to perform basic CRUD (Create, Read, Update, Delete) operations on database tables.

## Usage

You can use either a where condition or a column_name and column_value to specify which records to
select/update/delete.  
You can also specify the columns to select (default is all columns).

Here's a simple example of how to use the `GenericCRUD` class:

```python
from database_mysql_local.generic_crud import GenericCRUD

# Initialize the CRUD object with your schema name and connection (or let it create a default connection).
crud = GenericCRUD('your_database')  # if you have a connection object, you can pass it as a second argument

# Insert a new record into a table.
data = {'name': 'John', 'age': 30, 'city': 'New York'}
crud.insert(table_name='my_table', data_dict=data)

# Select records from a table using column_name and column_value.
result = crud.select(table_name='my_table', select_clause_value="age, city", column_name="name",
                     column_value="John", limit=10)
print(result)  # (30, 'New York')

# Update records in a table using the where condition.
update_data = {'age': 31}
crud.update(table_name='my_table', data_dict=update_data, where="name='John'")

# Selecting all columns using the where condition.
result = crud.select(table_name='my_table', where="name='John'", limit=10)
print(result)  # age is now 31

# select one:
result = crud.select_one(table_name='my_table')

# Delete records from a table using the where condition.
crud.delete(table_name='my_table', where="name='John'")

crud.switch_db('your_database2')

# Close the connection when done.
crud.close()
```

# Why to use GenericCRUD?

To reduce duplicate code in all CRUD packages. Have a central location with logic i.e. automatically populate fields from
UserContext in the future.<br>

git submodule add https://github.com/circles-zone/sql2code-local-python-package sql2code


# Physical Delete is_test_data
Needs
-- To add is_test_data column
ALTER
CREATE VIEW
DELETE
-- To REPLACE VIEW
DROP



