#CL_1
text = '''import numpy as np

# Fuzzy Set Operations
def union(A, B):
    return np.maximum(A, B)

def intersection(A, B):
    return np.minimum(A, B)

def complement(A):
    return 1 - A

def difference(A, B):
    return np.maximum(A - B, 0)

# Fuzzy Relation - Cartesian Product
def cartesian_product(A, B):
    return np.outer(A, B)

# Max-Min Composition of Two Fuzzy Relations
def max_min_composition(R1, R2):
    result = np.zeros((R1.shape[0], R2.shape[1]))
    for i in range(R1.shape[0]):
        for j in range(R2.shape[1]):
            result[i, j] = np.max(np.minimum(R1[i, :], R2[:, j]))
    return result

# Example fuzzy sets A and B
A = np.array([0.2, 0.4, 0.7, 0.8])
B = np.array([0.1, 0.8, 0.2, 0.3])

# Perform Operations
print("Fuzzy Set A:", A)
print("Fuzzy Set B:", B)
print("Union of A and B:", union(A, B))
print("Intersection of A and B:", intersection(A, B))
print("Complement of A:", complement(A))
print("Difference (A - B):", difference(A, B))

# Cartesian Products
R1 = cartesian_product(A, B)
R2 = cartesian_product(B, A)

print("\nCartesian product (A x B):\n", R1)
print("Cartesian product (B x A):\n", R2)

# Max-Min Composition
composition_result = max_min_composition(R1, R2)
print("\nMax-Min Composition of R1 and R2:\n", composition_result)'''

print(text)
