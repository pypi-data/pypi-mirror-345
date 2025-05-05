code = '''
# d8

# 1. The following table gives the count of matched strings and count of mismatch on each coordinate

import pandas as pd
import numpy as np

# Step 1: Create the dictionary
data = {
    'Coordinate': ['C1', 'C2', 'C3', 'C4', 'C5'],
    'Count': [300, 210, 230, 260, 270],
    'Mismatch': [5, 13, 14, 3, 2]
}

# Step 2: Create a DataFrame
df = pd.DataFrame(data)

# Save it to a CSV
df.to_csv('coordinate_data.csv', index=False)
print("CSV file 'coordinate_data.csv' created successfully.")

# Step 3: Calculate mean and standard deviation for Count
mean_count = df['Count'].mean()
std_count = df['Count'].std()

# Add a new column for Standard Score (Z-score)
df['Standard_Score'] = (df['Count'] - mean_count) / std_count

# Display final dataframe
print("\nData with Standard Score:")
print(df)


# 2. Consider n random numbers in the range 60 to 90

import random

# Step 1: Generate n random numbers between 60 and 90
n = 20  # you can set n to any number you want
random_numbers = [random.randint(60, 90) for _ in range(n)]

# Step 2: Write numbers to a file
with open('random_numbers.txt', 'w') as file:
    for num in random_numbers:
        file.write(str(num) + '\n')

print("Random numbers written to 'random_numbers.txt'.")

# Step 3: Read the file and display content
with open('random_numbers.txt', 'r') as file:
    numbers = file.readlines()
    numbers = [int(num.strip()) for num in numbers]  # Convert back to integers

print("\nContent of the file:")
print(numbers)

# Step 4: Display maximum and minimum value
print("\nMaximum value:", max(numbers))
print("Minimum value:", min(numbers))



# 3. Take a paragraph of text input.

# Step 1: Input paragraph
paragraph = input("Enter a paragraph: ")

# Step 2: Write into r1.txt
with open('r1.txt', 'w') as file:
    file.write(paragraph)

# Step 3: Read from r1.txt
with open('r1.txt', 'r') as file:
    content = file.read()
    print("\nContent of r1.txt:")
    print(content)

# Step 4: Write into r2.txt (Copying)
with open('r2.txt', 'w') as file:
    file.write(content)

# Step 5: Read from r2.txt
with open('r2.txt', 'r') as file:
    copied_content = file.read()
    print("\nContent of r2.txt:")
    print(copied_content)

    

# 4. in the year 2019 the number of COVID effected patients were 20percent of the total population, the number of effected people were 60percent in the year 2020 and 80% were affected in the year 2021.

import matplotlib.pyplot as plt

# Step 1: Input total world population
n = int(input("Enter the total world population: "))

# Step 2: Prepare list for actual values
covid_cases = [
    0.2 * n,   # 20% for 2019
    0.6 * n,   # 60% for 2020
    0.8 * n    # 80% for 2021
]

# Step 3: Display the list
print("\nList of COVID affected people each year:", covid_cases)

# Step 4: Prepare labels
labels = ['2019', '2020', '2021']

# Step 5: Plotting Pie Chart
plt.pie(covid_cases, labels=labels, autopct='%.2f%%')
plt.title("COVID Affected Population Percentage (2019-2021)")
plt.show()



# 5. Pandas read a csv file from the following url https://media.geeksforgeeks.org/wp-content/uploads/nba.csv

import pandas as pd
from sklearn import datasets

# Part (a): Read CSV file and print size, shape, dimension
nba_data = pd.read_csv("https://media.geeksforgeeks.org/wp-content/uploads/nba.csv")

print("Size of DataFrame:", nba_data.size)
print("Shape of DataFrame:", nba_data.shape)
print("Dimension of DataFrame:", nba_data.ndim)

# Part (b): Load IRIS dataset
iris = datasets.load_iris()
print("\nPreview of IRIS data:\n", iris.data[:5])

# Display features and class labels
print("\nFeatures:", iris.feature_names)
print("Target Classes:", iris.target_names)

# Part (c): Create DataFrame and replace target values
iris_df = pd.DataFrame(iris.data, columns=iris.feature_names)
iris_df['Species'] = iris.target

# Replace 0,1,2 with actual species names
species_mapping = {0: 'Setosa', 1: 'Versicolor', 2: 'Virginica'}
iris_df['Species'] = iris_df['Species'].map(species_mapping)

print("\nDataFrame after replacing class labels:\n", iris_df.head())

# Part (d): Group the class level based on Species
grouped = iris_df.groupby('Species')

# Part (e): Mean of sepal length and sepal width
print("\nMean of Sepal Length and Sepal Width for each Species:")
print(grouped[['sepal length (cm)', 'sepal width (cm)']].mean())

# Part (f): Max and standard deviation of each feature
print("\nMaximum values of each feature:")
print(grouped.max())

print("\nStandard Deviation of each feature:")
print(grouped.std())



# 6. sklearn library cluster the following dataset into 3 clusters by kmeans algorithm

# Step 1: Create CSV manually or using pandas
import pandas as pd

# Creating the data
data = {
    'Country': ['USA', 'Canada', 'France', 'UK', 'Germany', 'Australia'],
    'Latitude': [44.97, 62.40, 46.75, 54.01, 51.15, -25.45],
    'Longitude': [-103.77, -96.80, 2.40, -2.53, 10.40, 133.11],
    'Language': ['English', 'English', 'French', 'English', 'German', 'English']
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('countries.csv', index=False)

# Step 2: Read CSV
df = pd.read_csv('countries.csv')
print("Data loaded from CSV:\n", df)

# Step 3: Plot latitude and longitude
import matplotlib.pyplot as plt

plt.scatter(df['Latitude'], df['Longitude'], color='blue')
plt.title('Countries: Latitude vs Longitude')
plt.xlabel('Latitude')
plt.ylabel('Longitude')
plt.grid(True)
plt.show()

# Step 4: Apply KMeans Clustering
from sklearn.cluster import KMeans

# Only considering Latitude and Longitude for clustering
X = df[['Latitude', 'Longitude']]

# Create KMeans model
kmeans = KMeans(n_clusters=3, random_state=0)
kmeans.fit(X)

# Add cluster label to DataFrame
df['Cluster'] = kmeans.labels_

print("\nData with cluster assignment:\n", df)

# Step 5: Plot clusters
colors = ['red', 'green', 'blue']

for i in range(3):
    cluster_data = df[df['Cluster'] == i]
    plt.scatter(cluster_data['Latitude'], cluster_data['Longitude'], color=colors[i], label=f'Cluster {i}')

plt.title('Clusters of Countries')
plt.xlabel('Latitude')
plt.ylabel('Longitude')
plt.legend()
plt.grid(True)
plt.show()



# 7. Heart Failure Dataset Analysis

import pandas as pd
import matplotlib.pyplot as plt

# (a) Read the dataset
url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/00519/heart_failure_clinical_records_dataset.csv'
df = pd.read_csv(url)
print("Dataset loaded successfully!")

# (b) Display first 10 records
print("\nFirst 10 records:\n", df.head(10))

# (c) Display last 10 records
print("\nLast 10 records:\n", df.tail(10))

# (d) Check system's maximum display limit
print("\nMax rows pandas can display:", pd.get_option("display.max_rows"))

# (e) Display datatype of serum_creatinine
print("\nDatatype of serum_creatinine:", df['serum_creatinine'].dtype)

# (f) Display features having null
print("\nColumns with Null Values:\n", df.isnull().sum())

# (g) Fill null values with mean (if any)
df.fillna(df.mean(), inplace=True)

# (h) Count total number of records
print("\nTotal number of records:", len(df))

# (i) Find median of platelets and display records
platelets_median = df['platelets'].median()
print("\nMedian value of platelets:", platelets_median)

# Display records where platelets = median
print("\nRecords with platelets equal to median:\n", df[df['platelets'] == platelets_median])

# (j) Display records where creatinine_phosphokinase > 4000
print("\nRecords with creatinine_phosphokinase > 4000:\n", df[df['creatinine_phosphokinase'] > 4000])

# (h again) Find Standard Score for serum_creatinine and plot
serum_mean = df['serum_creatinine'].mean()
serum_std = df['serum_creatinine'].std()
df['serum_standard_score'] = (df['serum_creatinine'] - serum_mean) / serum_std

plt.plot(df['serum_standard_score'])
plt.title('Standard Score of Serum Creatinine')
plt.xlabel('Sample Index')
plt.ylabel('Standard Score')
plt.grid()
plt.show()

# (i) Remove duplicate records
df = df.drop_duplicates()
print("\nAfter removing duplicates, total records:", len(df))

# (j) Find correlation between age and ejection_fraction and plot
correlation = df['age'].corr(df['ejection_fraction'])
print("\nCorrelation between Age and Ejection Fraction:", correlation)

plt.scatter(df['age'], df['ejection_fraction'])
plt.title('Age vs Ejection Fraction')
plt.xlabel('Age')
plt.ylabel('Ejection Fraction')
plt.grid()
plt.show()

'''


def print_code():
    print(code)

if __name__ == "__main__":
    exec(code)