# Keble-DB

A comprehensive database toolkit providing CRUD operations for MongoDB, SQL, and Qdrant databases with both synchronous and asynchronous support.

## Installation

```bash
pip install keble-db
```

## Key Features

- **CRUD Operations**: Complete Create, Read, Update, Delete operations for different databases
- **Dual API Support**: Both synchronous and asynchronous interfaces
- **Multiple Database Support**: MongoDB, SQL (SQLAlchemy/SQLModel), and Qdrant vector database
- **FastAPI Integration**: Specialized dependency injection utilities for FastAPI
- **Extended Redis Support**: Enhanced Redis functionality with namespace management and batch operations
- **Pydantic Integration**: Fully compatible with Pydantic v2 for data validation

## Schemas

The package provides essential schemas for database operations:

- **QueryBase**: Used throughout the package for creating consistent queries
- **ObjectId**: Custom ObjectId implementation for use with Pydantic (you cannot use bson.ObjectId directly in Pydantic)

```python
from keble_db.schemas import QueryBase, ObjectId

# Create a query with filters
# Note: filters and order_by vary by database type
query = QueryBase(
    filters={"name": "test"},  # MongoDB: dict with query operators, SQL: list of expressions, Qdrant: dict
    limit=10,
    offset=0,
    # Order by fields vary by database type:
    # MongoDB: list of tuples [(field_name, ASCENDING/DESCENDING)]
    # SQL: list of SQLAlchemy expressions
    # Qdrant: not applicable for vector similarity search
    order_by=[("created_at", -1)]  # MongoDB example
)

# Using ObjectId with Pydantic
from pydantic import BaseModel

class MyModel(BaseModel):
    id: ObjectId
    name: str
```

## QueryBase Implementation Details

The `QueryBase` class is used to build queries across different database types, but its fields have different expectations depending on the database type:

### MongoDB QueryBase

```python
from keble_db.schemas import QueryBase
from pymongo import ASCENDING, DESCENDING

# MongoDB uses dict for filters with MongoDB query operators
query = QueryBase(
    filters={"name": "John", "age": {"$gt": 18}},  # MongoDB query dict
    limit=10,
    offset=0,  # MongoDB requires int offset
    order_by=[("created_at", DESCENDING), ("name", ASCENDING)]  # List of (field, direction) tuples
)
```

### SQL QueryBase

```python
from keble_db.schemas import QueryBase
from sqlmodel import select
from mymodels import User  # Your SQLModel

# SQL uses list of SQLAlchemy expressions for filters
query = QueryBase(
    filters=[User.age > 18, User.name == "John"],  # List of SQLAlchemy expressions
    limit=10,
    offset=0,  # SQL requires int offset
    order_by=[User.created_at.desc(), User.name.asc()]  # List of SQLAlchemy expression objects
)
```

### Qdrant QueryBase

```python
from keble_db.schemas import QueryBase

# For Qdrant search operations (with int offset)
search_query = QueryBase(
    filters={"name": {"$eq": "Test Item"}},  # Qdrant filter dict
    limit=10,
    offset=0,  # For search: integer offset
    # order_by is not applicable for vector similarity search
)

# For Qdrant scroll operations (with string point_id as offset)
scroll_query = QueryBase(
    filters={"name": {"$eq": "Test Item"}},  # Qdrant filter dict
    limit=10,
    offset="some_point_id",  # For scroll: string point_id as offset
    # order_by is not applicable for vector similarity search
)
```

## Creating CRUD Classes

You can define custom CRUD classes by extending the base classes for each database type:

### MongoDB CRUD Class

```python
from pydantic import BaseModel
from keble_db.crud.mongo import MongoCRUDBase

# Define your model
class UserModel(BaseModel):
    name: str
    email: str
    age: int

# Define your CRUD class
class CRUDUser(MongoCRUDBase[UserModel]):
    # You can add custom methods here
    pass

# Initialize the CRUD instance
user_crud = CRUDUser(
    model=UserModel,
    collection="users",
    database="my_database"
)
```

### SQL CRUD Class

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from keble_db.crud.sql import SqlCRUDBase

