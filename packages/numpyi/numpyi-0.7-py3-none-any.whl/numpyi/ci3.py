code = '''
import numpy as np
import matplotlib.pyplot as plt

# 1. Generate simple synthetic data
def generate_data(n=200):
    X = np.random.rand(n, 2)  # 2D data (2 features)
    y = ((X[:, 0] > 0.5) & (X[:, 1] > 0.5)).astype(int)  # Label is 1 if both features > 0.5
    return X, y

# 2. NSA (Negative Selection Algorithm) Classifier
class NSAClassifier:
    def __init__(self, num_detectors=50, radius=0.1):
        self.num_detectors = num_detectors  # Number of detectors
        self.radius = radius  # Distance threshold
        self.detectors = []  # List to store detector points

    def train(self, X_self):
        # Generate detectors that are far from "self" (i.e., safe) points
        while len(self.detectors) < self.num_detectors:
            candidate = np.random.rand(2)  # Random 2D point
            if all(np.linalg.norm(candidate - x) > self.radius for x in X_self):
                self.detectors.append(candidate)

    def predict(self, X):
        predictions = []
        for x in X:
            # If close to any detector, classify as "damaged" (1)
            if any(np.linalg.norm(x - d) <= self.radius for d in self.detectors):
                predictions.append(1)
            else:
                predictions.append(0)  # Otherwise, classify as "safe" (0)
        return np.array(predictions)

# 3. Train and test the classifier
X, y = generate_data()  # Generate dataset
split = int(0.8 * len(X))  # 80% training, 20% testing
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

X_self = X_train[y_train == 0]  # Use only "safe" data (label 0) to train detectors

clf = NSAClassifier(num_detectors=50, radius=0.1)
clf.train(X_self)

y_pred = clf.predict(X_test)

# 4. Calculate accuracy
acc = np.mean(y_pred == y_test)
print("Accuracy:", acc)

# 5. Visualize results
plt.figure(figsize=(8, 6))
plt.scatter(X_test[:, 0], X_test[:, 1], c=y_pred, cmap='coolwarm', edgecolor='k', label='Test Data')
plt.scatter(np.array(clf.detectors)[:, 0], np.array(clf.detectors)[:, 1],
            c='green', marker='x', label='Detectors')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('NSA Classifier - Predicted Damage (Red=Damaged, Blue=Safe)')
plt.legend()
plt.grid(True)
plt.show()
'''

print(code)