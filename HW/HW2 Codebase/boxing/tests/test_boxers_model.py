import pytest
import sqlite3
import re

from contextlib import contextmanager

from boxing.models.boxers_model import (
    get_boxer_by_id, get_leaderboard, get_boxer_by_name,
    get_weight_class, create_boxer, update_boxer_stats,
    delete_boxer, Boxer
)


def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

def test_create_boxer(mock_cursor):
    """Test creating a boxer in the database.

    """
    create_boxer(name="John Doe", weight=180, height=75, reach=10.0, age=30)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers(name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("John Doe", 180, 75, 10.0, 30)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def create_boxer_invalid_weight(mock_cursor):
    """Test creating a boxer with invalid weight.

    """
    with pytest.raises(ValueError, match="Invalid weight: -180. Must be at least 125."):
        create_boxer(id = 1, name="John Doe", weight=-180, height=75, reach=10.0, age=30)

def create_boxer_invalid_height(mock_cursor):
    """Test creating a boxer with invalid height.

    """
    with pytest.raises(ValueError, match="Invalid height: -75. Must be at least 60."):
        create_boxer(id = 1, name="John Doe", weight=180, height=-75, reach=10.0, age=30)

def create_boxer_invalid_reach(mock_cursor):    
    """Test creating a boxer with invalid reach.

    """
    with pytest.raises(ValueError, match="Invalid reach: -10.0. Must be at least 10.0."):
        create_boxer(id = 1, name="John Doe", weight=180, height=75, reach=-10.0, age=30)

def create_boxer_invalid_age(mock_cursor):  
    """Test creating a boxer with invalid age.

    """
    with pytest.raises(ValueError, match="Invalid age: -30. Must be at least 18."):
        create_boxer(id = 1, name="John Doe", weight=180, height=75, reach=10.0, age=-30)

def create_boxer_invalid_name(mock_cursor):  
    """Test creating a boxer with invalid name.

    """
    with pytest.raises(TypeError, match="Invalid name: 3. Must be a string."):
        create_boxer(id = 1, name=3, weight=180, height=75, reach=10.0, age=30)

def create_boxer_duplicate_name(mock_cursor):
    """Test creating a boxer with a duplicate name.

    """
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.fetchone.return_value= (1,)

    with pytest.raises(ValueError, match="Boxer with name 'John Doe' already exists."):
        create_boxer(id = 1, name="John Doe", weight=180, height=75, reach=10.0, age=30)

def test_delete_boxer(mock_cursor):
    """Test deleting a boxer from the database.

    """


    mock_cursor.fetchone.return_value = (1, "John Doe", 180, 75, 10.0, 30)
    delete_boxer(1)

    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_delete_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The UPDATE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."

def test_delete_boxer_not_found(mock_cursor):
    """Test deleting a boxer that does not exist.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 99 not found."):
        delete_boxer(99)

def test_get_boxer_by_id(mock_cursor):
    """Test retrieving a boxer by ID.

    """
    mock_cursor.fetchone.return_value = (1, "John Doe", 180, 75, 10.0, 30)

    result = get_boxer_by_id(1)

    expected_result = Boxer(id=1, name="John Doe", weight=180, height=75, reach=10.0, age=30)
    assert result == expected_result, f"Expected {expected_result}, but got {result}"

    expected_query = normalize_whitespace("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    actual_args = mock_cursor.execute.call_args[0][1]
    expected_args = (1,)

    assert actual_args == expected_args, f"The SQL query arguments did not match. Expected {expected_args}, got {actual_args}."

def test_get_boxer_by_id_not_found(mock_cursor):
    """Test retrieving a boxer by ID when the boxer does not exist.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 99 not found."):
        get_boxer_by_id(99)

def test_get_boxer_by_bad_id(mock_cursor):
    """Test retrieving a boxer by ID when the ID is invalid.

    """
    with pytest.raises(TypeError, match="Invalid type: Expected 'int', got 'str'"):
        get_boxer_by_id("abc")

def test_get_boxer_by_name(mock_cursor):
    """Test retrieving a boxer by name.

    """
    mock_cursor.fetchone.return_value = (1, "John Doe", 180, 75, 10.0, 30)

    result = get_boxer_by_name("John Doe")

    expected_result = Boxer(id=1, name="John Doe", weight=180, height=75, reach=10.0, age=30)
    assert result == expected_result, f"Expected {expected_result}, but got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    actual_args = mock_cursor.execute.call_args[0][1]
    expected_args = ("John Doe",)

    assert actual_args == expected_args, f"The SQL query arguments did not match. Expected {expected_args}, got {actual_args}."

def test_get_boxer_by_name_not_found(mock_cursor):
    """Test retrieving a boxer by name when the boxer does not exist.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer 'John Doe' not found."):
        get_boxer_by_name("John Doe")

def test_get_boxer_by_name_bad_name(mock_cursor):
    """Test retrieving a boxer by name when the name is invalid.

    """
    with pytest.raises(TypeError, match="Invalid type: Expected 'str', got 'int'"):
        get_boxer_by_name(123)

def test_get_leaderboard(mock_cursor):
    """Test retrieving the leaderboard.

    """
    mock_cursor.fetchall.return_value = [
        (1, "John Doe", 180, 75, 10.0, 30, 5, 3, 0.6),
        (2, "Jane Smith", 150, 65, 8.0, 28, 10, 8, 0.8)
    ]

    result = get_leaderboard()

    assert len(result) == 2, "Expected 2 boxers in the leaderboard."
    assert result[0]['name'] == "John Doe", "Expected first boxer to be John Doe."

def test_get_weight_class(mock_cursor):
    """Test retrieving the weight class of a boxer.

    """
    mock_cursor.fetchone.return_value = ("MIDDLEWEIGHT",)

    result = get_weight_class(200)
    expected_result = "MIDDLEWEIGHT"
    assert result == expected_result, f"Expected {expected_result}, but got {result}"

def test_get_weight_class_invalid_weight(mock_cursor):
    """Test retrieving the weight class with an invalid weight.

    """
    with pytest.raises(ValueError, match="Invalid weight: -200. Weight must be at least 125."):
        get_weight_class(-200)

def test_get_weight_class_invalid_type(mock_cursor):
    """Test retrieving the weight class with an invalid type.

    """
    with pytest.raises(TypeError, match="Invalid type: Expected 'int', got 'str'"):
        get_weight_class("abc")


def test_update_boxer_stats_invalid_result(mock_cursor):
    """Test updating the stats of a boxer with an invalid result.

    """
    with pytest.raises(ValueError, match="Invalid result: invalid. Expected 'win' or 'loss'."):
        update_boxer_stats(1, 'invalid')

def test_update_boxer_stats_invalid_id(mock_cursor):
    """Test updating the stats of a boxer with an invalid ID.

    """
    with pytest.raises(TypeError, match="Invalid type: Expected 'int', got 'str'"):
        update_boxer_stats("abc", 'win')

def test_update_boxer_stats_not_found(mock_cursor):
    """Test updating the stats of a boxer that does not exist.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 99 not found."):
        update_boxer_stats(99, 'win')