# Define your model
class UserModel(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    email: str
    age: int

# Define your CRUD class
class CRUDUser(SqlCRUDBase[UserModel]):
    # You can add custom methods here
    pass

# Initialize the CRUD instance
user_crud = CRUDUser(
    model=UserModel,
    table_name="users"
)
```

### Qdrant CRUD Class

```python
from pydantic import BaseModel
from typing import List
from keble_db.crud.qdrant import QdrantCRUDBase

# Define your models
class VectorModel(BaseModel):
    vector: List[float]

class ItemModel(BaseModel):
    id: int
    name: str
    description: str

# Define your CRUD class
class CRUDItem(QdrantCRUDBase[ItemModel, VectorModel]):
    # You can add custom methods here
    pass

# Initialize the CRUD instance
item_crud = CRUDItem(
    model=ItemModel,
    vector_model=VectorModel,
    collection="items"
)
```

## Database Operations by Type

### MongoDB CRUD Operations

The MongoDB CRUD interface provides methods for working with MongoDB collections.

```python
from keble_db.crud.mongo import MongoCRUDBase
from pymongo import MongoClient, ASCENDING, DESCENDING
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from keble_db.schemas import QueryBase

# Define your model
class User(BaseModel):
    name: str
    email: str
    age: int

# Create a CRUD instance
user_crud = MongoCRUDBase(
    model=User,
    collection="users",
    database="my_database"
)

# Synchronous operations
mongo_client = MongoClient("mongodb://localhost:27017")

# Create a document
user = User(name="John", email="john@example.com", age=30)
# Returns pymongo.results.InsertOneResult
result = user_crud.create(mongo_client, obj_in=user)

# Read documents
# MongoDB QueryBase usage
query = QueryBase(
    filters={"name": "John"},  # MongoDB uses dict for filters with query operators
    limit=10,
    offset=0,
    order_by=[("created_at", DESCENDING)]  # List of (field, direction) tuples
)

# First returns a User model instance or None
user = user_crud.first(mongo_client, query=query)
# get_multi returns a list of User model instances
users = user_crud.get_multi(mongo_client, query=QueryBase(limit=10, offset=0))

# MongoDB _id is typically a bson.ObjectId
user_by_id = user_crud.first_by_id(mongo_client, _id="6463a8880f23dfd71c67c487")  # ObjectId as string

# Update a document
# Returns pymongo.results.UpdateResult
update_result = user_crud.update(mongo_client, _id="6463a8880f23dfd71c67c487", obj_in={"age": 31})

# Delete documents
# Returns pymongo.results.DeleteResult
delete_result = user_crud.delete(mongo_client, _id="6463a8880f23dfd71c67c487")
delete_multi_result = user_crud.delete_multi(mongo_client, query=QueryBase(filters={"age": {"$lt": 18}}))

# Asynchronous operations with motor client
async_mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")

# Create a document asynchronously
user = User(name="Jane", email="jane@example.com", age=28)
result = await user_crud.acreate(async_mongo_client, obj_in=user)

# Read documents asynchronously
user = await user_crud.afirst(async_mongo_client, query=QueryBase(filters={"name": "Jane"}))
users = await user_crud.aget_multi(async_mongo_client, query=QueryBase(limit=10, offset=0))
user_by_id = await user_crud.afirst_by_id(async_mongo_client, _id="6463a8880f23dfd71c67c487")

# Update a document asynchronously
update_result = await user_crud.aupdate(async_mongo_client, _id="6463a8880f23dfd71c67c487", obj_in={"age": 29})

# Delete documents asynchronously
delete_result = await user_crud.adelete(async_mongo_client, _id="6463a8880f23dfd71c67c487")
delete_multi_result = await user_crud.adelete_multi(async_mongo_client, query=QueryBase(filters={"age": {"$lt": 18}}))

# Aggregate operations (MongoDB specific)
from typing import List
class AggregationResult(BaseModel):
    _id: int
    count: int

aggregated_data = user_crud.aggregate(
    mongo_client,
    pipelines=[{"$group": {"_id": "$age", "count": {"$sum": 1}}}],
    model=AggregationResult
)

# Async aggregate operations (MongoDB specific)
aggregated_data = await user_crud.aaggregate(
    async_mongo_client,
    pipelines=[{"$group": {"_id": "$age", "count": {"$sum": 1}}}],
    model=AggregationResult
)
```

### SQL CRUD Operations

The SQL CRUD interface provides methods for working with SQL databases via SQLAlchemy/SQLModel.

```python
from keble_db.crud.sql import SqlCRUDBase
from sqlmodel import Session, create_engine, SQLModel, Field, select, col
from typing import Optional
from uuid import UUID, uuid4
from keble_db.schemas import QueryBase

# Define your model
class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    email: str
    age: int

# Create a CRUD instance
user_crud = SqlCRUDBase(
    model=User,
    table_name="users"
)

# Create a session
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)
session = Session(engine)

