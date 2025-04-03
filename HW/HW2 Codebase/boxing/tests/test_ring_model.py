from dataclasses import asdict

import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

@pytest.fixture
def ring_model():
    """Fixture to create a RingModel instance for testing."""
    return RingModel()

@pytest.fixture
def mock_update_boxer_stats(mocker):
    """Fixture to mock the update_boxer_stats function."""
    return mocker.patch("boxing.models.ring_model.update_boxer_stats")

@pytest.fixture
def boxer_1():
    """Fixture to create a Boxer instance for testing."""
    return Boxer(id = 1, name="Boxer 1", weight=150, height=70, reach=9.0, age=25)

@pytest.fixture
def boxer_2():
    """Fixture to create another Boxer instance for testing."""
    return Boxer(id = 2, name="Boxer 2", weight=160, height=72, reach=9.5, age=30)

def test_enter_ring(ring_model, boxer_1, boxer_2):
    """Test entering the ring with two boxers."""
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)

    assert len(ring_model.ring) == 2
    assert boxer_1 in ring_model.ring
    assert boxer_2 in ring_model.ring

def test_enter_ring_with_same_boxer(ring_model, boxer_1):
    """Test entering the ring with the same boxer twice."""
    ring_model.enter_ring(boxer_1)
    with pytest.raises(ValueError, match="Boxer already in the ring."):
        ring_model.enter_ring(boxer_1)


def test_enter_ring_with_invalid_boxer(ring_model):
    """Test entering the ring with an invalid boxer."""
    invalid_boxer = "Not a Boxer"
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer', got 'str'"):
        ring_model.enter_ring(invalid_boxer)

def test_enter_ring_full(ring_model, boxer_1, boxer_2):
    """Test entering the ring when it is already full."""
    boxer_3 = Boxer(id = 3, name="Boxer 3", weight=170, height=74, reach=10.0, age=28)

    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)

    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(boxer_3)

def test_clear_ring(ring_model, boxer_1, boxer_2):
    """Test clearing the ring."""
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)

    assert len(ring_model.ring) == 2

    ring_model.clear_ring()

    assert len(ring_model.ring) == 0, "Ring should be empty after clearing."

def test_get_boxers(ring_model, boxer_1, boxer_2):
    """Test getting boxers from the ring."""
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)

    boxers = ring_model.get_boxers()

    assert len(boxers) == 2
    assert boxer_1 in boxers
    assert boxer_2 in boxers

def test_get_boxers_empty_ring(ring_model):
    """Test getting boxers from an empty ring."""
    with pytest.raises(ValueError, match="No boxers in the ring."):
        ring_model.get_boxers()

def test_get_fighting_skill(ring_model, boxer_1):
    """Test getting the fighting skill of a boxer."""
    skill = ring_model.get_fighting_skill(boxer_1)

    assert isinstance(skill, float), "Fighting skill should be a float."
    assert skill > 0, "Fighting skill should be greater than 0."

def test_get_fighting_skill_invalid_boxer(ring_model):
    """Test getting the fighting skill of an invalid boxer."""
    invalid_boxer = "Not a Boxer"
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer', got 'str'"):
        ring_model.get_fighting_skill(invalid_boxer)

def test_fight_with_not_enough_boxers(ring_model, boxer_1):
    """Test fighting with not enough boxers in the ring."""
    ring_model.enter_ring(boxer_1)

    with pytest.raises(ValueError, match="Not enough boxers in the ring to start a fight."):
        ring_model.fight()

def test_fight_empty_ring(ring_model):
    """Test fighting in an empty ring."""
    with pytest.raises(ValueError, match="Not enough boxers in the ring to start a fight."):
        ring_model.fight()




