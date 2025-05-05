code = '''
# Q1  Fuzzy 
# #include <stdio.h>
# #include <math.h>

# #define C 2  // Number of clusters
# #define ITERATIONS 5
# #define FUZZINESS 1.26

# int N; // Number of data points (User Input)

# // Data points and Membership Matrix
# double data[100][2]; // Assuming max 100 data points
# //double membership[100][C]; // Membership matrix
# double clusterCenters[C][2]; // Cluster centers
# double membership[4][C] = {
#     {0.6, 0.4},
#     {0.7, 0.3},
#     {0.2, 0.8},
#     {0.3, 0.7}
# };

# // Function to take user input
# void getUserInput() {
#     printf("Enter the number of data points: ");
#     scanf("%d", &N);

#     printf("Enter %d data points (x y):\n", N);
#     for (int i = 0; i < N; i++) {
#         scanf("%lf %lf", &data[i][0], &data[i][1]);
#     }

#     // Initialize the membership matrix with random values (normalized)
#     /*printf("\nInitial Membership Matrix:\n");
#     for (int i = 0; i < N; i++) {
#         double sum = 0.0;
#         for (int j = 0; j < C; j++) {
#             membership[i][j] = (rand() % 100) / 100.0; // Random values [0,1]
#             sum += membership[i][j];
#         }
#         for (int j = 0; j < C; j++) {
#             membership[i][j] /= sum; // Normalize
#             printf("%.4f ", membership[i][j]);
#         }
#         printf("\n");
#     }*/
# }

# // Function to update cluster centers
# void updateClusterCenters() {
#     double numerator[C][2] = {0}, denominator[C] = {0};
   
#     for (int j = 0; j < C; j++) {
#         for (int i = 0; i < N; i++) {
#             double weight = pow(membership[i][j], FUZZINESS);
#             numerator[j][0] += weight * data[i][0];
#             numerator[j][1] += weight * data[i][1];
#             denominator[j] += weight;
#         }
#         clusterCenters[j][0] = numerator[j][0] / denominator[j];
#         clusterCenters[j][1] = numerator[j][1] / denominator[j];
#     }
# }

# // Function to update the membership matrix
# void updateMembershipMatrix() {
#     for (int i = 0; i < N; i++) {
#         for (int j = 0; j < C; j++) {
#             double sum = 0.0;
#             double distIJ = sqrt(pow(data[i][0] - clusterCenters[j][0], 2) +
#                                  pow(data[i][1] - clusterCenters[j][1], 2)) + 1e-10; // Avoid division by zero

#             for (int k = 0; k < C; k++) {
#                 double distIK = sqrt(pow(data[i][0] - clusterCenters[k][0], 2) +
#                                      pow(data[i][1] - clusterCenters[k][1], 2)) + 1e-10;
#                 sum += pow(distIJ / distIK, 2 / (FUZZINESS - 1));
#             }
#             membership[i][j] = 1.0 / sum;
#         }
#     }
# }

# // Function to print cluster centers
# void printClusterCenters() {
#     printf("\nCluster Centers:\n");
#     for (int j = 0; j < C; j++) {
#         printf("Cluster %d: (%.4f, %.4f)\n", j + 1, clusterCenters[j][0], clusterCenters[j][1]);
#     }
# }

# // Function to print membership matrix
# void printMembershipMatrix() {
#     printf("\nMembership Matrix:\n");
#     for (int i = 0; i < N; i++) {
#         for (int j = 0; j < C; j++) {
#             printf("%.4f ", membership[i][j]);
#         }
#         printf("\n");
#     }
# }

# int main() {
#     getUserInput();

#     for (int iter = 0; iter < ITERATIONS; iter++) {
#         printf("\nIteration %d:\n", iter + 1);
#         updateClusterCenters();
#         printClusterCenters();
#         updateMembershipMatrix();
#         printMembershipMatrix();
#     }

#     return 0;
# }






#Q2   Theta    user define threshold

# #include <stdio.h>
# #include <stdlib.h>
# #include <math.h>
# #include <time.h>

# #define C 2  // Number of clusters
# #define MAX_ITERATIONS 1000  // Maximum iterations to avoid infinite loop
# #define FUZZINESS 1.26

# int N;  // Number of data points (User Input)
# double theta; // Convergence threshold

# // Data points, membership matrix, and cluster centers
# double data[100][2];  // Assuming max 100 data points
# double membership[100][C];  // Membership matrix
# double oldMembership[100][C]; // Previous membership matrix
# double clusterCenters[C][2];  // Cluster centers

# // Function to get user input
# void getUserInput() {
#     printf("Enter the number of data points: ");
#     scanf("%d", &N);

#     printf("Enter the convergence threshold (theta): ");
#     scanf("%lf", &theta);

#     printf("Enter %d data points (x y):\n", N);
#     for (int i = 0; i < N; i++) {
#         scanf("%lf %lf", &data[i][0], &data[i][1]);
#     }

#     // Initialize membership matrix randomly (5-digit precision)
#     srand(time(0));  // Seed random number generator
#     printf("\nInitial Membership Matrix:\n");
#     for (int i = 0; i < N; i++) {
#         double sum = 0.0;
#         for (int j = 0; j < C; j++) {
#             membership[i][j] = ((rand() % 100000) / 100000.0); // Random [0,1] with 5-digit precision
#             sum += membership[i][j];
#         }
#         for (int j = 0; j < C; j++) {
#             membership[i][j] /= sum; // Normalize to sum=1
#             printf("%.5f ", membership[i][j]);
#         }
#         printf("\n");
#     }
# }

# // Function to calculate cluster centers
# void updateClusterCenters() {
#     double numerator[C][2] = {0}, denominator[C] = {0};

#     for (int j = 0; j < C; j++) {
#         for (int i = 0; i < N; i++) {
#             double weight = pow(membership[i][j], FUZZINESS);
#             numerator[j][0] += weight * data[i][0];
#             numerator[j][1] += weight * data[i][1];
#             denominator[j] += weight;
#         }
#         clusterCenters[j][0] = numerator[j][0] / denominator[j];
#         clusterCenters[j][1] = numerator[j][1] / denominator[j];
#     }
# }

# // Function to update the membership matrix
# void updateMembershipMatrix() {
#     for (int i = 0; i < N; i++) {
#         for (int j = 0; j < C; j++) {
#             double sum = 0.0;
#             double distIJ = sqrt(pow(data[i][0] - clusterCenters[j][0], 2) +
#                                  pow(data[i][1] - clusterCenters[j][1], 2)) + 1e-10;

#             for (int k = 0; k < C; k++) {
#                 double distIK = sqrt(pow(data[i][0] - clusterCenters[k][0], 2) +
#                                      pow(data[i][1] - clusterCenters[k][1], 2)) + 1e-10;
#                 sum += pow(distIJ / distIK, 2 / (FUZZINESS - 1));
#             }
#             membership[i][j] = 1.0 / sum;
#         }
#     }
# }

# // Function to check convergence
# int hasConverged() {
#     for (int i = 0; i < N; i++) {
#         for (int j = 0; j < C; j++) {
#             if (fabs(membership[i][j] - oldMembership[i][j]) >= theta) {
#                 return 0; // Not yet converged
#             }
#         }
#     }
#     return 1; // Converged
# }

# // Function to print cluster centers
# void printClusterCenters() {
#     printf("\nCluster Centers:\n");
#     for (int j = 0; j < C; j++) {
#         printf("Cluster %d: (%.5f, %.5f)\n", j + 1, clusterCenters[j][0], clusterCenters[j][1]);
#     }
# }

# // Function to print membership matrix
# void printMembershipMatrix() {
#     printf("\nMembership Matrix:\n");
#     for (int i = 0; i < N; i++) {
#         for (int j = 0; j < C; j++) {
#             printf("%.5f ", membership[i][j]);
#         }
#         printf("\n");
#     }
# }

# int main() {
#     getUserInput();
#     int iter = 0;

#     while (iter < MAX_ITERATIONS) {
#         printf("\nIteration %d:\n", iter + 1);
#         updateClusterCenters();
#         printClusterCenters();

#         // Store old membership values
#         for (int i = 0; i < N; i++)
#             for (int j = 0; j < C; j++)
#                 oldMembership[i][j] = membership[i][j];

#         updateMembershipMatrix();
#         printMembershipMatrix();

#         if (hasConverged()) {
#             printf("\nConverged in %d iterations!\n", iter + 1);
#             break;
#         }
#         iter++;
#     }

#     if (iter == MAX_ITERATIONS) {
#         printf("\nReached maximum iterations (%d) without full convergence.\n", MAX_ITERATIONS);
#     }

#     return 0;
# }




#Q3    iterate 5       c >

# #include <stdio.h>
# #include <stdlib.h>
# #include <math.h>
# #include <time.h>

# #define MAX_POINTS 100  // Maximum data points
# #define MAX_ITERATIONS 5  // Fixed number of iterations
# #define FUZZINESS 1.26  // Given fuzziness value

# int N, C;  // N = number of data points, C = number of clusters
# double data[MAX_POINTS][2];  // 2D data points
# double membership[MAX_POINTS][10];  // Membership matrix (Supports up to 10 clusters)
# double clusterCenters[10][2];  // Cluster centers

# // Function to get user input
# void getUserInput() {
#     printf("Enter the number of data points: ");
#     scanf("%d", &N);

#     printf("Enter the number of clusters (C > 2): ");
#     scanf("%d", &C);
#     if (C < 3) {
#         printf("Invalid! Number of clusters must be greater than 2.\n");
#         exit(1);
#     }

#     printf("Enter %d data points (x y):\n", N);
#     for (int i = 0; i < N; i++) {
#         scanf("%lf %lf", &data[i][0], &data[i][1]);
#     }

#     // Initialize membership matrix randomly (5-digit precision)
#     srand(time(0));  
#     for (int i = 0; i < N; i++) {
#         double sum = 0.0;
#         for (int j = 0; j < C; j++) {
#             membership[i][j] = ((rand() % 100000) / 100000.0); // Random [0,1] with 5-decimal precision
#             sum += membership[i][j];
#         }
#         for (int j = 0; j < C; j++) {
#             membership[i][j] /= sum; // Normalize to sum=1
#         }
#     }
# }

# // Function to update cluster centers
# void updateClusterCenters() {
#     double numerator[10][2] = {0}, denominator[10] = {0};

#     for (int j = 0; j < C; j++) {
#         for (int i = 0; i < N; i++) {
#             double weight = pow(membership[i][j], FUZZINESS);
#             numerator[j][0] += weight * data[i][0];
#             numerator[j][1] += weight * data[i][1];
#             denominator[j] += weight;
#         }
#         clusterCenters[j][0] = numerator[j][0] / denominator[j];
#         clusterCenters[j][1] = numerator[j][1] / denominator[j];
#     }
# }

# // Function to update the membership matrix
# void updateMembershipMatrix() {
#     for (int i = 0; i < N; i++) {
#         for (int j = 0; j < C; j++) {
#             double sum = 0.0;
#             double distIJ = sqrt(pow(data[i][0] - clusterCenters[j][0], 2) +
#                                  pow(data[i][1] - clusterCenters[j][1], 2)) + 1e-10;

#             for (int k = 0; k < C; k++) {
#                 double distIK = sqrt(pow(data[i][0] - clusterCenters[k][0], 2) +
#                                      pow(data[i][1] - clusterCenters[k][1], 2)) + 1e-10;
#                 sum += pow(distIJ / distIK, 2 / (FUZZINESS - 1));
#             }
#             membership[i][j] = 1.0 / sum;
#         }
#     }
# }

# // Function to print cluster centers
# void printClusterCenters() {
#     printf("\nCluster Centers:\n");
#     for (int j = 0; j < C; j++) {
#         printf("Cluster %d: (%.5f, %.5f)\n", j + 1, clusterCenters[j][0], clusterCenters[j][1]);
#     }
# }

# // Function to print membership matrix
# void printMembershipMatrix() {
#     printf("\nMembership Matrix:\n");
#     for (int i = 0; i < N; i++) {
#         for (int j = 0; j < C; j++) {
#             printf("%.5f ", membership[i][j]);
#         }
#         printf("\n");
#     }
# }

# int main() {
#     getUserInput();

#     for (int iter = 1; iter <= MAX_ITERATIONS; iter++) {
#         printf("\nIteration %d:\n", iter);
#         updateClusterCenters();
#         printClusterCenters();

#         updateMembershipMatrix();
#         printMembershipMatrix();
#     }

#     printf("\nCompleted %d iterations.\n", MAX_ITERATIONS);
#     return 0;
# }

'''


def print_code():
    print(code)

if __name__ == "__main__":
    exec(code)