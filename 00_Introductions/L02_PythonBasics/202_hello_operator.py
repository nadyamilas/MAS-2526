#What is an operator?
#An operator is a symbol that tells the computer to do something.
##rithmetic operators are used with numeric values to perform common mathematical operations.
#For example, the + operator tells the computer to add two numbers.
#The - operator tells the computer to subtract two numbers.
#The * operator tells the computer to multiply two numbers.
#The / operator tells the computer to divide two numbers.
#The % operator tells the computer to divide two numbers and return the remainder.
#The ** operator tells the computer to raise a number to a power.
#The // operator tells the computer to divide two numbers and return the quotient.
#The = operator tells the computer to assign a value to a variable.
a = 10
#This is how you assign a value to a variable.
b = 5
#Now you know how to assign a value to a variable.
c = a + b
#This is how you add two numbers.
print(c)
print("Addition",c) 

c = a % b
#This is how you divide two numbers and return the remainder.(Modulo operator)
print("Modulo",c)

#Conditional operators are used to compare two values.
#== is the equality operator. It checks if two values are equal.
var_1 = 57
if var_1 == 57:
    print("The value of this variable is 57")
#This is how you check if a variable is equal to a value.
#Try changing the value of var_1 to something else and see what happens.

#Logical operators are used to combine conditional statements.
# Using "and" logical operator
num_1 = 5
num_2 = 10

if num_1 > 0 and num_2 > 0:
    print("Both numbers are positive")

#Membership operators are used to test if a sequence is present in an object.
fruits = ["apple", "banana", "cherry"]

if "banana" in fruits:
    print("Yes, 'banana' is in the list")
else:
    print("No, 'banana' is not in the list")

#Identity operators are used to compare the objects, not if they are equal, but if they are actually the same object, with the same memory location.
x = ["apple", "banana"]
y = ["apple", "banana"]
z = x #This is how you assign a variable to another variable.
# 'is' operator returns true if both variables are the same object.
if x is z:
    print("x and z are the same object")

    
#Now let's run this program.
