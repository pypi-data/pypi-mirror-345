code = '''
# Q1

# 1.  select the best splitting attribute to become the root node of a Decision Tree, using Gini 

import pandas as pd

# Sample data
data = {
    'Age': ['Young', 'Young', 'Middle', 'Young', 'Senior', 'Middle', 'Senior', 'Middle', 'Senior'],
    'Income': ['Low', 'High', 'High', 'middle', 'Low', 'Middle', 'middle', 'High', 'high'],
    'Class': ['No', 'yes', 'yes', 'no', 'no', 'yes', 'no', 'no', 'yes']
}

df = pd.DataFrame(data)

# Step 1: Normalize text (case-insensitive duplicates)
df = df.applymap(lambda x: x.strip().lower())

# Step 2: Remove duplicates with conflicting class labels
df = df.drop_duplicates(subset=['Age', 'Income'], keep=False)

# Gini calculation function
def gini_index(groups, classes):
    n_instances = sum([len(group) for group in groups])
    gini = 0.0
    for group in groups:
        size = len(group)
        if size == 0: continue
        score = 0.0
        for class_val in classes:
            p = [row[-1] for row in group].count(class_val) / size
            score += p * p
        gini += (1.0 - score) * (size / n_instances)
    return gini

# Convert to list of lists for processing
dataset = df.values.tolist()
features = df.columns[:-1]
classes = df['Class'].unique()

# Determine best split
min_gini = float('inf')
best_attr = None

for i, attr in enumerate(features):
    values = set(row[i] for row in dataset)
    groups = []
    for v in values:
        groups.append([row for row in dataset if row[i] == v])
    gini = gini_index(groups, classes)
    if gini < min_gini:
        min_gini = gini
        best_attr = attr

print(f"Best attribute to split on (root node): {best_attr.capitalize()}")



#Q2

import pandas as pd
import numpy as np

# a) Load data
df = pd.read_csv('lung_cancer.csv')  # Replace with your actual file path
print("Total observations:", len(df))
print("Features:")
print(df.columns.tolist())

# b) Remove unnecessary attributes (example: dropping ID or unnamed columns)
cols_to_drop = [col for col in df.columns if 'unnamed' in col.lower() or 'id' in col.lower()]
df.drop(columns=cols_to_drop, inplace=True, errors='ignore')

# c) Standardize null values using column mean
for col in df.select_dtypes(include=[np.number]).columns:
    df[col].fillna(df[col].mean(), inplace=True)

# d) Mode of each attribute
print("\nMode of each attribute:")
print(df.mode().iloc[0])

# e) Correlation matrix
print("\nCorrelation between features:")
print(df.corr(numeric_only=True))

# f) Remove duplicate rows
df.drop_duplicates(inplace=True)

# g) Display size, shape, and dimension
print("\nSize:", df.size)
print("Shape:", df.shape)
print("Dimension:", df.ndim)




#Q3

import pandas as pd
import numpy as np

# Generate data
n = 2_000_000
positions = np.arange(n)
values = np.random.normal(loc=45, scale=1.2, size=n)

# Create DataFrame
df = pd.DataFrame({
    'position': positions,
    'value': values
})

print(df.head())
print("\nShape of DataFrame:", df.shape)
'''

def print_code():
    print(code)

if __name__ == "__main__":
    exec(code)