#Here we explore random numbers in Python
#Random numbers are used for games, simulations, testing, security, and privacy applications.
#Python has a built-in module called random that can be used to make random numbers.
#Let's look at some examples.
#This is how you import a module.
import random
#This is how you generate a random number between 0 and 1.
print(random.random())
#This is how you generate a random number between 1 and 10.
print(random.randint(1, 10))

#You can use random numbers to make a random choice from a list.
my_list = ["apple", "banana", "cherry"]
print(random.choice(my_list))

#We can use random numbers to make a random choice from a string.
#Strings can have special characters.
def return_random_character():
    special_characters = "!@#$%^&+" #This is a string of special characters.
    random_character = random.choice(special_characters)
    return random_character + " "

#create a function to create a series of random characters
def generate_random_ASCII(size):
    for j in range(size):
        print(return_random_character(), end="")


if __name__ == "__main__":
    generate_random_ASCII(10)