# Create a document
user = User(name="John", email="john@example.com", age=30)
# Returns the created User instance with populated id
created_user = user_crud.create(session, obj_in=user)

# Create multiple documents
users = [
    User(name="Alice", email="alice@example.com", age=25),
    User(name="Bob", email="bob@example.com", age=35),
]
# Returns a list of created User instances
created_users = user_crud.create_multi(session, obj_in_list=users)

# SQL QueryBase usage
query = QueryBase(
    # SQL uses list of SQLAlchemy expressions for filters
    filters=[User.age > 18, User.name == "John"],
    limit=10,
    offset=0,
    order_by=[User.created_at.desc()]  # List of SQLAlchemy expression objects
)

# Read documents
# Returns a User instance or None
user = user_crud.first(session, query=query)
# Returns a list of User instances
users = user_crud.get_multi(session, query=QueryBase(limit=10, offset=0))
# SQL _id is typically a UUID or int depending on your model
user_by_id = user_crud.first_by_id(session, _id=uuid4())

# Count documents
# Returns an integer
count = user_crud.count(session, query=QueryBase(filters=[User.age > 18]))

# Update a document
# Returns the updated User instance
updated_user = user_crud.update(session, _id=uuid4(), obj_in={"age": 31})

# Delete documents
# Returns None
user_crud.delete(session, _id=uuid4())
# Can delete by id or by object instances
user_crud.delete_multi(session, obj_in_list=[uuid4(), user1, user2])
```

### Qdrant Vector Database CRUD Operations

The Qdrant CRUD interface provides methods for working with Qdrant vector database.

```python
from keble_db.crud.qdrant import QdrantCRUDBase
from qdrant_client import QdrantClient, AsyncQdrantClient
from pydantic import BaseModel
from typing import List
from keble_db.schemas import QueryBase

# Define your models
class VectorModel(BaseModel):
    vector: List[float]

class Item(BaseModel):
    id: int
    name: str
    description: str

# Create a CRUD instance
item_crud = QdrantCRUDBase(
    model=Item,
    vector_model=VectorModel,
    collection="items"
)

# Synchronous operations
qdrant_client = QdrantClient("localhost", port=6333)

# Create an item with vector
vector = VectorModel(vector=[0.1, 0.2, 0.3])
item = Item(id=1, name="Test Item", description="This is a test item")
# Returns boolean (True if operation was successful)
result = item_crud.create(qdrant_client, vector, item, "unique_id_1")

# Create multiple items
items_and_vectors = [
    ("unique_id_2", Item(id=2, name="Item 2", description="Description 2"), VectorModel(vector=[0.4, 0.5, 0.6])),
    ("unique_id_3", Item(id=3, name="Item 3", description="Description 3"), VectorModel(vector=[0.7, 0.8, 0.9])),
]
# Returns boolean (True if operation was successful)
result = item_crud.create_multi(qdrant_client, payloads_and_vectors=items_and_vectors)

# Qdrant QueryBase usage
# order_by is not applicable for vector similarity search
query = QueryBase(
    filters={"name": {"$eq": "Test Item"}},  # Qdrant uses dict for filters
    limit=10,
    offset=0,  # For search: int offset
    # order_by is not applicable for Qdrant vector similarity search
)

# Read items
# Returns Item instance or None
item = item_crud.first_by_id(qdrant_client, _id="unique_id_1")
# Returns full Qdrant record (with vector and payload)
record = item_crud.first_record_by_id(qdrant_client, _id="unique_id_1")
# Returns list of Item instances
items = item_crud.get_multi_by_ids(qdrant_client, _ids=["unique_id_1", "unique_id_2"])
# Returns list of full Qdrant records
records = item_crud.get_multi_records_by_ids(qdrant_client, _ids=["unique_id_1", "unique_id_2"])

# Search by vector similarity
# Returns list of search results with scores
search_results = item_crud.search(
    qdrant_client,
    vector=[0.1, 0.2, 0.3],
    vector_key="vector",
    score_threshold=0.75
)

# Update items
# Returns boolean (True if operation was successful)
result = item_crud.update_payload(qdrant_client, _id="unique_id_1", payload=item)
result = item_crud.overwrite_payload(qdrant_client, _id="unique_id_1", payload=item)
result = item_crud.update_vector(qdrant_client, _id="unique_id_1", vector=vector)

# Delete items
# Returns boolean (True if operation was successful)
result = item_crud.delete(qdrant_client, _id="unique_id_1")
result = item_crud.delete_multi(qdrant_client, query=QueryBase(filters={"name": {"$eq": "Test Item"}}))

