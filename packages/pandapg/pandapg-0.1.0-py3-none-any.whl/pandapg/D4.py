code = '''

# 1 Square of each element
def square_elements(lst):
    return list(map(lambda x: x ** 2, lst))

numbers = [1, 2, 3, 4, 5]
result = square_elements(numbers)
print("Squared List:", result)

# 2 Generate Password

import random
import string

def generate_password():
    upper_case_letters = random.sample(string.ascii_uppercase, 2)
    digits = random.sample(string.digits, 1)  
    special_chars = random.sample("!@#$%^&*()", 1)
    remaining_chars = random.sample(string.ascii_lowercase + string.digits + string.punctuation, 6)

    password_chars = upper_case_letters + digits + special_chars + remaining_chars
    random.shuffle(password_chars)

    if '@' not in password_chars:
        password_chars[2] = '@'

    password = ''.join(password_chars)
    return password

password = generate_password()
print("Generated Password:", password)

# 3 a 5x2 Integer Array between 100 to 200
import numpy as np

array_5x2 = np.arange(100, 200, 10).reshape(5, 2)

print("5x2 Integer Array:")
print(array_5x2)

# 3 b 5x5 array of random floating point values

array_5x5 = np.random.rand(5, 5)

odd_rows_even_columns = array_5x5[::2, 1::2]

print("\n5x5 Array of Floating Point Values:")
print(array_5x5)

print("\nOdd Rows and Even Columns:")
print(odd_rows_even_columns)

# 4 2D array with user IDs and passwords

user_data = [
    ["U1", "P1"],
    ["U2", "P2"],
    ["U3", "P3"],
    ["U4", "P4"],
    ["U5", "P5"]
]

def authenticate(userid, password):
    for user in user_data:
        if user[0] == userid and user[1] == password:
            return "Authentication Successful"
    
    return "Authentication Failed"

userid_input = input("Enter User ID: ")
password_input = input("Enter Password: ")

result = authenticate(userid_input, password_input)
print(result)

# 5 Create an NxC matrix initialized with 0's

import numpy as np
import random

def initialize_matrix(N, C):
    matrix = np.zeros((N, C), dtype=int)

    for i in range(N):
        cluster_index = random.randint(0, C-1)  
        matrix[i][cluster_index] = 1
    
    return matrix

# Example usage
N = 5
C = 3

matrix = initialize_matrix(N, C)
print("Initialized Matrix:")
print(matrix)

# 6 Calculate mean and standard deviation for each day
import numpy as np
from collections import Counter

data = {
    'Mon': [112, 90, 87, 87, 87],
    'Tues': [112, 87, 88, 75, 75],
    'Wed': [90, 82, 81, 75, 65],
    'Thurs': [92, 87, 81, 71, 75],
    'Fri': [100, 45, 40, 42, 45]
}

mean_speeds = {}
std_devs = {}

for day, speeds in data.items():
    mean_speeds[day] = np.mean(speeds)
    std_devs[day] = np.std(speeds)

counter = Counter(data['Mon'])
mode_monday = counter.most_common(1)[0][0] 

# Output the results
print("Mean Speed for each day:")
for day, mean in mean_speeds.items():
    print(f"{day}: {mean:.2f} km/h")

print("\nStandard Deviation of Speeds for each day:")
for day, std_dev in std_devs.items():
    print(f"{day}: {std_dev:.2f} km/h")

print(f"\nMost frequent speed on Monday: {mode_monday} km/h")

# 7 a. Accept a word as parameter

def count_vowels_and_length(word):
    vowels = "aeiouAEIOU"  # List of vowels
    vowel_count = 0
    length = 0
    
    for char in word:
        if char in vowels:
            vowel_count += 1
        length += 1
    
    return vowel_count, length

# Example usage
word = input("Enter a word: ")
vowel_count, length = count_vowels_and_length(word)
print(f"Number of vowels: {vowel_count}")
print(f"Total length of the word: {length}")

# 7 b accept a list of names and find the length

def count_vowels_and_length(word):
    vowels = "aeiouAEIOU"
    vowel_count = 0
    length = 0
    
    for char in word:
        if char in vowels:
            vowel_count += 1
        length += 1
    
    return vowel_count, length

def process_names(names):
    for name in names:
        vowel_count, length = count_vowels_and_length(name)
        print(f"Name: {name}")
        print(f"Length: {length}")
        print(f"Number of vowels: {vowel_count}\n")

# Example usage
names = ["John", "Alice", "Bob", "Emily"]
process_names(names)

# 7 c Count all letters digits special symbol

def count_letters_digits_specials(s):
    letters = 0
    digits = 0
    specials = 0
    
    for char in s:
        if char.isalpha(): 
            letters += 1
        elif char.isdigit(): 
            digits += 1
        else:
            specials += 1
    
    return letters, digits, specials

# Example usage
string = input("Enter a string: ")
letters, digits, specials = count_letters_digits_specials(string)
print(f"Letters: {letters}, Digits: {digits}, Special Symbols: {specials}")

# 7 d String made of first middle and last

def merge_strings(s1, s2):
    first_s1 = s1[0]
    mid_s1 = s1[len(s1) // 2] if len(s1) % 2 != 0 else s1[len(s1) // 2 - 1]
    last_s1 = s1[-1]
    
    first_s2 = s2[0]
    mid_s2 = s2[len(s2) // 2] if len(s2) % 2 != 0 else s2[len(s2) // 2 - 1]
    last_s2 = s2[-1]
    
    new_string = first_s1 + mid_s1 + last_s1 + first_s2 + mid_s2 + last_s2
    return new_string

# Example usage
s1 = "America"
s2 = "Netherlands"
new_string = merge_strings(s1, s2)
print(f"New string: {new_string}")

# 7 e. occurences of a substring 

def find_substring_occurrences(s, substring):
    s = s.lower()
    substring = substring.lower()
    
    count = 0
    start = 0
    
    while True:
        start = s.find(substring, start) 
        if start == -1:
            break
        count += 1
        start += 1 
    
    return count

# Example usage
string = input("Enter the string: ")
substring = input("Enter the substring to search for: ")
occurrences = find_substring_occurrences(string, substring)
print(f"Occurrences of '{substring}': {occurrences}")

# 8 list and a tupple 100 random integer

import random
import time
import sys

random_numbers = [random.randint(2, 200) for _ in range(100)]

random_list = random_numbers.copy()
random_tuple = tuple(random_numbers)

start_list = time.time()
squared_list = []
for num in random_list:
    squared_list.append(num ** 2)
end_list = time.time()

start_tuple = time.time()
squared_tuple = []
for num in random_tuple:
    squared_tuple.append(num ** 2)
end_tuple = time.time()

memory_list = sys.getsizeof(random_list)
memory_tuple = sys.getsizeof(random_tuple)

print("Time taken to iterate and square list:", end_list - start_list, "seconds")
print("Time taken to iterate and square tuple:", end_tuple - start_tuple, "seconds")

print("Memory used by list:", memory_list, "bytes")
print("Memory used by tuple:", memory_tuple, "bytes")

'''

def print_code():
    print(code)

if __name__ == "__main__":
    exec(code)