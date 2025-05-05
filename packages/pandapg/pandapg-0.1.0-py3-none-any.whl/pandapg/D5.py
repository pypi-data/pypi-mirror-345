code = '''
#1 a 2D Points

import matplotlib.pyplot as plt

x = [1, 3, 5, 7, 9]
y = [2, 4, 1, 6, 3]

plt.plot(x, y, linestyle='--', color='red', marker='+', markersize=10.5, linewidth=2.5)

plt.title('2D Points Joined with Dashed Line')
plt.xlabel('X-Axis')
plt.ylabel('Y-Axis')

plt.xlim(min(x)-4, max(x)+4)
plt.ylim(min(y)-4, max(y)+4)

plt.savefig('r1.jpg')
plt.show()

# 1 b Plot f(x) = x2 and f(x)=x3

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-10, 10, 100)  # 100 points between -10 and 10

y1 = x**2  # x squared
y2 = x**3  # x cubed

plt.plot(x, y1, linestyle='--', color='blue', label='f(x) = x^2')
plt.plot(x, y2, linestyle='-.', color='green', label='f(x) = x^3')

plt.title('Functions f(x) = x² and f(x) = x³')
plt.xlabel('X-Axis')
plt.ylabel('Y-Axis')

plt.legend()

plt.xlim(min(x)-4, max(x)+4)
plt.ylim(min(min(y1), min(y2))-4, max(max(y1), max(y2))+4)

plt.savefig('r2.jpg')
plt.show()

# 2 Different Graph Same figure

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-5, 5, 100)  # 100 points between -5 and 5

y1 = x
y2 = x**2
y3 = x**3
y4 = x**4
y5 = x**5
y6 = x**6

plt.figure(figsize=(12, 8))

# Subplot 1 - f(x) = x
plt.subplot(2, 3, 1)  # (rows, columns, plot_number)
plt.plot(x, y1, 'r')
plt.title('f(x) = x')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

# Subplot 2 - f(x) = x²
plt.subplot(2, 3, 2)
plt.plot(x, y2, 'g')
plt.title('f(x) = x²')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

# Subplot 3 - f(x) = x³
plt.subplot(2, 3, 3)
plt.plot(x, y3, 'b')
plt.title('f(x) = x³')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

# Subplot 4 - f(x) = x⁴
plt.subplot(2, 3, 4)
plt.plot(x, y4, 'm')
plt.title('f(x) = x⁴')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

# Subplot 5 - f(x) = x⁵
plt.subplot(2, 3, 5)
plt.plot(x, y5, 'c')
plt.title('f(x) = x⁵')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

# Subplot 6 - f(x) = x⁶
plt.subplot(2, 3, 6)
plt.plot(x, y6, 'y')
plt.title('f(x) = x⁶')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

plt.tight_layout()
plt.show()

# 3 f(x)=2x + 4 f(x)=4x2 + 5x + 4

import matplotlib.pyplot as plt

def plot_functions(x):
    y1 = [2*i + 4 for i in x]  # For f(x) = 2x + 4
    y2 = [4*i**2 + 5*i + 4 for i in x]  # For f(x) = 4x² + 5x + 4

    plt.plot(x, y1, label='f(x) = 2x + 4', color='blue', linestyle='--')
    plt.plot(x, y2, label='f(x) = 4x² + 5x + 4', color='red', linestyle='-')

    plt.title('Plot of Two Functions')
    plt.xlabel('X Values')
    plt.ylabel('Y Values')

    plt.legend()

    plt.grid(True)

    plt.savefig('two_functions_plot.jpg')
    plt.show()

x_input = list(map(int, input("Enter space-separated x values: ").split()))
plot_functions(x_input)

# 4 0.345 to 0.567

import random

def area_of_square(side):
    return side * side

n = int(input("Enter how many random numbers you want to generate: "))

random_numbers = [round(random.uniform(0.345, 0.567), 5) for _ in range(n)]

with open('random_numbers.txt', 'w') as f:
    for number in random_numbers:
        f.write(str(number) + '\n')

print("\nRandom numbers written to 'random_numbers.txt'.")

numbers_from_file = []
with open('random_numbers.txt', 'r') as f:
    for line in f:
        numbers_from_file.append(float(line.strip()))

print("\nContent of the file:")
for num in numbers_from_file:
    print(num)

average = sum(numbers_from_file) / len(numbers_from_file)
print("\nAverage of numbers:", average)

area = area_of_square(average)
print("\nArea of square with side as average value:", area)

# 5 [4,5,5,7,6,8,8,9,4,4,4,4,5,5,7,7,8,8,8]

import matplotlib.pyplot as plt

data = [4,5,5,7,6,8,8,9,4,4,4,4,5,5,7,7,8,8,8]

min_val = min(data)
max_val = max(data)

bins = range(min_val, max_val + 5, 5)

plt.hist(data, bins=bins, color='skyblue', edgecolor='black')

plt.title("Plotting Histogram")
plt.xlabel("Data Points")
plt.ylabel("Frequency")

plt.xlim(min_val - 4, max_val + 4)

plt.savefig('histogram_plot.jpg')
plt.show()

# 6 O, E, A, B

import matplotlib.pyplot as plt

grades = [23, 34, 12, 5]
labels = ['O', 'E', 'A', 'B']

plt.pie(grades, labels=labels, autopct='%.2f%%', startangle=90, colors=['gold', 'skyblue', 'lightgreen', 'lightcoral'])

plt.title("Percentage of Students in DBMS Grades")
plt.show()

# 7 company number of units

import matplotlib.pyplot as plt

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

faceCreamSalesData = [250, 263, 274, 289, 300, 310, 320, 305, 300, 310, 290, 280]
faceWashSalesData = [150, 160, 170, 180, 190, 200, 210, 205, 200, 195, 185, 180]
toothPasteSalesData = [100, 110, 120, 130, 140, 150, 160, 155, 150, 145, 140, 135]
bathingsoapSalesData = [350, 360, 370, 380, 390, 400, 410, 405, 400, 390, 380, 370]
shampooSalesData = [120, 130, 140, 150, 160, 170, 180, 175, 170, 165, 160, 155]
moisturizerSalesData = [90, 95, 100, 105, 110, 115, 120, 118, 115, 112, 110, 108]

x = list(range(12))

plt.plot(x, faceCreamSalesData, label='Face Cream Sales', marker='o')
plt.plot(x, faceWashSalesData, label='Face Wash Sales', marker='o')
plt.plot(x, toothPasteSalesData, label='Toothpaste Sales', marker='o')
plt.plot(x, bathingsoapSalesData, label='Bathing Soap Sales', marker='o')
plt.plot(x, shampooSalesData, label='Shampoo Sales', marker='o')
plt.plot(x, moisturizerSalesData, label='Moisturizer Sales', marker='o')

plt.title('Sales Data Per Month')
plt.xlabel('Month')
plt.ylabel('Units Sold')

plt.xticks(x, months)

plt.yticks(range(0, 500, 50))
plt.legend(loc='upper left')
plt.show()

# 8 faceCream Sales Data

import matplotlib.pyplot as plt
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
faceCreamSalesData = [250, 263, 274, 289, 300, 310, 320, 305, 300, 310, 290, 280]

x = list(range(12))

plt.bar(x, faceCreamSalesData, color='skyblue', width=0.6)
plt.title('Face Cream Sales Per Month')
plt.xlabel('Month')
plt.ylabel('Units Sold')
plt.xticks(x, months)
plt.show()

'''


def print_code():
    print(code)

if __name__ == "__main__":
    exec(code)