# Scroll through items with pagination using point_id
# Returns tuple of (list of items, next_point_id)
items, next_point_id = item_crud.scroll(
    qdrant_client,
    query=QueryBase(
        filters={"name": {"$eq": "Test Item"}},
        limit=10,
        offset=None  # First page has None offset, subsequent pages use the returned next_point_id
    )
)
# Using the next_point_id for the next page
if next_point_id:
    next_page_items, next_point_id = item_crud.scroll(
        qdrant_client,
        query=QueryBase(
            filters={"name": {"$eq": "Test Item"}},
            limit=10,
            offset=next_point_id  # Use the point_id as string offset
        )
    )

# Asynchronous operations
async_qdrant_client = AsyncQdrantClient("localhost", port=6333)

# Create an item asynchronously
result = await item_crud.acreate(async_qdrant_client, vector, item, "unique_id_4")

# Read items asynchronously
item = await item_crud.afirst_by_id(async_qdrant_client, _id="unique_id_4")
items = await item_crud.aget_multi_by_ids(async_qdrant_client, _ids=["unique_id_4"])

# Search asynchronously
search_results = await item_crud.asearch(
    async_qdrant_client,
    vector=[0.1, 0.2, 0.3],
    vector_key="vector",
    score_threshold=0.75
)

# Update items asynchronously
await item_crud.aupdate_payload(async_qdrant_client, _id="unique_id_4", payload=item)
await item_crud.aoverwrite_payload(async_qdrant_client, _id="unique_id_4", payload=item)
await item_crud.aupdate_vector(async_qdrant_client, _id="unique_id_4", vector=vector)

# Delete items asynchronously
await item_crud.adelete(async_qdrant_client, _id="unique_id_4")
await item_crud.adelete_multi(async_qdrant_client, query=QueryBase(filters={"name": {"$eq": "Test Item"}}))

# Scroll items asynchronously
items, next_point_id = await item_crud.ascroll(
    async_qdrant_client,
    query=QueryBase(
        filters={"name": {"$eq": "Test Item"}},
        limit=10
    )
)
```

## Database Session Management

The `session` module provides tools for managing database connections in API services. It handles the creation and management of database sessions, which should be handled at the API endpoint level.

```python
from keble_db import DbSettingsABC
from pydantic_settings import BaseSettings
from fastapi import FastAPI, Depends

# 1. Define settings class implementing the DbSettingsABC interface
class Settings(BaseSettings, DbSettingsABC):
    # Implement required settings for database connections
    mongodb_uri: str
    sql_uri: str
    redis_url: str
    # ... other settings
    
# 2. Initialize settings
settings = Settings()

# 3. Initialize database and dependency objects
from keble_db.session import Db, ApiDbDeps

# Initialize the core database handler
db = Db(settings)

# Example of db usage
mongo_client = db.get_mongo()
redis_client = db.get_redis(namespace="my-app")
sql_session = db.get_sql_write_client()

# Initialize the API dependencies handler
api_db_deps = ApiDbDeps(db)

# 4. Use in FastAPI application
app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: str, mongo_client = Depends(api_db_deps.get_amongo)):
    # Use the mongo client to access the database
    user = await user_crud.afirst_by_id(mongo_client, _id=user_id)
    return user

@app.get("/products")
async def get_products(sql_session = Depends(api_db_deps.get_sql)):
    # Use SQL session
    products = product_crud.get_multi(sql_session, query=QueryBase(limit=10))
    return products

@app.get("/cache")
async def get_cache(redis_client = Depends(api_db_deps.get_redis)):
    # Use Redis client
    cached_data = redis_client.get("some_key")
    return {"data": cached_data}
```

## Extended Redis Support

The package provides extended Redis functionality with namespace management and batch operations.

```python
from keble_db.wrapper import ExtendedRedis
from redis import Redis

redis_client = Redis(host="localhost", port=6379)
# The ExtendedRedis act like redis.asyncio.Redis,
# which it DOES NOT have an "a" in front of the api,
# but all apis are awaitable
extended_redis = ExtendedRedis(redis_client, namespace="my-app")

# Set with namespace
await extended_redis.set("user:1", "data")  # Actual key: "my-app:user:1"

# Get with namespace
data = await extended_redis.get("user:1")

# Delete all keys in a namespace
await extended_redis.delete_keys_by_pattern("user:*")  # Deletes all "my-app:user:*" keys
```

