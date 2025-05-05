
code = '''

# 1
# a) Find Armstrong numbers up to 'n'
def Armstrong(n):
    print("Armstrong numbers up to", n)
    for num in range(1, n + 1):
        digits = list(map(int, str(num)))
        if sum([d**len(digits) for d in digits]) == num:
            print(num, end=" ")
    print("\n")

# b) Find Prime numbers up to 'n'
def Prime(n):
    print("Prime numbers up to", n)
    for num in range(2, n + 1):
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                break
        else:
            print(num, end=" ")
    print("\n")

# c) Print pattern of stars
def Pattern(n):
    for i in range(1, n + 1):
        print('* ' * i)
    for i in range(n - 1, 0, -1):
        print('* ' * i)


num = int(input("Enter a number: "))
Armstrong(num)
Prime(num)
Pattern(5)

# 2
# MyModule1.py

# Predefined user credentials
user_ids = ["alice", "bob", "charlie"]
passwords = ["pass123", "bob@456", "charlie#789"]

def Authenticate(uid, pwd):
    if uid in user_ids:
        index = user_ids.index(uid)
        if index < len(passwords) and passwords[index] == pwd:
            return 1
    return 0

def Rect_Area(l, b):
    return l * b

def Multi(x):
    for i in range(1, 11):
        print(f"{x} x {i} = {x*i}")

# main.py

import MyModule1

uid = input("Enter user ID: ")
pwd = input("Enter password: ")

if MyModule1.Authenticate(uid, pwd):
    print("Login Successful!")
else:
    print("Invalid Credentials.")

l = float(input("Enter length of rectangle: "))
b = float(input("Enter breadth of rectangle: "))
print("Area of Rectangle:", MyModule1.Rect_Area(l, b))

x = int(input("Enter number for multiplication table: "))
MyModule1.Multi(x)

# 3 Generate 100 unique 8-digit ticket numbers

import random

tickets = random.sample(range(10_000_000, 100_000_000), 100)

lucky_tickets = random.sample(tickets, 3)

print("Winning Tickets:")
print("1st Winner:", lucky_tickets[0])
print("2nd Winner:", lucky_tickets[1])

print("🎖 Backup Ticket:", lucky_tickets[2])

# 4 Recursive sum from 0 to num
def recursive_sum(num):
    if num == 0:
        return 0
    return num + recursive_sum(num - 1)

print(recursive_sum(10))

# 5 Print list in reverse order
def reverse_list(lst):
    for item in reversed(lst):
        print(item)

reverse_list([1, 2, 3, 4, 5])
'''

def print_code():
    print(code)

if __name__ == "__main__":
    exec(code)