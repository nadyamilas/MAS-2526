import math

def generate_circle(radius):
    for y in range(-radius, radius + 1):
        line = ""
        for x in range(-radius, radius + 1):
            distance = math.sqrt(x**2 + y**2)
            if distance <= radius:
                line += "* "
            else:
                line += "  "
        print(line)

def main():
    radius = int(input("Enter radius for the circle: "))
    generate_circle(radius)

if __name__ == "__main__":
    main()