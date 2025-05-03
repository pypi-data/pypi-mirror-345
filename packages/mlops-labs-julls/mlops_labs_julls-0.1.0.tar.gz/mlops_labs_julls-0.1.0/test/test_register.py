import pytest

#import sys
#sys.path += ['/Users/julianlilas/Desktop/MLOps/mlops_labs/src/mlops_labs/register_ex']
#from register import *

from register_ex.register import *

def test_valid_username():
    assert is_valid_username("julien") is True
    assert is_valid_username("") is False
    assert is_valid_username("john doe") is False 

def test_valid_email():
    assert is_valid_email("test@example.com") is True
    assert is_valid_email("noatsign.com") is False
    assert is_valid_email("missing@dot") is False

def test_valid_password():
    assert is_valid_password("Azerty12!") is True
    assert is_valid_password("short1!") is False
    assert is_valid_password("longbutnopunctua123") is False
    assert is_valid_password("!@#$%^&*()") is False

def test_register_user_valid(monkeypatch):
    inputs = iter([
        "validuser",               # username
        "valid@email.com",         # email
        "Strongpass123!"           # password
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    assert register_user() == "Registration successful"

def test_register_user_invalid_username(monkeypatch):
    inputs = iter([
        "",                        
        "valid@email.com",
        "Strongpass123!"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    assert register_user() == "Invalid username"

def test_is_prime(monkeypatch):
    inputs = iter([2,3,5,23])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    assert input_is_prime() == "It is a prime number"

def test_is_not_prime(monkeypatch):
    inputs = iter([4,6,8,9,10])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    assert input_is_prime() == "It is not a prime number"

def test_is_prime():   
    assert is_prime(3) is True
    assert is_prime(4) is False
    assert is_prime(15) is False
    assert is_prime(23) is True