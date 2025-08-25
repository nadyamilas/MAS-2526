def is_prime(number):
    # Check if the number is less than or equal to 1
    # Prime numbers are greater than 1, so set the initial result to True
    result = number > 1 #this is a boolean expression, since it returns a boolean value we do not need to use an if statement to check if it is true or false

    # Use a for loop to iterate from 2 to the square root of the number (inclusive)
    # We use int(number ** 0.5) + 1 to ensure we cover the upper bound correctly
    # (The largest possible factor of a number cannot exceed its square root)
    for i in range(2, int(number ** 0.5) + 1):
        # Check if the number is divisible by any value in the range
        # If it is divisible, it is not a prime number, so set the result to False
        if number % i == 0:
            result = False
            break

    return result

# Example usage:
num = 17
if is_prime(num):
    print(f"The number {num} is prime.")
else:
    print(f"The number {num} is not prime.")


#let's test this function
print(is_prime(5))
print(is_prime(10))
print(is_prime(11))
print(is_prime(12))
print(is_prime(13))

