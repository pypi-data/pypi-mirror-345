class NN:
    codes = [
        '''
import numpy as np
import matplotlib.pyplot as plt

x = np.array([1, 2, 3, 4, 5])
y = np.array([10, 12, 14, 16, 18])

coeff = np.polyfit(x, y, 2)
poly = np.poly1d(coeff)

plt.scatter(x, y)
x_line = np.linspace(min(x), max(x), 100)
y_fit = poly(x_line)
plt.plot(x_line, y_fit)
plt.show()

for i in range(6, 10):
    new_x = i
    predicted_y = poly(new_x)
    print(f"For x = {new_x} predicted y is {predicted_y}")
        ''',
        '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris

iris = load_iris()
df = pd.DataFrame(data=iris.data, columns=iris.feature_names)

x = df['sepal length (cm)']
y = df['sepal width (cm)']

coeff = np.polyfit(x, y, 2)
poly = np.poly1d(coeff)

x_line = np.linspace(x.min(), x.max(), 100)
y_fit = poly(x_range)
plt.scatter(x, y)
plt.plot(x_range, y_fit)

plt.xlabel('Sepal Length (cm)')
plt.ylabel('Sepal Width (cm)')
plt.title('Polynomial Curve Fitting on Iris Dataset')
plt.show()
        ''',
        '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris

iris = load_iris()
df = pd.DataFrame(data=iris.data, columns=iris.feature_names)

x = df['sepal length (cm)']
y = df['sepal width (cm)']

noise = np.random.normal(0, 0.2, size=y.shape) 
y_noisy = y + noise

coeff = np.polyfit(x, y_noisy, 2)
poly = np.poly1d(coeff)

x_line = np.linspace(x.min(), x.max(), 100)
y_fit = poly(x_line)

plt.scatter(x, y_noisy)
plt.plot(x_line, y_fit)

plt.xlabel('Sepal Length (cm)')
plt.ylabel('Sepal Width (cm)')
plt.title('Polynomial Curve Fitting on Noisy Iris Dataset')
plt.show()
        ''',
        '''
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input

X = np.array([
    [0.0, 0.0],
    [0.0, 1.0],
    [1.0, 0.0],
    [1.0, 1.0]
])

y = np.array([
    [0.0, 1.0],
    [1.0, 0.0],
    [1.0, 0.0],
    [0.0, 1.0]
])

model = Sequential([
    Input(shape=(2,)),
    Dense(8, activation='relu'),
    Dense(8, activation='relu'),
    Dense(2, activation='linear')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
    loss='mse',
    metrics=['mae']
)

history = model.fit(X, y, epochs=100, verbose=0)

loss, mae = model.evaluate(X, y, verbose=0)
print(f"\nFinal Loss: {loss:.6f}, Final MAE: {mae:.6f}")

predictions = model.predict(X)
print("\nPredictions:")
print(predictions)

print("\nRounded Predictions (close to 0 or 1):")
print(np.round(predictions))
        ''',
        '''
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input

X = np.array([
    [0.0, 0.0],
    [0.0, 1.0],
    [1.0, 0.0],
    [1.0, 1.0]
])

y = np.array([
    [1, 0], 
    [0, 1],  
    [0, 1],  
    [1, 0] 
])

model = Sequential([
    Input(shape=(2,)),
    Dense(8, activation='relu'),
    Dense(8, activation='relu'),
    Dense(2, activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history = model.fit(X, y, epochs=50, verbose=0)

loss, accuracy = model.evaluate(X, y, verbose=0)
print(f"\nFinal Loss: {loss:.6f}, Final Accuracy: {accuracy:.6f}")

predictions = model.predict(X)
print("\nPredicted Probabilities:")
print(predictions)

print("\nPredicted Classes (argmax):")
print(np.argmax(predictions, axis=1))
        ''',
        '''
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input

X = np.array([
    [0.0, 0.0],
    [0.0, 1.0],
    [1.0, 0.0],
    [1.0, 1.0]
])

y = np.array([
    [0.0, 1.0],
    [0.0, 1.0], 
    [0.0, 1.0],
    [1.0, 0.0] 
])

model = Sequential([
    Input(shape=(2,)),
    Dense(8, activation='relu'),
    Dense(8, activation='relu'),
    Dense(2, activation='linear')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
    loss='mse',
    metrics=['mae']
)

history = model.fit(X, y, epochs=450, verbose=0)

loss, mae = model.evaluate(X, y, verbose=0)
print(f"\nFinal Loss: {loss:.6f}, Final MAE: {mae:.6f}")

@tf.function
def make_predictions(model, data):
    return model(data)

predictions = make_predictions(model, X)
print("\nPredictions (AND, NAND):")
print(predictions.numpy())

print("\nRounded Predictions (close to 0 or 1):")
print(np.round(predictions.numpy()))
        ''',
        '''
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input

X = np.array([
    [0.0, 0.0],
    [0.0, 1.0],
    [1.0, 0.0],
    [1.0, 1.0]
])

y = np.array([0, 0, 0, 1]) 

model = Sequential([
    Input(shape=(2,)),
    Dense(8, activation='relu'),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

history = model.fit(X, y, epochs=50, verbose=0)

loss, accuracy = model.evaluate(X, y, verbose=0)
print(f"\nFinal Loss: {loss:.6f}, Final Accuracy: {accuracy:.6f}")

predictions = model.predict(X)
print("\nPredictions (probabilities for NAND):")
print(predictions)

predicted_classes = (predictions > 0.5).astype(int)
print("\nPredicted Classes (0 = AND, 1 = NAND):")
print(predicted_classes)
        ''',
        '''
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt

(X_train, y_train), (X_test, y_test) = tf.keras.datasets.mnist.load_data()

X_train = X_train / 255.0
X_test = X_test / 255.0

model = models.Sequential([
    layers.Flatten(input_shape=(28, 28)),  
    layers.Dense(128, activation='relu'), 
    layers.Dense(10, activation='softmax') 
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

history = model.fit(X_train, y_train, epochs=5, validation_split=0.2)

test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"\nTest Accuracy: {test_acc*100:.2f}%")

y_pred_probs = model.predict(X_test)
y_pred_classes = np.argmax(y_pred_probs, axis=1)

plt.imshow(X_test[0], cmap='gray')
plt.title(f"True: {y_test[0]} | Predicted: {y_pred_classes[0]}")
plt.axis('off')
plt.show()
        ''',
        '''
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

transform = transforms.Compose([
    transforms.ToTensor(), 
    transforms.Normalize((0.5,), (0.5,))
])

train_dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(28*28, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 10)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.view(x.size(0), -1)  
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x) 
        return x

model = SimpleNN()
loss_fn = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

epochs = 5

for epoch in range(epochs):
    model.train()
    total_loss = 0

    for images, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = loss_fn(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(train_loader):.4f}")

model.eval()
correct = 0
total = 0

with torch.no_grad():
    for images, labels in test_loader:
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

accuracy = 100 * correct / total
print(f"Test Accuracy: {accuracy:.2f}%")

images, labels = next(iter(test_loader))
outputs = model(images)
_, predicted = torch.max(outputs, 1)

plt.imshow(images[0].squeeze(), cmap='gray')
plt.title(f"True: {labels[0].item()} | Predicted: {predicted[0].item()}")
plt.axis('off')
plt.show()
        ''',
        '''
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np

class SimpleNN(nn.Module):
    def __init__(self, activation_function='relu'):
        super(SimpleNN, self).__init__()

        if activation_function == 'relu':
            self.activation = nn.ReLU()
        elif activation_function == 'tanh':
            self.activation = nn.Tanh()

        self.layer1 = nn.Linear(2, 2)
        self.output_layer = nn.Linear(2, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.activation(self.layer1(x))
        x = self.sigmoid(self.output_layer(x))
        return x

def train_model(model, X_train_tensor, y_train_tensor, lr, momentum):
    criterion = nn.BCELoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)

    for epoch in range(50):
        model.train()
        optimizer.zero_grad()
        output = model(X_train_tensor)
        loss = criterion(output, y_train_tensor)
        loss.backward()
        optimizer.step()

    return model

def optimize_hyperparameters(X_train_tensor, y_train_tensor):
    best_accuracy = 0
    best_params = {}

    learning_rates = [0.01, 0.1]
    momenta = [0.5, 0.9]
    activations = ['relu', 'tanh']

    for lr in learning_rates:
        for momentum in momenta:
            for activation in activations:
                print(f"Training with lr={lr}, momentum={momentum}, activation={activation}")

                model = SimpleNN(activation_function=activation)
                trained_model = train_model(model, X_train_tensor, y_train_tensor, lr, momentum)

                with torch.no_grad():
                    model.eval()
                    output = trained_model(X_train_tensor)
                    predicted = (output > 0.5).float()
                    accuracy = (predicted == y_train_tensor).float().mean()

                print(f"Accuracy: {accuracy.item():.4f}")

                if accuracy.item() > best_accuracy:
                    best_accuracy = accuracy.item()
                    best_params = {
                        'learning_rate': lr,
                        'momentum': momentum,
                        'activation_function': activation
                    }

    return best_params, best_accuracy

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [0], [0], [1]])

X_train_tensor = torch.tensor(X, dtype=torch.float32)
y_train_tensor = torch.tensor(y, dtype=torch.float32)

best_params, best_accuracy = optimize_hyperparameters(X_train_tensor, y_train_tensor)

print("\nBest Hyperparameters:")
print(f"Learning Rate: {best_params['learning_rate']}")
print(f"Momentum: {best_params['momentum']}")
print(f"Activation Function: {best_params['activation_function']}")
print(f"Best Accuracy: {best_accuracy:.4f}")
        ''',
        '''
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class SimpleNN(nn.Module):
    def __init__(self, activation_function='relu'):
        super(SimpleNN, self).__init__()

        if activation_function == 'relu':
            self.activation = nn.ReLU()
        elif activation_function == 'tanh':
            self.activation = nn.Tanh()

        self.layer1 = nn.Linear(1, 2)
        self.layer2 = nn.Linear(2, 1)

    def forward(self, x):
        x = self.activation(self.layer1(x))
        x = self.layer2(x)
        return x

def train_model(model, X_train_tensor, y_train_tensor, lr, momentum):
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)

    for epoch in range(100):
        model.train()
        optimizer.zero_grad()
        output = model(X_train_tensor)
        loss = criterion(output, y_train_tensor)
        loss.backward()
        optimizer.step()

    return model

def optimize_hyperparameters(X_train_tensor, y_train_tensor):
    best_rmse = float('inf')
    best_params = {}

    learning_rates = [0.01, 0.1, 0.001]
    momenta = [0.5, 0.9]
    activations = ['relu', 'tanh']

    for lr in learning_rates:
        for momentum in momenta:
            for activation in activations:
                print(f"Training with lr={lr}, momentum={momentum}, activation={activation}")

                model = SimpleNN(activation_function=activation)
                trained_model = train_model(model, X_train_tensor, y_train_tensor, lr, momentum)

                with torch.no_grad():
                    model.eval()
                    output = trained_model(X_train_tensor)
                    rmse = torch.sqrt(nn.MSELoss()(output, y_train_tensor))

                print(f"RMSE: {rmse.item():.4f}")

                if rmse.item() < best_rmse:
                    best_rmse = rmse.item()
                    best_params = {
                        'learning_rate': lr,
                        'momentum': momentum,
                        'activation_function': activation
                    }

    return best_params, best_rmse

X = np.array([[1], [2], [3], [4], [5]])
y = np.array([[2], [4], [6], [8], [10]])

X_train_tensor = torch.tensor(X, dtype=torch.float32)
y_train_tensor = torch.tensor(y, dtype=torch.float32)

best_params, best_rmse = optimize_hyperparameters(X_train_tensor, y_train_tensor)

print("\nBest Hyperparameters:")
print(f"Learning Rate: {best_params['learning_rate']}")
print(f"Momentum: {best_params['momentum']}")
print(f"Activation Function: {best_params['activation_function']}")
print(f"Best RMSE: {best_rmse:.4f}")
        ''',
        '''
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class SimpleNN(nn.Module):
    def __init__(self, activation_function='relu'):
        super(SimpleNN, self).__init__()

        if activation_function == 'relu':
            self.activation = nn.ReLU()
        elif activation_function == 'tanh':
            self.activation = nn.Tanh()

        self.layer1 = nn.Linear(1, 2)
        self.layer2 = nn.Linear(2, 1)

    def forward(self, x):
        x = self.activation(self.layer1(x))
        x = self.layer2(x)
        return x

def train_model(model, X_train_tensor, y_train_tensor, lr, momentum):
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)

    for epoch in range(100):
        model.train()
        optimizer.zero_grad()
        output = model(X_train_tensor)
        loss = criterion(output, y_train_tensor)
        loss.backward()
        optimizer.step()

    return model

def optimize_hyperparameters(X_train_tensor, y_train_tensor):
    best_rmse = float('inf')
    best_params = {}

    learning_rates = [0.01, 0.1, 0.001]
    momenta = [0.5, 0.9]
    activations = ['relu', 'tanh']

    for lr in learning_rates:
        for momentum in momenta:
            for activation in activations:
                print(f"Training with lr={lr}, momentum={momentum}, activation={activation}")

                model = SimpleNN(activation_function=activation)
                trained_model = train_model(model, X_train_tensor, y_train_tensor, lr, momentum)

                with torch.no_grad():
                    model.eval()
                    output = trained_model(X_train_tensor)
                    rmse = torch.sqrt(nn.MSELoss()(output, y_train_tensor))

                print(f"RMSE: {rmse.item():.4f}")

                if rmse.item() < best_rmse:
                    best_rmse = rmse.item()
                    best_params = {
                        'learning_rate': lr,
                        'momentum': momentum,
                        'activation_function': activation
                    }

    return best_params, best_rmse

X = np.array([[1], [2], [3], [4], [5]])
y = np.array([[2], [4], [6], [8], [10]])

X_train_tensor = torch.tensor(X, dtype=torch.float32)
y_train_tensor = torch.tensor(y, dtype=torch.float32)

best_params, best_rmse = optimize_hyperparameters(X_train_tensor, y_train_tensor)

print("\nBest Hyperparameters:")
print(f"Learning Rate: {best_params['learning_rate']}")
print(f"Momentum: {best_params['momentum']}")
print(f"Activation Function: {best_params['activation_function']}")
print(f"Best RMSE: {best_rmse:.4f}")
        ''',
        '''
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import random

class SimpleNN(nn.Module):
    def __init__(self, input_size, hidden_size, activation_function='relu'):
        super(SimpleNN, self).__init__()

        if activation_function == 'relu':
            self.activation = nn.ReLU()
        elif activation_function == 'tanh':
            self.activation = nn.Tanh()

        self.layer1 = nn.Linear(input_size, hidden_size)
        self.layer2 = nn.Linear(hidden_size, 1)

    def forward(self, x):
        x = self.activation(self.layer1(x))
        x = self.layer2(x)
        return x

def train_model(model, X_train_tensor, y_train_tensor, lr, batch_size, epochs=100):
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=lr)

    model.train()
    for epoch in range(epochs):
        permutation = torch.randperm(X_train_tensor.size(0))

        for i in range(0, X_train_tensor.size(0), batch_size):
            indices = permutation[i:i+batch_size]
            batch_x, batch_y = X_train_tensor[indices], y_train_tensor[indices]

            optimizer.zero_grad()
            output = model(batch_x)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()

    return model

def random_search_hyperparameters(X_train_tensor, y_train_tensor, num_trials=10):
    best_rmse = float('inf')
    best_params = {}

    learning_rates = [0.01, 0.1, 0.001]
    batch_sizes = [8, 16, 32]
    hidden_sizes = [4, 8, 16]
    activations = ['relu', 'tanh']

    for trial in range(num_trials):
        lr = random.choice(learning_rates)
        batch_size = random.choice(batch_sizes)
        hidden_size = random.choice(hidden_sizes)
        activation = random.choice(activations)

        print(f"Trial {trial+1}: Training with lr={lr}, batch_size={batch_size}, hidden_size={hidden_size}, activation={activation}")

        model = SimpleNN(input_size=X_train_tensor.shape[1], hidden_size=hidden_size, activation_function=activation)

        trained_model = train_model(model, X_train_tensor, y_train_tensor, lr, batch_size)

        with torch.no_grad():
            model.eval()
            output = trained_model(X_train_tensor)
            rmse = torch.sqrt(nn.MSELoss()(output, y_train_tensor))

        print(f"RMSE: {rmse.item():.4f}")

        if rmse.item() < best_rmse:
            best_rmse = rmse.item()
            best_params = {
                'learning_rate': lr,
                'batch_size': batch_size,
                'hidden_size': hidden_size,
                'activation_function': activation
            }

    return best_params, best_rmse

X, y = make_regression(n_samples=100, n_features=5, noise=0.1, random_state=42)

scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train_tensor = torch.tensor(X, dtype=torch.float32)
y_train_tensor = torch.tensor(y, dtype=torch.float32).view(-1, 1)

best_params, best_rmse = random_search_hyperparameters(X_train_tensor, y_train_tensor, num_trials=10)

print("\nBest Hyperparameters:")
print(f"Learning Rate: {best_params['learning_rate']}")
print(f"Batch Size: {best_params['batch_size']}")
print(f"Hidden Size: {best_params['hidden_size']}")
print(f"Activation Function: {best_params['activation_function']}")
print(f"Best RMSE: {best_rmse:.4f}")
        ''',
        '''
import sympy as sp

def compute_hessian(f, variables):

    gradient = [sp.diff(f, var) for var in variables]
    hessian = sp.Matrix([[sp.diff(gradient[i], var) for var in variables]
                         for i in range(len(variables))])

    return hessian

if __name__ == "__main__":

    x, y, z = sp.symbols('x y z')
    f = 2*x*2 + 3*x*y + 10*y2 + 8*y*z + 2*z*3
    variables = [x, y, z]
    hessian = compute_hessian(f, variables)
    print("Hessian matrix:")
    sp.print(hessian)
        ''',
        '''
import numpy as np
from scipy.linalg import eigh

def objective_function(x):
    return 2*x[0]*2 + 3*x[0]*x[1] + 10*x[1]2 + 8*x[1]*x[2] + 2*x[2]*3

def compute_hessian_fd(f, x, h=1e-5):
    n = len(x)
    hessian = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            x1 = x.copy(); x1[i] += h; x1[j] += h
            x2 = x.copy(); x2[i] += h; x2[j] -= h
            x3 = x.copy(); x3[i] -= h; x3[j] += h
            x4 = x.copy(); x4[i] -= h; x4[j] -= h
            hessian[i, j] = (f(x1) - f(x2) - f(x3) + f(x4)) / (4*h**2)
    return hessian

def analyze_hessian(hessian):
    rounded_hessian = np.round(hessian, 3)
    print("\nHessian Matrix:")
    print(rounded_hessian)

    is_symmetric = np.allclose(hessian, hessian.T)
    print("Is Symmetric:", is_symmetric)

    eigenvalues = eigh(hessian, eigvals_only=True)
    print("Eigenvalues:", np.round(eigenvalues, 5))

    is_positive_definite = np.all(eigenvalues > 0)
    print("Is Positive Definite:", is_positive_definite)

    determinant = np.linalg.det(hessian)
    print("Determinant of Hessian:", round(determinant, 5))

    if is_positive_definite:
        print("→ The function has a local minimum at the point.")
    elif np.all(eigenvalues < 0):
        print("→ The function has a local maximum at the point.")
    else:
        print("→ The function has a saddle point at the point.")

if __name__ == "__main__":
    point = np.array([1.0, 1.0, 1.0])  # Evaluation point
    hessian = compute_hessian_fd(objective_function, point)
    analyze_hessian(hessian)
        ''',
        '''
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score

iris = load_iris()
X = iris.data
y = iris.target

X = X[y != 2]
y = y[y != 2]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.long)

class BNN(nn.Module):
    def __init__(self):
        super(BNN, self).__init__()
        self.fc1 = nn.Linear(4, 64)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(64, 2)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return torch.softmax(x, dim=-1)

model = BNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 100
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_tensor)
    loss = criterion(outputs, y_train_tensor)
    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch [{epoch}/{num_epochs}], Loss: {loss.item():.4f}")

model.eval()
with torch.no_grad():
    y_pred_prob = model(X_test_tensor)
    y_pred = torch.argmax(y_pred_prob, dim=1)

accuracy = accuracy_score(y_test_tensor.numpy(), y_pred.numpy())
precision = precision_score(y_test_tensor.numpy(), y_pred.numpy())
recall = recall_score(y_test_tensor.numpy(), y_pred.numpy())

print("\nEvaluation Metrics:")
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
        ''',
        '''
 import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from torch.utils.data import DataLoader, TensorDataset

iris = load_iris()
X = iris.data
y = iris.target

X = X[y != 2]
y = y[y != 2]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.long)

class RegularizedNN(nn.Module):
    def __init__(self):
        super(RegularizedNN, self).__init__()
        self.fc1 = nn.Linear(4, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 2)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return torch.softmax(x, dim=-1)

best_val_loss = float('inf')
early_stop_count = 0
patience = 10

model = RegularizedNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=0.01)

def add_noise(X, noise_factor=0.1):
    return X + noise_factor * torch.randn_like(X)

num_epochs = 100
for epoch in range(num_epochs):
    model.train()

    X_train_augmented = add_noise(X_train_tensor)

    outputs = model(X_train_augmented)
    loss = criterion(outputs, y_train_tensor)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    model.eval()
    with torch.no_grad():
        val_outputs = model(X_test_tensor)
        val_loss = criterion(val_outputs, y_test_tensor)

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        early_stop_count = 0
    else:
        early_stop_count += 1
        if early_stop_count >= patience:
            print(f"Early stopping at epoch {epoch+1}")
            break

    if epoch % 10 == 0:
        print(f"Epoch [{epoch}/{num_epochs}], Loss: {loss.item():.4f}, Validation Loss: {val_loss.item():.4f}")

model.eval()
with torch.no_grad():
    y_pred_prob = model(X_test_tensor)
    y_pred = torch.argmax(y_pred_prob, dim=1)

accuracy = accuracy_score(y_test_tensor.numpy(), y_pred.numpy())
print(f"\nTest Accuracy: {accuracy:.4f}")
        ''',
        '''
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)
n_samples = 500

mean1, mean2 = [2, 2], [8, 8]
cov1, cov2 = [[1, 0], [0, 1]], [[1, 0], [0, 1]]

X1 = np.random.multivariate_normal(mean1, cov1, n_samples // 2)
X2 = np.random.multivariate_normal(mean2, cov2, n_samples // 2)
X = np.vstack([X1, X2])

n_components = 2
n_features = X.shape[1]

means = np.array([X[np.random.choice(X.shape[0])], X[np.random.choice(X.shape[0])]])
covariances = [np.eye(n_features)] * n_components
weights = np.ones(n_components) / n_components

def e_step(X, means, covariances, weights):
    n_samples, n_components = X.shape[0], len(means)
    gamma = np.zeros((n_samples, n_components))

    for k in range(n_components):
        diff = X - means[k]
        cov_inv = np.linalg.inv(covariances[k])
        exponent = np.diagonal(np.dot(diff, cov_inv) @ diff.T)
        norm_factor = np.linalg.det(covariances[k]) ** 0.5
        density = (1 / (2 * np.pi * norm_factor)) * np.exp(-0.5 * exponent)
        gamma[:, k] = weights[k] * density

    gamma /= np.sum(gamma, axis=1)[:, np.newaxis]
    return gamma

def m_step(X, gamma):
    n_samples, n_components = X.shape[0], gamma.shape[1]
    n_features = X.shape[1]

    means = np.dot(gamma.T, X) / np.sum(gamma, axis=0)[:, np.newaxis]
    covariances = []
    weights = np.sum(gamma, axis=0) / n_samples

    for k in range(n_components):
        diff = X - means[k]
        covariances.append(np.dot(gamma[:, k] * diff.T, diff) / np.sum(gamma[:, k]))

    return means, covariances, weights

def log_likelihood(X, means, covariances, weights):
    n_samples, n_components = X.shape[0], len(means)
    likelihood = np.zeros(n_samples)

    for k in range(n_components):
        diff = X - means[k]
        cov_inv = np.linalg.inv(covariances[k])
        exponent = np.diagonal(np.dot(diff, cov_inv) @ diff.T)
        norm_factor = np.linalg.det(covariances[k]) ** 0.5
        likelihood += weights[k] * (1 / (2 * np.pi * norm_factor)) * np.exp(-0.5 * exponent)

    return np.sum(np.log(likelihood))

max_iter = 100
convergence_threshold = 1e-6
prev_log_likelihood = None

for i in range(max_iter):
    gamma = e_step(X, means, covariances, weights)
    means, covariances, weights = m_step(X, gamma)
    current_log_likelihood = log_likelihood(X, means, covariances, weights)

    if prev_log_likelihood is not None and abs(current_log_likelihood - prev_log_likelihood) < convergence_threshold:
        print(f"Converged at iteration {i+1}")
        break

    prev_log_likelihood = current_log_likelihood

    print(f"Iteration {i+1}: Log Likelihood = {current_log_likelihood:.4f}")

print("\nFinal Parameters:")
print("Means:")
print(means)
print("Covariances:")
for c in covariances:
    print(c)
print("Weights:")
print(weights)

plt.scatter(X[:, 0], X[:, 1], c=np.argmax(gamma, axis=1), cmap='viridis', s=30, alpha=0.5)
plt.scatter(means[:, 0], means[:, 1], c='red', marker='x', label='Means')
plt.legend()
plt.title('EM Algorithm - GMM Clustering')
plt.show()
        ''',
    ]

    @staticmethod
    def text(index):
        """Fetch a specific code based on the index."""
        try:
            return NN.codes[index - 1]
        except IndexError:
            return f"Invalid code index. Please choose a number between 1 and {len(NN.codes)}."
