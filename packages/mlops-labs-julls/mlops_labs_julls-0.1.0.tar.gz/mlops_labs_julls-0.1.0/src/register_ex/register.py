import re 
import math

def is_valid_username(username):
    
    return bool(username) and " " not in username

def is_valid_email(email):

    return "@" in email and "." in email

def is_valid_password(password):

    if len(password) < 8:
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def register_user():

    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")

    if not is_valid_username(username):
        return "Invalid username"
    if not is_valid_email(email):
        return "Invalid email"
    if not is_valid_password(password):
        return "Invalid password"

    return "Registration successful"

def is_prime(number):
    if number < 2:
        return False
    for n in range(2, math.floor(math.sqrt(number) + 1)): 
        if number % n == 0:
            return False
    return True

def input_is_prime():
    number = input("number to check if prime: ")

    if is_prime(number) is True:
        return "It is a prime number"

    else:
        return "It is not a prime number"

if __name__ == "__main__":
    print(register_user())