import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class to manage a ring for a fight.

    Attributes:
        ring (List[Boxer]): A list of boxers currently in the ring.

    """
    def __init__(self):
        """Initializes the ring with an empty list of boxers.
        
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Simulates a fight in the ring and determines the outcome.

        Returns:
            str: the outcome of the fight for each boxer attached to their name.

        Raises:
            ValueError: If there are not enough boxers in the ring to start a fight.

        """
        if len(self.ring) < 2:
            logger.error("Not enough boxers in the ring to start a fight.")
            raise ValueError("Not enough boxers in the ring to start a fight.")
        
        if len(self.ring) > 2:
            logger.error("There are too many boxers in the ring.")
            raise ValueError("There are too many boxers in the ring.")
        
        logger.info("Starting a fight between two boxers.")

        boxer_1, boxer_2 = self.get_boxers()

        if boxer_1 == boxer_2:
            logger.error("Both boxers are the same.")
            raise ValueError("Both boxers are the same.")
        
        if not isinstance(boxer_1, Boxer) or not isinstance(boxer_2, Boxer):
            logger.error("Invalid type: boxer is not a valid Boxer instance.")
            raise TypeError("Invalid type: boxer is not a valid Boxer instance.")
        
        if not boxer_1 or not boxer_2:
            logger.error("Boxer 1 or Boxer 2 is None.")
            raise ValueError("Boxer 1 or Boxer 2 is None.")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()
        
        logger.info(f"Fight finished. Winner: {winner.name}, Loser: {loser.name}")

        return winner.name

    def clear_ring(self):
        """Clears all boxers from the ring.

        Clears all songs from the playlist.

        """

        logger.info("Received request to clear the ring.")

        if not self.ring:
            logger.warning("Ring is already empty.")
            return
        
        self.ring.clear()
        logger.info("Ring cleared successfully.")

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to be added to the ring.

        Raises:
            TypeError: If the boxer is not a valid Boxer instance.
            ValueError: If the ring is full or the boxer is already in the ring.

        """
        logger.info("Received request to add a boxer to the ring.")


        if not isinstance(boxer, Boxer):
            logger.error("Invalid type: boxer is not a valid Boxer instance.")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error("Ring is full, cannot add more boxers.")
            raise ValueError("Ring is full, cannot add more boxers.")
        
        if boxer in self.ring:
            logger.error("Boxer already in the ring.")
            raise ValueError("Boxer already in the ring.")

        self.ring.append(boxer)
        logger.info(f"Boxer '{boxer.name}' added to the ring.")

    def get_boxers(self) -> List[Boxer]:
        """Returns a list of boxers in the ring.

        Returns:
            List[Boxer]: A list of boxers currently in the ring.

        """
        logger.info("retrieving boxers in the ring.")

        if not self.ring:
            logger.warning("No boxers in the ring.")
            raise ValueError("No boxers in the ring.")
        else:
            logger.info("Boxers retrieved successfully.")

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Returns the fighting skill of a specified boxer.

        Args:
            boxer (Boxer): The boxer whose skill is to be calculated.

        Returns:
            float: The calculated fighting skill of the boxer.

        Raises:
            TypeError: If the boxer is not a valid Boxer instance.

        """

        if not isinstance(boxer, Boxer):
            logger.error("Invalid type: boxer is not a valid Boxer instance.")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        logger.info(f"Calculating fighting skill for boxer: {boxer.name}")
        
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        if skill < 0:
            logger.warning(f"Fighting skill for boxer {boxer.name} is negative, setting to 0.")
            skill = 0

        logger.info(f"Successfully retrieved fighting skill for boxer {boxer.name}: {skill}")
        return skill
