import pytest
from unittest.mock import patch, MagicMock

from kuhl_haus.canary.handlers import script_handler
from kuhl_haus.canary.scripts.canary import Canary
from kuhl_haus.canary.scripts.script import Script


@pytest.fixture
def mock_canary():
    """Fixture to mock the Canary class import."""
    mock = MagicMock()
    return mock


def test_script_handler_returns_correct_handler_for_valid_script():
    """Test that script_handler returns the correct handler for a valid script name."""
    # Arrange
    script_name = "canary"

    # Act
    sut = script_handler(script_name)

    # Assert
    assert issubclass(sut, Script)
    assert issubclass(sut, Canary)


def test_script_handler_raises_value_error_for_invalid_script():
    """Test that script_handler raises ValueError for an invalid script name."""
    # Arrange
    invalid_script_name = "invalid_script"

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        script_handler(invalid_script_name)

    assert invalid_script_name in str(excinfo.value)


def test_script_handler_with_empty_string():
    """Test that script_handler handles empty string input correctly."""
    # Arrange
    empty_script_name = ""
    expected_error_message = f"No handler for script {empty_script_name}"

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        script_handler(empty_script_name)

    assert str(excinfo.value) == expected_error_message


@pytest.mark.parametrize("invalid_input", [None, 123])
def test_script_handler_with_invalid_input_values(invalid_input):
    """Test that script_handler handles invalid input values appropriately."""
    # Arrange & Act & Assert
    with pytest.raises(ValueError):
        script_handler(invalid_input)


@pytest.mark.parametrize("invalid_input", [[], {}])
def test_script_handler_with_invalid_input_types(invalid_input):
    """Test that script_handler handles invalid input types appropriately."""
    # Arrange & Act & Assert
    with pytest.raises(TypeError):
        script_handler(invalid_input)


def test_script_handler_case_sensitivity():
    """Test that script_handler is case-sensitive."""
    # Arrange
    script_name = "Canary"  # Capitalized

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        script_handler(script_name)

    assert script_name in str(excinfo.value)
