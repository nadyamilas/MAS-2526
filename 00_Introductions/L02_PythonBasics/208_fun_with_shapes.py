def generate_square(size):
    #We can generate a square by printing a square of the same size.
    for _ in range(size):
        print("* " * size)

def generate_triangle(size):
    #We can generate a triangle by printing a square of increasing size.
    for i in range(1, size + 1):
        print("* " * i)

def main():
    #This is the main function.
    shape = 'triangle'
    size = 25

    if shape == 'square':
        #This is an if statement. It is executed if the condition is true.
        generate_square(size)
    elif shape == 'triangle':
        #This is an elif statement. It is executed if the above condition is false and this condition is true.
        generate_triangle(size)


if __name__ == "__main__":
    #The main function is the entry point of the program.
    #This means that this is the first function that will be executed.
    #This is where we call all the other functions.
    main()
