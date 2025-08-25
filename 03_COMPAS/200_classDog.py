
class Dog:

    def __init__(self, name, color='white'):
        self.name = name
        self.color = color
        self.tricks = []    # creates a new empty list for each dog

    def add_trick(self, trick):
        self.tricks.append(trick)
    
    def bark(self):
        print('woof woof')



dog1 = Dog('Fido', 'brown')
dog2 = Dog('Buddy')

dog1.add_trick('roll over')
dog1.add_trick('cath frisbee')
dog1.bark()

dog2.add_trick('play dead')



print(dog1.tricks)
print(dog1.name)
print(dog1.color)
print(dog2.color)



###################################self############################################

class MyClass:
    def __init__(self, name):
        self.name = name  # `self` refers to the current object

    def say_hello(self):
        print(f"Hello, my name is {self.name}")  # Using `self` to access the object's attribute

# Creating an instance of MyClass
obj = MyClass("Alice")
obj1 = MyClass("Bob")
print (obj.name)

# Calling the method
obj.say_hello()  # This is the same as calling MyClass.say_hello(obj)

###################################self############################################
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

# Creating an instance of Rectangle
rect1 = Rectangle(4, 5)
rect2 = Rectangle(10, 20)

# Accessing instance-specific values
print(rect1.area())  # Output: 20 (4 * 5)
print(rect2.area())  # Output: 200 (10 * 20)