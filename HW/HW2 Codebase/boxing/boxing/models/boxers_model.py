from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:

    """
    A class to manage a playlist of songs.

    Attributes:
        id (int): The id number of the boxer.
        name (str): The name of the boxer.
        weight (int): The weight of the boxer.
        height (int): The height of the boxer.
        reach (float): The reach of the boxer.
        age (int): The age of the boxer.
        weight_class (str): The weight class of the boxer.

    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
      
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class



def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Adds a boxer.

    Args:
        name (str): The name of the boxer to be added.
        weight (int): The weight of the boxer to be added.
        height (int): The height of the boxer to be added.
        reach (float): The reach of the boxer to be added.
        age (int): The age of the boxer to be added.

    Raises:
        ValueError: If qny field is invalid.
        TypeError: If the name is not of the expected type.
        sqlite3.IntegrityError: If the boxer already exists.
        sqlite3.Error: If there is an error with the database.

    """
    logger.info(f"received request to add boxer: {name}, weight: {weight}, height: {height}, reach: {reach}, age: {age}")

    if not isinstance(name, str) or not name.strip():
        logger.warning(f"Invalid name provided: {name}.")
        raise TypeError(f"Invalid name: {name}. Must be a string.")
    if not isinstance(weight, int) or weight < 125:
        logger.warning(f"Invalid weight provided: {weight}.")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if not isinstance(height, int) or height <= 0:
        logger.warning(f"Invalid height provided: {height}.")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if not isinstance(reach, float) or reach <= 0:
        logger.warning(f"Invalid reach provided: {reach}.")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not isinstance(age, int) or not (18 <= age <= 40):
        logger.warning(f"Invalid age provided: {age}.")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.error(f"Boxer with name '{name}' already exists.")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()
            logger.info(f"Boxer '{name}' added successfully.")

    except sqlite3.IntegrityError:
        logger.error(f"Boxer with name '{name}' already exists.")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"Database error occurred: {e}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer.

        Args:
            boxer_id (int): The ID of the boxer to remove.

        Raises:
            ValueError: If the boxer id is not found.
            TypeError: If the boxer_id is not an integer.
            sqlite3.Error: If there is an error with the database.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if not isinstance(boxer_id, int):
                logger.error(f"Invalid type: boxer_id is not an integer.")
                raise TypeError(f"Invalid type: Expected 'int', got '{type(boxer_id).__name__}'")

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

            logger.info(f"Boxer with ID {boxer_id} deleted successfully.")

    except sqlite3.Error as e:
        logger.error(f"Database error occurred: {e}")
        raise e
    


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Returns a leaderboard of all boxers sorted by wins.

    Args:
        sort_by (str): The field to sort by. Can be 'wins' or 'win_pct'.
            Defaults to 'wins'.

    Returns:
        List[dict[str, Any]]: A list of all boxers and their info sorted by wins.

    Raises:
        ValueError: If the sorting parameter is invalid.
        sqlite3.Error: If there is an error with the database.

    """
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error(f"Invalid sort_by parameter: {sort_by}")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve leaderboard data.")
            cursor.execute(query)
            rows = cursor.fetchall()

        if not rows:
            logger.info("No boxers found in the database.")
            return []

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)

        logger.info("Leaderboard data retrieved successfully.")
        return leaderboard
    

    except sqlite3.Error as e:
        logger.error(f"Database error occurred: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Retrieves a boxer by their boxer ID.

    Args:
        boxer_id (int): The ID of the boxer to retrieve.

    Returns:
        Boxer: The boxer with the specified ID.

    Raises:
        ValueError: If the boxer is not found.
        TypeError: If the boxer_id is not an integer.
        sqlite3.Error: If there is an error with the database.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if not isinstance(boxer_id, int):
                logger.error(f"Invalid type: boxer_id is not an integer.")
                raise TypeError(f"Invalid type: Expected 'int', got '{type(boxer_id).__name__}'")

            logger.info(f"Attempting to retrieve boxer with ID: {boxer_id}")
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Boxer with ID {boxer_id} retrieved successfully.")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.info(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error occurred while retrieving song by id {boxer_id}: {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieves a boxer by their name.

    Args:
        boxer_name (str): The name of the boxer to retrieve.

    Returns:
        Boxer: The boxer with the specified name.

    Raises:
        ValueError: If the boxer is not found.
        TypeError: If the boxer_name is not a valid string.
        sqlite3.Error: If there is an error with the database.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if not isinstance(boxer_name, str) or not boxer_name.strip():
                logger.error(f"Invalid type: boxer_name is not a valid string.")
                raise TypeError(f"Invalid type: Expected 'str', got '{type(boxer_name).__name__}'")
            

            logger.info(f"Attempting to retrieve boxer with name: {boxer_name}")
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Boxer with name {boxer_name} retrieved successfully.")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.info(f"Boxer with name {boxer_name} not found.")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error occurred while retrieving boxer by name {boxer_name}: {e}")
        raise e


def get_weight_class(weight: int) -> str:
    """Returns the weight class of a specified weight.

    Returns:
        str: The weight class assigned.

    Raises:
        ValueError: If the weight is less than 125.
        TypeError: If the weight is not an integer.

    """

    if not isinstance(weight, int):
        logger.error(f"Invalid type: weight is not an integer.")
        raise TypeError(f"Invalid type: Expected 'int', got '{type(weight).__name__}'")

    logger.info(f"Calculating weight class for weight: {weight}")

    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid weight provided: {weight}.")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")
    
    logger.info(f"Weight class calculated: {weight_class}")

    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Updates the stats of a boxer after a fight.

    Args:
        boxer_id (int): The ID of the boxer to update.
        result (str): The result of the fight ('win' or 'loss').

    Raises:
        ValueError: If the boxer ID is not found or if the result is invalid.
        TypeError: If the boxer_id is not an integer.
        sqlite3.Error: If there is an error with the database.

    """
    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result provided: {result}.")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")
    
    if not isinstance(boxer_id, int):
        logger.error(f"Invalid type: boxer_id is not an integer.")
        raise TypeError(f"Invalid type: Expected 'int', got '{type(boxer_id).__name__}'")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to update stats for boxer ID {boxer_id} with result: {result}")

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Boxer ID {boxer_id} stats updated successfully.")

    except sqlite3.Error as e:
        logger.error(f"Database error occurred while updating stats for boxer ID {boxer_id}: {e}")
        raise e
