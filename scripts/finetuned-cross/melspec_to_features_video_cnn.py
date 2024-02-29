# -*- coding: utf-8 -*-
"""melspec_to_features_video_cnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1F5lenT4KPtyyDCW8sMP8N3y0NTfptG3h
"""

# from google.colab import drive
# drive.mount('/content/drive')

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
from sklearn.model_selection import train_test_split
import numpy as np
from tqdm import tqdm

class CNN(nn.Module):
    def __init__(self, num_classes):
        super(CNN, self).__init__()
        self.features = models.resnet18(weights='DEFAULT')
        # Modify the first layer to accept 1 channel input (for grayscale spectrograms)
        self.features.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        # Modify the final layer to output desired feature size
        self.features.fc = nn.Linear(self.features.fc.in_features, num_classes)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = self.features(x)
        x = self.softmax(x)
        return x

def preprocess_image(image_path):
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # Resize to match ResNet input size
        transforms.ToTensor(),           # Convert to tensor
    ])
    img_tensor = transform(img)
    # img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension
    return img_tensor

def load_dataset(input_folder):
    X = []
    y = []
    # List all files in the input folder
    files = os.listdir(input_folder)
    # Iterate over files in the folder
    for filename in files:
        if filename.endswith(".png"):  # Assuming mel spectrograms are stored as PNG files
            input_path = os.path.join(input_folder, filename)
            img_tensor = preprocess_image(input_path)
            X.append(img_tensor)
            # Extract label from filename (assuming filename is in format "abc_IEO_label_xyz.png")
            label = filename.split("_")[2]
            if label == "HAP":
                y.append(0)
            elif label == "SAD":
                y.append(1)
            elif label == "ANG":
                y.append(2)
    return X, y

def train_model(model, criterion, optimizer, train_loader, device):
    model.train()
    running_loss = 0.0
    correct_preds = 0
    total_preds = 0
    for inputs, labels in tqdm(train_loader):
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * inputs.size(0)
        _, predicted = torch.max(outputs, 1)
        correct_preds += (predicted == labels).sum().item()
        total_preds += labels.size(0)

    epoch_loss = running_loss / len(train_loader.dataset)
    accuracy = correct_preds / total_preds
    return epoch_loss, accuracy

def test_model(model, criterion, test_loader, device):
    model.eval()
    running_loss = 0.0
    correct_preds = 0
    total_preds = 0
    with torch.no_grad():
        for inputs, labels in tqdm(test_loader):
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            correct_preds += (predicted == labels).sum().item()
            total_preds += labels.size(0)
    epoch_loss = running_loss / len(test_loader.dataset)
    accuracy = correct_preds / total_preds
    return epoch_loss, accuracy

# def extract_features_from_folder(input_folder):
#     # Initialize the model
#     model = CNN(num_classes=3)  # 3 classes for HAPPY, SAD, ANGRY
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model.to(device)
#     model.eval()  # Set the model to evaluation mode

#     # List all files in the input folder
#     files = os.listdir(input_folder)

#     # Iterate over files in the folder
#     for filename in files:
#         if filename.endswith(".png"):  # Assuming mel spectrograms are stored as PNG files
#             input_path = os.path.join(input_folder, filename)
#             img_tensor = preprocess_image(input_path)
#             img_tensor = img_tensor.to(device)
#             with torch.no_grad():
#                 output_features = model(img_tensor)
#             print(f"Features extracted for {filename}: {output_features}")

# extract_features_from_folder('/content/drive/MyDrive/csci535/melspec')

# !python3 melspec_to_features_cnn.py /content/drive/MyDrive/csci535/melspec

if __name__ == "__main__":
    Check if input arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python melspec_to_features_cnn.py input_folder model")
        sys.exit(1)

    input_folder = sys.argv[1]
    cross_model = sys.argv[2]
    # input_folder = '/content/drive/MyDrive/csci535/melspec'
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print("Input folder does not exist.")
        sys.exit(1)

    # Check if model exists
    if not os.path.exists(cross_model):
        print("Model does not exist.")
        sys.exit(1)

    # Load dataset and split into train and test sets
    X, y = load_dataset(input_folder)
    print(f"Total number of samples: {len(X)}")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    print(f"Number of train samples: {len(X_train)}", f"Number of test samples: {len(X_test)}")
    # Initialize the model
    model = CNN(num_classes=3)  # 3 classes for HAPPY, SAD, ANGRY
    # Load the saved state dictionary
    # state_dict = torch.load('/content/drive/MyDrive/csci535/models/ResNet18_melspec_50_32_0.001')
    # state_dict = torch.load('/content/drive/MyDrive/csci535/models/ResNet18_video_50_32_0.001')
    state_dict = torch.load(cross_model)
    
    # Load the state dictionary into the model
    model.load_state_dict(state_dict)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Define loss function and optimizer
    _lr = 0.001
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=_lr)

    # Create data loaders
    _bs = 32
    # train_loader = torch.utils.data.DataLoader(list(zip(X_train, y_train)), batch_size=_bs, shuffle=True)
    test_loader = torch.utils.data.DataLoader(list(zip(X_test, y_test)), batch_size=_bs)
    print(f"Batch size: {_bs}", f"lr: {_lr}")
    # Training loop
    # num_epochs = 50
    # for epoch in range(num_epochs):
    #     print("Epoch " + str(epoch))
    #     train_loss, train_accuracy = train_model(model, criterion, optimizer, train_loader, device)
    #     test_loss, test_accuracy = test_model(model, criterion, test_loader, device)
    #     print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Train Accuracy: {train_accuracy:.4f}, Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.4f}")
    test_loss, test_accuracy = test_model(model, criterion, test_loader, device)
    print(f"Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.4f}")

# torch.save(model.state_dict(), 'ResNet18_melspec_'+str(num_epochs)+'_'+str(_bs)+'_'+str(_lr))

# ! ls -lh /content/

# !cp '/content/ResNet18_melspec_50_32_0.001' '/content/drive/MyDrive/csci535/models'

