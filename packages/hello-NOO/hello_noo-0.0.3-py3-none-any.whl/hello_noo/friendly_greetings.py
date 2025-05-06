
from . import greetings

def greet_with_name(greeting, name):
    print(greeting +',', name+'!')


if __name__ == "__main__":
    greet_with_name("Welcome", "Python")
    greet_with_name(greetings.hi(), "Python")
