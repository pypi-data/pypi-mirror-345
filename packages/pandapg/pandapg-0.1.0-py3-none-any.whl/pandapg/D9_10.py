code = '''
Q1

import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

# Step a) Create DataFrame
n = 2_000_000  # 2 million
positions = np.arange(n)
mapping_values = np.random.normal(loc=45, scale=1.2, size=n)

df = pd.DataFrame({
    "Position": positions,
    "Mapping": mapping_values
})

# Step b) Display first 1000 records
print(df.head(1000))

# Plot mapping values position-wise
plt.figure(figsize=(12,6))
plt.plot(df["Position"][:1000], df["Mapping"][:1000], marker='.', linestyle='none')
plt.title("Mapping Values for First 1000 Positions")
plt.xlabel("Position")
plt.ylabel("Mapping Value")
plt.show()

# Step c) Mask values in random region [P, P+L]
P = random.randint(0, n-5000)
L = random.randint(1000, 5000)

print(f"\nSelected region: [{P}, {P+L}]")

# New random values with different distribution
new_values = np.random.normal(loc=4000, scale=0.5, size=L)
df.loc[P:P+L-1, "Mapping"] = new_values

# Step d) Set 3 random positions inside [P, P+L] as NaN
random_positions = random.sample(range(P, P+L), 3)
df.loc[random_positions, "Mapping"] = np.nan

print(f"\nRandom NaN positions: {random_positions}")

# Step e) Display all positions where Mapping > 4000
high_mapping = df[df["Mapping"] > 4000]
print("\nPositions where Mapping > 4000:")
print(high_mapping)

# Step f) Replace all missing values (NaN) with 999
df["Mapping"] = df["Mapping"].mask(df["Mapping"].isna(), 999)

# Step g) Regions having mapping value < 12
low_mapping = df[df["Mapping"] < 12]
print(f"\nRegions with Mapping < 12: {len(low_mapping)} records")
print(low_mapping)

# Plot again
plt.figure(figsize=(12,6))
plt.plot(df["Position"][:10000], df["Mapping"][:10000], marker='.', linestyle='none')
plt.title("Mapping Values for First 10000 Positions")
plt.xlabel("Position")
plt.ylabel("Mapping Value")
plt.show()

# Step h) Add Class column (Normal / Abnormal)
df['Class'] = df['Mapping'].apply(lambda x: 'Abnormal' if x > 3000 else 'Normal')

# Step i) Remove instances where Mapping = 999
df = df[df["Mapping"] != 999]

# Step ii) Create Test and Training set
X = df[["Mapping"]]
y = df["Class"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

# Step iii) Train and Compare 3 classifiers
# 1. Decision Tree
dt_model = DecisionTreeClassifier()
dt_model.fit(X_train, y_train)
dt_pred = dt_model.predict(X_test)

print("\nDecision Tree:")
print(confusion_matrix(y_test, dt_pred))
print(classification_report(y_test, dt_pred))
print(f"Accuracy: {accuracy_score(y_test, dt_pred)*100:.2f}%")

# 2. KNN Classifier
knn_model = KNeighborsClassifier()
knn_model.fit(X_train, y_train)
knn_pred = knn_model.predict(X_test)

print("\nKNN Classifier:")
print(confusion_matrix(y_test, knn_pred))
print(classification_report(y_test, knn_pred))
print(f"Accuracy: {accuracy_score(y_test, knn_pred)*100:.2f}%")

# 3. SVM Classifier
svm_model = SVC()
svm_model.fit(X_train, y_train)
svm_pred = svm_model.predict(X_test)

print("\nSVM Classifier:")
print(confusion_matrix(y_test, svm_pred))
print(classification_report(y_test, svm_pred))
print(f"Accuracy: {accuracy_score(y_test, svm_pred)*100:.2f}%")





# Problem 2 water acess

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report

# a) Load the dataset
df = pd.read_csv('water_potability.csv')   # <-- Use your path if needed

# b) Display all features and target column
print("\nFeatures (Columns):")
print(df.columns)
print("\nTarget Column: 'Potability'")

# c) Count total records
print(f"\nTotal records: {len(df)}")

# d) Display type of each column
print("\nData Types of Each Column:")
print(df.dtypes)

# e) Plot the hardness feature
plt.plot(df['Hardness'])
plt.title('Hardness in Water Samples')
plt.xlabel('Sample Number')
plt.ylabel('Hardness')
plt.show()

# f) Mean sulphate value
mean_sulphate = df['Sulfate'].mean()
print(f"\nMean Sulphate present: {mean_sulphate:.2f}")

# g) Fill NULLs with mean values
df.fillna(df.mean(), inplace=True)

# h) Display samples where ph<4 and chloramine=5
specific_samples = df[(df['ph'] < 4) & (df['Chloramines'] == 5)]
print("\nSamples with ph<4 and Chloramines=5:")
print(specific_samples)

# i) Mask ph<4 with its mean value
ph_mean = df['ph'].mean()
df['ph'] = df['ph'].mask(df['ph'] < 4, ph_mean)

# j) Convert Target Column 1->Drinkable, 0->Non-Drinkable
df['Potability'] = df['Potability'].map({1: 'Drinkable', 0: 'Non-Drinkable'})

print("\nTarget column after mapping:")
print(df['Potability'].value_counts())

# k) Split into 85% train and 15% test
X = df.drop('Potability', axis=1)
y = df['Potability']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

# l) Build classification model using KNN and SVM

# KNN Model
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)
y_pred_knn = knn.predict(X_test)

# SVM Model
svm = SVC()
svm.fit(X_train, y_train)
y_pred_svm = svm.predict(X_test)

# m) Test Performance

# KNN Performance
print("\nKNN Classifier Performance:")
print(f"Accuracy: {accuracy_score(y_test, y_pred_knn):.2f}")
print("Classification Report:")
print(classification_report(y_test, y_pred_knn))

# SVM Performance
print("\nSVM Classifier Performance:")
print(f"Accuracy: {accuracy_score(y_test, y_pred_svm):.2f}")
print("Classification Report:")
print(classification_report(y_test, y_pred_svm))





Q3     airline

# Problem 3 - Airline Passenger Satisfaction Prediction

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder

# a) Load the dataset
df = pd.read_csv('airline_passenger_satisfaction.csv')   # <-- Use correct file path!

# Display all features and target column
print("\nAll Features:")
print(df.columns)
print("\nTarget column: Usually 'satisfaction'")

# b) Create a sample dataset with specific columns
sample_df = df[['Age', 'Flight Distance', 'Inflight wifi service', 'Seat comfort', 'satisfaction']]

print("\nSample Dataset Columns:")
print(sample_df.head())

# c) Remove all objects having NULL
sample_df.dropna(inplace=True)

# d) Create train-test split
X = sample_df.drop('satisfaction', axis=1)
y = sample_df['satisfaction']

# Encode target column (satisfied/dissatisfied → 1/0)
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Decision Tree Model
tree_model = DecisionTreeClassifier(random_state=42)
tree_model.fit(X_train, y_train)
y_pred_tree = tree_model.predict(X_test)

# e) Display accuracy
print("\nDecision Tree Accuracy:", accuracy_score(y_test, y_pred_tree))

# f) Calculate precision and sensitivity manually
def manual_precision_recall(y_true, y_pred):
    TP = sum((y_true == 1) & (y_pred == 1))
    FP = sum((y_true == 0) & (y_pred == 1))
    FN = sum((y_true == 1) & (y_pred == 0))
    
    precision = TP / (TP + FP) if (TP + FP) != 0 else 0
    recall = TP / (TP + FN) if (TP + FN) != 0 else 0
    return precision, recall

precision, recall = manual_precision_recall(y_test, y_pred_tree)
print("\nManual Precision:", precision)
print("Manual Sensitivity (Recall):", recall)

# g) Plot the tree
plt.figure(figsize=(15,10))
plot_tree(tree_model, filled=True, feature_names=X.columns, class_names=["Dissatisfied", "Satisfied"])
plt.title("Decision Tree for Passenger Satisfaction")
plt.show()

# h) Convert any categorical feature (if any left) - (already done for target)
# [In sample_df, only numerical columns were selected.]

# i) Apply Naive Bayes
nb_model = GaussianNB()
nb_model.fit(X_train, y_train)
y_pred_nb = nb_model.predict(X_test)

# j) Compare the two results
print("\nNaive Bayes Accuracy:", accuracy_score(y_test, y_pred_nb))

precision_nb, recall_nb = manual_precision_recall(y_test, y_pred_nb)
print("\nNaive Bayes Precision:", precision_nb)
print("Naive Bayes Sensitivity (Recall):", recall_nb)




Q1     k means k=2

# Problem 1 - Water Sample Clustering using KMeans

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Step 1: Load the water quality dataset
df = pd.read_csv('water_potability.csv')  # <-- Update correct filename if needed

# Step 2: Select any two features (say, 'ph' and 'Hardness')
features = df[['ph', 'Hardness']]

# Step 3: Handle missing values by filling them with mean
features.fillna(features.mean(), inplace=True)

# Step 4: Standardize the features (good practice for KMeans)
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Step 5: Apply KMeans clustering with k=2
kmeans = KMeans(n_clusters=2, random_state=42)
clusters = kmeans.fit_predict(scaled_features)

# Add cluster labels to the dataframe
features['Cluster'] = clusters

# Step 6: Plot the clusters
plt.figure(figsize=(10,6))
plt.scatter(features['ph'], features['Hardness'], c=features['Cluster'], cmap='viridis')
plt.title('Water Sample Clustering (k=2)')
plt.xlabel('pH')
plt.ylabel('Hardness')
plt.grid(True)
plt.show()

# Step 7: Elbow Method to find optimal k
distortions = []
K = range(1, 10)

for k in K:
    kmeanModel = KMeans(n_clusters=k, random_state=42)
    kmeanModel.fit(scaled_features)
    distortions.append(kmeanModel.inertia_)

# Plotting the Elbow graph
plt.figure(figsize=(12,6))
plt.plot(K, distortions, 'bx-')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Distortion (Inertia)')
plt.title('The Elbow Method to Find Optimal k')
plt.grid(True)
plt.show()




Q2   fuzziness 1.26

import numpy as np
import pandas as pd

# Step 1: Load CSV Data
data = pd.read_csv('data.csv')  # <-- replace 'data.csv' with your actual CSV file name
X = data.values

# Step 2: Initialize parameters
c = 2                  # Number of clusters
m = 1.26               # Fuzziness level (m > 1)
max_iter = 100         # Maximum iterations
epsilon = 1e-5         # Convergence threshold

# Step 3: Initialize random membership matrix (rows = samples, cols = clusters)
n_samples = X.shape[0]
U = np.random.dirichlet(np.ones(c), size=n_samples)

# Step 4: Start iterations
for iteration in range(max_iter):
    # Save the previous membership matrix
    U_prev = U.copy()
    
    # Step 4a: Calculate cluster centers
    centers = []
    for j in range(c):
        numerator = np.sum((U[:, j][:, None] ** m) * X, axis=0)
        denominator = np.sum(U[:, j] ** m)
        centers.append(numerator / denominator)
    centers = np.array(centers)
    
    # Step 4b: Update membership matrix U
    for i in range(n_samples):
        for j in range(c):
            denom_sum = 0
            for k in range(c):
                dist_ij = np.linalg.norm(X[i] - centers[j]) + 1e-10
                dist_ik = np.linalg.norm(X[i] - centers[k]) + 1e-10
                denom_sum += (dist_ij / dist_ik) ** (2 / (m - 1))
            U[i][j] = 1.0 / denom_sum

    # Step 4c: Check convergence
    if np.linalg.norm(U - U_prev) < epsilon:
        print(f"Converged at iteration {iteration}")
        break

# Step 5: Print the final cluster centers and membership matrix
print("\nCluster Centers:")
print(centers)

print("\nFinal Membership Matrix (first 10 samples):")
print(U[:10])




Q3   K=2  and  K=3

import numpy as np
import pandas as pd
import random

# Step 1: Load the data
data = pd.read_csv('data.csv')   # <-- replace 'data.csv' with your filename
X = data.values

# Step 2: Define Distance Calculation (Euclidean Distance)
def euclidean_distance(a, b):
    return np.sqrt(np.sum((a - b) ** 2))

# Step 3: Initialize Centroids randomly
def initialize_centroids(X, k):
    indices = random.sample(range(len(X)), k)
    centroids = X[indices]
    return centroids

# Step 4: Assign clusters based on nearest centroid
def assign_clusters(X, centroids):
    clusters = []
    for point in X:
        distances = [euclidean_distance(point, centroid) for centroid in centroids]
        cluster = np.argmin(distances)
        clusters.append(cluster)
    return np.array(clusters)

# Step 5: Update centroids
def update_centroids(X, clusters, k):
    new_centroids = []
    for i in range(k):
        points = X[clusters == i]
        if len(points) == 0:
            new_centroid = X[random.randint(0, len(X)-1)]
        else:
            new_centroid = np.mean(points, axis=0)
        new_centroids.append(new_centroid)
    return np.array(new_centroids)

# Step 6: Calculate Sum Squared Error (SSE)
def calculate_sse(X, centroids, clusters):
    sse = 0
    for i, point in enumerate(X):
        centroid = centroids[clusters[i]]
        sse += euclidean_distance(point, centroid) ** 2
    return sse

# Step 7: KMeans Algorithm
def kmeans(X, k, max_iters=40, threshold=1e-4):
    centroids = initialize_centroids(X, k)
    for iteration in range(max_iters):
        clusters = assign_clusters(X, centroids)
        new_centroids = update_centroids(X, clusters, k)
        diff = np.linalg.norm(centroids - new_centroids)
        
        print(f"Iteration {iteration+1}, Centroid Change = {diff:.6f}")
        
        if diff < threshold:
            print("Convergence achieved!")
            break
        centroids = new_centroids
    
    final_sse = calculate_sse(X, centroids, clusters)
    return centroids, clusters, final_sse

# Step 8: Run KMeans for k=2 and k=3
for k in [2, 3]:
    print(f"\nRunning KMeans for k = {k}")
    centroids, clusters, sse = kmeans(X, k)
    print(f"Final Centroids for k={k}:\n{centroids}")
    print(f"Final SSE for k={k}: {sse:.2f}")

'''

def print_code():
    print(code)

if __name__ == "__main__":
    exec(code)