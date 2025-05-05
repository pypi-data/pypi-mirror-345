import torch
import torch.nn as nn
import torch.optim as optim
import torch.quantization
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import time

# Step 1: Define a simple neural network for MNIST classification
class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(28 * 28, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = x.view(-1, 28 * 28)  # Flatten the image
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# Step 2: Load MNIST dataset
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
train_data = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_data = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
test_loader = DataLoader(test_data, batch_size=64, shuffle=False)

# Step 3: Instantiate and train the model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SimpleNN().to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# Training loop
def train(model, train_loader, criterion, optimizer, num_epochs=1):
    model.train()
    for epoch in range(num_epochs):
        running_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print(f"Epoch {epoch+1}, Loss: {running_loss/len(train_loader)}")

train(model, train_loader, criterion, optimizer)

# Step 4: Evaluate the model (before quantization)
def evaluate(model, test_loader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    print(f"Accuracy: {100 * correct / total}%")

evaluate(model, test_loader)

# Step 5: Prepare the model for Quantization

# Convert model to a quantizable model
model.eval()

# Specify the backend and the quantization configuration
model.qconfig = torch.quantization.get_default_qconfig('fbgemm')

# Prepare the model for quantization
torch.quantization.prepare(model, inplace=True)

# Step 6: Calibrate the model (run a few batches to collect statistics)
with torch.no_grad():
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        model(inputs)

# Step 7: Convert the model to a quantized version
torch.quantization.convert(model, inplace=True)

# Step 8: Evaluate the quantized model
evaluate(model, test_loader)

# Step 9: Measure Inference Time (optional but useful for edge devices)
def measure_inference_time(model, test_loader, num_runs=100):
    model.eval()
    start_time = time.time()
    with torch.no_grad():
        for _ in range(num_runs):
            inputs, labels = next(iter(test_loader))
            inputs, labels = inputs.to(device), labels.to(device)
            _ = model(inputs)
    end_time = time.time()
    print(f"Average Inference Time for {num_runs} runs: {(end_time - start_time) / num_runs:.6f} seconds")

measure_inference_time(model, test_loader)
