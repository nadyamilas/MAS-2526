#Let's create a fun excercize with loops.
#We make a pattern of stars on the screen.
for i in range(10):
    for j in range(i):
        print("*")
        
#This doesn't look right. Let's fix it.
for i in range(10):
    for j in range(i):
        print("i", end="") #This prints the * without a new line
    print() #This prints a new line

#Now let's run this program.