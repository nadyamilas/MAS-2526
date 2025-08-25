#Now we talk about loops
#Loops are used to execute a block of code repeatedly.
#There are two types of loops in Python.
#For loop
#While loop
#Let's look at some examples.
#This is how you create a For loop.
for i in range(10):
    print(i)

#you can also iterate over a list using a for loop.
my_list = ["apple", "banana", "cherry"]
for item in my_list:
    print(item)

#you can also nest loops within loops.
for i in range(10):
    for j in range(10):
        print(i, j)
#What will happen if you run this program?

#This is how you create a While loop.
i = 0
while i < 10: #break the loop when i is greater than 10
    print(i) 
    i += 1 #increment i by 1
#What will happen if you run this program?
