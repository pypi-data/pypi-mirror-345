code = '''
# DBSCAN 

# #include <stdio.h>
# #include <stdlib.h>
# #include <math.h>

# #define MAX_POINTS 10  // Adjust based on dataset size
# #define DIM 3          // Number of features: age, income, score
# #define EPS 12.5       // Radius for neighborhood search
# #define MIN_SAMPLES 3  // Minimum points to form a cluster
# #define UNCLASSIFIED -2
# #define NOISE -1

# typedef struct {
#     int id;
#     double features[DIM]; // Age, Income, Spending Score
#     int cluster;
# } Point;

# Point data[MAX_POINTS] = {
#     {1, {19, 15, 39}, UNCLASSIFIED},
#     {2, {21, 15, 81}, UNCLASSIFIED},
#     {3, {20, 16, 6}, UNCLASSIFIED},
#     {4, {23, 16, 77}, UNCLASSIFIED},
#     {5, {31, 17, 40}, UNCLASSIFIED},
#     {6, {22, 17, 76}, UNCLASSIFIED},
#     {7, {35, 18, 6}, UNCLASSIFIED},
#     {8, {23, 18, 94}, UNCLASSIFIED},
#     {9, {64, 19, 3}, UNCLASSIFIED},
#     {10, {30, 19, 72}, UNCLASSIFIED}
# };
# int total_points = MAX_POINTS;

# // Function to calculate Euclidean distance
# double euclidean_distance(Point *p1, Point *p2) {
#     double sum = 0;
#     for (int i = 0; i < DIM; i++) {
#         sum += pow(p1->features[i] - p2->features[i], 2);
#     }
#     return sqrt(sum);
# }

# // Find neighbors within EPS radius
# int find_neighbors(int idx, int neighbors[]) {
#     int count = 0;
#     for (int i = 0; i < total_points; i++) {
#         if (i != idx && euclidean_distance(&data[idx], &data[i]) <= EPS) {
#             neighbors[count++] = i;
#         }
#     }
#     return count;
# }

# // Expand cluster recursively
# void expand_cluster(int idx, int cluster_id) {
#     int neighbors[MAX_POINTS];
#     int count = find_neighbors(idx, neighbors);

#     if (count < MIN_SAMPLES) {
#         data[idx].cluster = NOISE;
#         return;
#     }

#     data[idx].cluster = cluster_id;
    
#     for (int i = 0; i < count; i++) {
#         int neighbor_idx = neighbors[i];
#         if (data[neighbor_idx].cluster == UNCLASSIFIED || data[neighbor_idx].cluster == NOISE) {
#             data[neighbor_idx].cluster = cluster_id;
#             expand_cluster(neighbor_idx, cluster_id);
#         }
#     }
# }

# // DBSCAN Algorithm
# void dbscan() {
#     int cluster_id = 0;
    
#     for (int i = 0; i < total_points; i++) {
#         if (data[i].cluster == UNCLASSIFIED) {
#             expand_cluster(i, cluster_id);
#             cluster_id++;
#         }
#     }
# }

# // Print results
# void print_results() {
#     printf("\nCustomer Clusters:\n");
#     for (int i = 0; i < total_points; i++) {
#         printf("Customer %d -> Cluster: %d\n", data[i].id, data[i].cluster);
#     }
# }

# // Main function
# int main() {
#     dbscan();  // Run DBSCAN clustering
#     print_results();  // Display clusters
#     return 0;
# }





#Q1  k means

# #include <stdio.h>
# #include <stdlib.h>
# #include <math.h>
# #include <float.h>

# #define MAX_POINTS 100
# #define MAX_CLUSTERS 2
# #define MAX_ITERATIONS 100
# #define OUTLIER_THRESHOLD 5.0  // Distance threshold to consider a point an outlier

# typedef struct {
#     float x, y;
# } Point;

# typedef struct {
#     float x, y;
# } Centroid;

# float distance(Point p1, Centroid c) {
#     return sqrtf(powf(p1.x - c.x, 2) + powf(p1.y - c.y, 2));
# }

# void assign_points_to_clusters(Point points[], int num_points, Centroid centroids[], int labels[]) {
#     for (int i = 0; i < num_points; i++) {
#         float min_distance = FLT_MAX;
#         int closest_centroid = 0;
       
#         // Find the closest centroid
#         for (int j = 0; j < MAX_CLUSTERS; j++) {
#             float dist = distance(points[i], centroids[j]);
#             if (dist < min_distance) {
#                 min_distance = dist;
#                 closest_centroid = j;
#             }
#         }
       
#         // Assign point to the closest centroid
#         labels[i] = closest_centroid;
#     }
# }

# void update_centroids(Point points[], int num_points, Centroid centroids[], int labels[]) {
#     for (int j = 0; j < MAX_CLUSTERS; j++) {
#         float sum_x = 0, sum_y = 0;
#         int cluster_size = 0;
       
#         // Sum the points assigned to the centroid
#         for (int i = 0; i < num_points; i++) {
#             if (labels[i] == j) {
#                 sum_x += points[i].x;
#                 sum_y += points[i].y;
#                 cluster_size++;
#             }
#         }
       
#         // Update centroid position (average of points assigned)
#         if (cluster_size > 0) {
#             centroids[j].x = sum_x / cluster_size;
#             centroids[j].y = sum_y / cluster_size;
#         }
#     }
# }

# int kmeans(Point points[], int num_points, Centroid centroids[], int labels[]) {
#     int iterations = 0;
   
#     while (iterations < MAX_ITERATIONS) {
#         int previous_labels[num_points];
#         for (int i = 0; i < num_points; i++) {
#             previous_labels[i] = labels[i];
#         }

#         assign_points_to_clusters(points, num_points, centroids, labels);
#         update_centroids(points, num_points, centroids, labels);
       
#         // Check for convergence (if labels don't change)
#         int converged = 1;
#         for (int i = 0; i < num_points; i++) {
#             if (labels[i] != previous_labels[i]) {
#                 converged = 0;
#                 break;
#             }
#         }

#         if (converged) {
#             break;
#         }
       
#         iterations++;
#     }
   
#     return iterations;
# }

# void print_centroids(Centroid centroids[]) {
#     for (int i = 0; i < MAX_CLUSTERS; i++) {
#         printf("Centroid %d: (%.2f, %.2f)\n", i + 1, centroids[i].x, centroids[i].y);
#     }
# }

# void print_clusters(Point points[], int num_points, int labels[]) {
#     for (int i = 0; i < num_points; i++) {
#         printf("Point (%.2f, %.2f) belongs to cluster %d\n", points[i].x, points[i].y, labels[i] + 1);
#     }
# }

# void print_outliers(Point points[], int num_points, Centroid centroids[], int labels[]) {
#     printf("\nOutliers:\n");
#     for (int i = 0; i < num_points; i++) {
#         float dist = distance(points[i], centroids[labels[i]]);
#         if (dist > OUTLIER_THRESHOLD) {
#             printf("Point (%.2f, %.2f) is an outlier (Distance: %.2f)\n", points[i].x, points[i].y, dist);
#         }
#     }
# }

# int main() {
#     int num_points;
   
#     // Taking user input for the number of points
#     printf("Enter the number of points: ");
#     scanf("%d", &num_points);

#     if (num_points <= 0 || num_points > MAX_POINTS) {
#         printf("Invalid number of points. Please enter a number between 1 and %d.\n", MAX_POINTS);
#         return 1;
#     }

#     Point points[MAX_POINTS];
   
#     // Taking user input for the points
#     printf("Enter the coordinates of the points (x y):\n");
#     for (int i = 0; i < num_points; i++) {
#         printf("Point %d: ", i + 1);
#         scanf("%f %f", &points[i].x, &points[i].y);
#     }

#     Centroid centroids[MAX_CLUSTERS];

#     // Taking user input for initial centroids
#     printf("Enter the initial centroids (x y) for the 2 clusters:\n");
#     for (int i = 0; i < MAX_CLUSTERS; i++) {
#         printf("Centroid %d: ", i + 1);
#         scanf("%f %f", &centroids[i].x, &centroids[i].y);
#     }

#     int labels[MAX_POINTS];  // Array to store which cluster each point belongs to

#     // Perform K-Means Clustering
#     int iterations = kmeans(points, num_points, centroids, labels);

#     // Print results
#     printf("\nK-means converged in %d iterations.\n\n", iterations);
#     print_centroids(centroids);
#     print_clusters(points, num_points, labels);
#     print_outliers(points, num_points, centroids, labels);

#     return 0;
# }





#Q2      Elbow method

# #include <stdio.h>
# #include <math.h>

# #define MAX_POINTS 100
# #define DIMENSIONS 2
# #define MAX_ITERATIONS 100

# // Structure to represent a point in 2D space
# typedef struct {
#     float x;
#     float y;
#     int cluster;  // To store the cluster index for each point
# } Point;

# // Function to calculate the Euclidean distance between two points
# float euclidean_distance(Point p1, Point p2) {
#     return sqrt((p1.x - p2.x) * (p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y));
# }

# // Function to calculate the Sum of Squared Errors (SSE) for the current clusters
# float calculate_sse(Point points[MAX_POINTS], Point centroids[MAX_POINTS], int n, int k) {
#     float sse = 0.0;

#     // Calculate SSE by summing the squared distances of each point to its centroid
#     for (int i = 0; i < n; i++) {
#         sse += euclidean_distance(points[i], centroids[points[i].cluster]) * euclidean_distance(points[i], centroids[points[i].cluster]);
#     }

#     return sse;
# }

# // Function to update centroids
# void update_centroid(Point centroids[MAX_POINTS], Point points[MAX_POINTS], int n, int k) {
#     float sum_x[k], sum_y[k];
#     int count[k];

#     for (int i = 0; i < k; i++) {
#         sum_x[i] = sum_y[i] = count[i] = 0;
#     }

#     // Sum up all points in each cluster
#     for (int i = 0; i < n; i++) {
#         int cluster_index = points[i].cluster;
#         sum_x[cluster_index] += points[i].x;
#         sum_y[cluster_index] += points[i].y;
#         count[cluster_index]++;
#     }

#     // Calculate new centroids
#     for (int i = 0; i < k; i++) {
#         if (count[i] != 0) {
#             centroids[i].x = sum_x[i] / count[i];
#             centroids[i].y = sum_y[i] / count[i];
#         }
#     }
# }

# // Function to assign points to the nearest centroid
# void assign_clusters(Point points[MAX_POINTS], Point centroids[MAX_POINTS], int n, int k) {
#     for (int i = 0; i < n; i++) {
#         float min_distance = INFINITY;
#         int closest_centroid = 0;

#         for (int j = 0; j < k; j++) {
#             float distance = euclidean_distance(points[i], centroids[j]);
#             if (distance < min_distance) {
#                 min_distance = distance;
#                 closest_centroid = j;
#             }
#         }

#         points[i].cluster = closest_centroid;
#     }
# }

# // Function to perform K-means clustering
# void k_means(Point points[MAX_POINTS], int n, int k, float *sse) {
#     Point centroids[k];

#     // Initialize centroids to fixed values
#     for (int i = 0; i < k; i++) {
#         centroids[i] = points[i];
#     }

#     int iterations = 0;
#     int prev_clusters[MAX_POINTS];
#     int converged = 0;

#     while (iterations < MAX_ITERATIONS && !converged) {
#         // Store the current clusters for convergence check
#         for (int i = 0; i < n; i++) {
#             prev_clusters[i] = points[i].cluster;
#         }

#         // Assign points to nearest centroid
#         assign_clusters(points, centroids, n, k);

#         // Update centroids
#         update_centroid(centroids, points, n, k);

#         // Check for convergence (if no points changed their cluster)
#         converged = 1;
#         for (int i = 0; i < n; i++) {
#             if (points[i].cluster != prev_clusters[i]) {
#                 converged = 0;
#                 break;
#             }
#         }

#         iterations++;
#     }

#     // Calculate and return the SSE
#     *sse = calculate_sse(points, centroids, n, k);
# }

# // Main function to apply the Elbow Method
# int main() {
#     int n;

#     // Input number of data points
#     printf("Enter the number of data points: ");
#     scanf("%d", &n);

#     Point points[MAX_POINTS];

#     // Input the data points
#     printf("Enter the data points (x, y):\n");
#     for (int i = 0; i < n; i++) {
#         printf("Point %d: ", i + 1);
#         scanf("%f %f", &points[i].x, &points[i].y);
#     }

#     // Array to store SSE for different k values
#     float sse_values[10];

#     // Run K-means for k values from 2 to 10 and calculate the SSE for each
#     printf("\nCalculating SSE for different values of k...\n");
#     for (int k = 2; k <= 10; k++) {
#         k_means(points, n, k, &sse_values[k - 2]);
#         printf("SSE for k = %d: %.2f\n", k, sse_values[k - 2]);
#     }

#     // Find the optimal value of k using the Elbow method
#     int optimal_k = 2;
#     float min_sse_diff = INFINITY;
   
#     for (int k = 2; k < 10; k++) {
#         float sse_diff = sse_values[k - 1] - sse_values[k - 2];
#         if (sse_diff > min_sse_diff) {
#             break;
#         }
#         optimal_k = k + 1;
#     }

#     // Print the optimal k value
#     printf("\nOptimal value of k based on the Elbow method: k = %d\n", optimal_k);

#     return 0;
# }





#Q3    Random

# #include <stdio.h>
# #include <stdlib.h>
# #include <math.h>
# #include <float.h>
# #include <time.h>

# #define MAX_POINTS 100
# #define MAX_CLUSTERS 10
# #define MAX_ITERATIONS 100
# #define OUTLIER_THRESHOLD 5.0  // Distance threshold to consider a point an outlier

# typedef struct {
#     float x, y;
# } Point;

# typedef struct {
#     float x, y;
# } Centroid;

# float distance(Point p1, Centroid c) {
#     return sqrtf(powf(p1.x - c.x, 2) + powf(p1.y - c.y, 2));
# }

# void assign_points_to_clusters(Point points[], int num_points, Centroid centroids[], int labels[], int k) {
#     for (int i = 0; i < num_points; i++) {
#         float min_distance = FLT_MAX;
#         int closest_centroid = 0;
       
#         for (int j = 0; j < k; j++) {
#             float dist = distance(points[i], centroids[j]);
#             if (dist < min_distance) {
#                 min_distance = dist;
#                 closest_centroid = j;
#             }
#         }
       
#         labels[i] = closest_centroid;
#     }
# }

# void update_centroids(Point points[], int num_points, Centroid centroids[], int labels[], int k) {
#     for (int j = 0; j < k; j++) {
#         float sum_x = 0, sum_y = 0;
#         int cluster_size = 0;
       
#         for (int i = 0; i < num_points; i++) {
#             if (labels[i] == j) {
#                 sum_x += points[i].x;
#                 sum_y += points[i].y;
#                 cluster_size++;
#             }
#         }
       
#         if (cluster_size > 0) {
#             centroids[j].x = sum_x / cluster_size;
#             centroids[j].y = sum_y / cluster_size;
#         }
#     }
# }

# float calculate_sse(Point points[], int num_points, Centroid centroids[], int labels[], int k) {
#     float sse = 0.0;
   
#     for (int i = 0; i < num_points; i++) {
#         float dist = distance(points[i], centroids[labels[i]]);
#         sse += dist * dist;
#     }
   
#     return sse;
# }

# int kmeans(Point points[], int num_points, Centroid centroids[], int labels[], int k) {
#     int iterations = 0;
   
#     while (iterations < MAX_ITERATIONS) {
#         int previous_labels[num_points];
#         for (int i = 0; i < num_points; i++) {
#             previous_labels[i] = labels[i];
#         }

#         assign_points_to_clusters(points, num_points, centroids, labels, k);
#         update_centroids(points, num_points, centroids, labels, k);
       
#         int converged = 1;
#         for (int i = 0; i < num_points; i++) {
#             if (labels[i] != previous_labels[i]) {
#                 converged = 0;
#                 break;
#             }
#         }

#         if (converged) {
#             break;
#         }
       
#         iterations++;
#     }
   
#     return iterations;
# }

# void print_centroids(Centroid centroids[], int k) {
#     printf("Centroids:\n");
#     for (int i = 0; i < k; i++) {
#         printf("Centroid %d: (%.2f, %.2f)\n", i + 1, centroids[i].x, centroids[i].y);
#     }
# }

# void print_clusters(Point points[], int num_points, int labels[]) {
#     for (int i = 0; i < num_points; i++) {
#         printf("Point (%.2f, %.2f) belongs to cluster %d\n", points[i].x, points[i].y, labels[i] + 1);
#     }
# }

# int main() {
#     int num_points, k;
   
#     // Taking user input for the number of points and clusters
#     printf("Enter the number of points: ");
#     scanf("%d", &num_points);

#     printf("Enter the number of clusters (k): ");
#     scanf("%d", &k);

#     if (num_points <= 0 || num_points > MAX_POINTS || k <= 1 || k > MAX_CLUSTERS) {
#         printf("Invalid input. Please enter valid values.\n");
#         return 1;
#     }

#     Point points[MAX_POINTS];
   
#     // Taking user input for the points
#     printf("Enter the coordinates of the points (x y):\n");
#     for (int i = 0; i < num_points; i++) {
#         printf("Point %d: ", i + 1);
#         scanf("%f %f", &points[i].x, &points[i].y);
#     }

#     int labels[MAX_POINTS];  // Array to store which cluster each point belongs to
#     float sse_values[3];     // Store SSE for 3 instances

#     srand(time(0));  // Seed the random number generator

#     int min_sse_instance = -1;
#     float min_sse = FLT_MAX;

#     // Execute K-means for 3 instances
#     for (int instance = 0; instance < 3; instance++) {
#         Centroid centroids[k];

#         // Randomly initialize centroids
#         for (int i = 0; i < k; i++) {
#             int rand_index = rand() % num_points;
#             centroids[i].x = points[rand_index].x;
#             centroids[i].y= points[rand_index].y;
#         }

#         // Perform K-Means Clustering
#         int iterations = kmeans(points, num_points, centroids, labels, k);

#         // Calculate the SSE for the current instance
#         float sse = calculate_sse(points, num_points, centroids, labels, k);
#         sse_values[instance] = sse;

#         printf("\nInstance %d:\n", instance + 1);
#         printf("K-means converged in %d iterations.\n", iterations);
#         print_centroids(centroids, k);
#         printf("Sum Squared Error: %.2f\n", sse);

#         // Track the instance with the least SSE
#         if (sse < min_sse) {
#             min_sse = sse;
#             min_sse_instance = instance;
#         }
#     }

#     // Output the instance with the least SSE
#     printf("\nInstance with least SSE is Instance %d with SSE = %.2f\n", min_sse_instance + 1, min_sse);

#     return 0;
# }
'''


def print_code():
    print(code)

if __name__ == "__main__":
    exec(code)