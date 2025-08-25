#Sequences are ordered collections of items. There are several sequence types in Python, the following three are the most important.
#Lists are mutable sequences, meaning that the items in a list can be changed.
#Tuples are immutable sequences, meaning that the items in a tuple cannot be changed.
#Strings are immutable sequences of Unicode code points, meaning that the characters in a string cannot be changed.
#Let's look at some examples.
#This is how you create a list.
my_list = ["apple", "banana", "cherry"]
#This is how you create a tuple.
my_tuple = ("apple", "banana", "cherry")
#This is how you create a string.
my_string = "apple"
#Now let's print the type of each of these variables.
print(type(my_list))
print(type(my_tuple))
print(type(my_string))

#List operations
#This is how you access an item in a list.
print(my_list[0])
#This is how you change an item in a list.
my_list[0] = "orange"
print(my_list)
#This is how you add an item to a list.
my_list.append("mango")
print(my_list)
#This is how you remove an item from a list.
my_list.remove("banana")
print(my_list)
#This is how you remove the last item from a list.
my_list.pop()
print(my_list)
#This is how you remove an item from a specific index.
my_list.pop(0)
print(my_list)
#This is how you clear a list.
my_list.clear()
print(my_list)
#This is how you delete a list.
del my_list

#A list of numbers can be sorted using the sort() method.
my_list = [4, 2, 3, 1]
my_list.sort()
print(my_list)

#A dictionary is a collection which is unordered, changeable and indexed. In Python dictionaries are written with curly brackets, and they have keys and values.
#This is how you create a dictionary.
my_dictionary = {"name": "Johnny", "age": 59} #Multiple data types can be stored in a dictionary.
#This is how you access a value in a dictionary.
print(my_dictionary["name"])
#This is how you change a value in a dictionary.
my_dictionary["name"] = "Marr"
print(my_dictionary)
#This is how you add a value to a dictionary.
my_dictionary["occupation"] = "Musician"
print(my_dictionary)

#Now let's run this program.