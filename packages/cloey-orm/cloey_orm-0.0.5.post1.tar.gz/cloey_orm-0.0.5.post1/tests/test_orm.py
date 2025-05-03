import pytest
import os
import sqlite3
from cloey.database import SQLiteConnection, PostgreSQLConnection
from cloey.orm import BaseModel
from models import User


# Set up test database connection
@pytest.fixture(scope='module')
def setup_db():
    """Setup the database for testing."""
    if os.path.exists("test_database.db"):
        os.remove("test_database.db")

    # BaseModel.set_connection(SQLiteConnection("test_database.db"))

    BaseModel.set_connection(PostgreSQLConnection(
        database="cloey",
        user="cloey",
        password="secret",
        host="localhost",
        port=5432
    ))
    
    with BaseModel.get_connection() as conn:
        User.create_table()
        yield conn


# Test cases
def test_insert_user(setup_db):
    """Test inserting and finding a user."""
    conn = setup_db

    global user
    user = User.create(name="Jane Doe", email="jane.doe@example.com")
    assert user is not None
    assert type(user) is User
    assert user.id is not None
    assert user.name == "Jane Doe"
    assert user.email == "jane.doe@example.com"

def test_find_user(setup_db):
    """Test inserting and finding a user."""
    conn = setup_db
    _user = User.find(id=user.id)

    assert _user is not None
    assert _user.id == user.id
    assert _user.name == user.name
    assert _user.email == user.email

def test_update_user(setup_db):
    """Test updating a user's email."""
    conn = setup_db

    # Insert a user
    User.create(name="Alice", email="alice@example.com")

    # Update the user's email
    User.update(data={"email": "alice.new@example.com"}, name="Alice")

    # Verify the update
    user = User.find(name="Alice")
    assert user is not None
    assert user.email == "alice.new@example.com"

def test_delete_user(setup_db):
    """Test deleting a user."""
    conn = setup_db

    # Insert a user
    User.create(name="Bob", email="bob@example.com")

    # Delete the user
    User.delete(name="Bob")

    # Verify the deletion
    user = User.find(name="Bob")
    assert user is None

def test_all_users(setup_db):
    """Test retrieving all users."""
    conn = setup_db

    # Insert multiple users
    User.create(name="Charlie", email="charlie@example.com")
    User.create(name="Dana", email="dana@example.com")

    # Retrieve all users
    users = User.all()
    assert len(users) >= 2
    names = {user.name for user in users}
    assert "Charlie" in names
    assert "Dana" in names

def test_not_explicit_tablename(setup_db):
    """Test tablename when when __tablename__ not provided"""
    conn = setup_db
    cursor = conn.cursor()

    class Test(BaseModel):
        name: str
        age: int
  
    Test.create_table()  
    query = """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE' 
        AND table_name = 'tests';""" if Test._get_conn_type() == 'psycopg2.extensions' else "SELECT name FROM sqlite_master WHERE type='table' AND name='tests'"
    cursor.execute(query)
    
    table = cursor.fetchone()
    

    assert table is not None, "The 'tests' table does not exist in the database"
    assert table[0] == 'tests', "Table name does not match 'tests'"

def test_explicit_tablename(setup_db):
    """Test tablename when __tablename__ is provided"""
    conn = setup_db
    cursor = conn.cursor()

    class Test(BaseModel):
        __tablename__ = "unit_tests"
        name: str
        age: int
    
    Test.create_table()  
    query = """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE' 
        AND table_name = 'unit_tests';""" if Test._get_conn_type() == 'psycopg2.extensions' else "SELECT name FROM sqlite_master WHERE type='table' AND name='unit_tests'"
    cursor.execute(query)
    
    table = cursor.fetchone()
    

    assert table is not None, "The 'tests' table does not exist in the database"
    assert table[0] == 'unit_tests', "Table name does not match 'tests'"

def test_migrations(setup_db):
    """Test generating and applying migrations."""
    conn = setup_db

    # Generate a migration script
    User.generate_and_save_migration()

    # Apply pending migrations
    User.apply_pending_migrations()


if __name__ == "__main__":
    pytest.main()
