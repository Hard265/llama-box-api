import pytest
from pydantic import ValidationError
from app.models.user import User

def test_valid_user_creation():
    """Test creating a user with valid data"""
    user = User(
        id="user123",
        email="test@example.com",
        is_active=True
    )
    
    assert user.id == "user123"
    assert user.email == "test@example.com"
    assert user.is_active is True

def test_default_is_active():
    """Test is_active defaults to True when not provided"""
    user = User(
        id="user123",
        email="test@example.com"
    )
    
    assert user.is_active is True

def test_invalid_email_raises_error():
    """Test invalid email raises validation error"""
    with pytest.raises(ValidationError):
        User(
            id="user123",
            email="invalid-email",
            is_active=True
        )

def test_missing_required_fields():
    """Test missing required fields raise errors"""
    with pytest.raises(ValidationError):  # Missing email
        User(id="user123", is_active=True)
        
    with pytest.raises(ValidationError):  # Missing id
        User(email="test@example.com", is_active=True)
