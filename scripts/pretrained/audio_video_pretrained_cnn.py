# -*- coding: utf-8 -*-
"""audio_video_pretrained_cnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14Tm2TmPyW6FTs3SVixofnbL4Q3ddr1pk
"""

# from google.colab import drive
# drive.mount('/content/drive')

# !python3 -m pip install facenet-pytorch
# !python3 -m pip install face_alignment

import cv2
import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
from facenet_pytorch import MTCNN
from sklearn.model_selection import train_test_split
import numpy as np
from tqdm import tqdm
import face_alignment
import dlib
import requests

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

def extract_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    mid_frame_index = frame_count // 2  # Index of the frame in the middle of the video
    cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame_index)
    ret, frame = cap.read()
    if ret:
        cap.release()
        return frame
    else:
        cap.release()
        return None

def detect_face(frame):
    mtcnn = MTCNN()
    boxes, _ = mtcnn.detect(frame)
    if boxes is not None:
        # Assuming only one face in the frame
        box = boxes[0]
        x1, y1, x2, y2 = box
        # Crop the frame to the detected face
        cropped_frame = frame[int(y1):int(y2), int(x1):int(x2)]
        return cropped_frame
    else:
        return None

# Function to download the pretrained face alignment model if it doesn't exist
def download_face_alignment_model(url, save_path):
    if not os.path.exists(save_path):
        print("Downloading pretrained face alignment model...")
        response = requests.get(url)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print("Download complete.")

# Specify the URL of the pretrained face alignment model
face_alignment_model_url = "https://github.com/1adrianb/face-alignment-models/releases/download/2.0.1/2DFAN4-11f355bf06.pth.tar"

# Download the pretrained face alignment model if it doesn't exist
face_alignment_model_path = os.path.abspath("2DFAN4-11f355bf06.pth.tar")
download_face_alignment_model(face_alignment_model_url, face_alignment_model_path)

# Initialize face alignment model
fa = face_alignment.FaceAlignment(2, flip_input=False)  # 2 corresponds to 2D landmarks

def align_face(frame):
    # Perform face alignment
    aligned_faces = fa.get_landmarks(frame)
    if aligned_faces is not None:
        aligned_face = aligned_faces[0]  # Assuming only one face in the frame
        return aligned_face
    else:
        return None

def preprocess_image(frame):
    # Convert the frame to a PIL Image
    frame_pil = Image.fromarray(frame.astype('uint8'))

    # Convert the image to grayscale
    frame_pil = frame_pil.convert('L')

    # Resize and normalize the frame
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485], std=[0.229]),  # For grayscale images, only 1 channel
    ])
    img_tensor = transform(frame_pil)
    return img_tensor

def preprocess_spectrogram(image_path):
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # Resize to match ResNet input size
        transforms.ToTensor(),           # Convert to tensor
    ])
    img_tensor = transform(img)
    # img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension
    return img_tensor

def load_spectrogram_dataset(input_folder):
    X = []
    y = []
    # List all files in the input folder
    files = os.listdir(input_folder)
    # Iterate over files in the folder
    for filename in files:
        if filename.endswith(".png"):  # Assuming mel spectrograms are stored as PNG files
            input_path = os.path.join(input_folder, filename)
            img_tensor = preprocess_spectrogram(input_path)
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

def load_dataset(input_folder):
    X = []
    y = []
    video_files = [file for file in os.listdir(input_folder) if file.endswith(".flv")]
    for video_file in tqdm(video_files):
        video_path = os.path.join(input_folder, video_file)
        frame = extract_frame(video_path)
        if frame is not None:
            cropped_face = detect_face(frame)
            if cropped_face is not None:
                preprocessed_face = preprocess_image(cropped_face)
                X.append(preprocessed_face)
                label = video_file.split("_")[2].split(".")[0]  # Adjusted to handle different file extensions
                if label == "HAP":
                    y.append(0)
                elif label == "SAD":
                    y.append(1)
                elif label == "ANG":
                    y.append(2)
            else:
                print(f"No face detected in {video_file}. Skipping.")
        else:
            print(f"Failed to extract frame from {video_file}. Skipping.")
    return X, y

class ConcatDataset(torch.utils.data.Dataset):
    def __init__(self, X1, X2, y):
        self.X1 = X1
        self.X2 = X2
        self.y = y

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        img1 = self.X1[idx]
        img2 = self.X2[idx]
        label = self.y[idx]
        # Concatenate images along the channel dimension
        concatenated_img = torch.cat((img1, img2), dim=2)
        return concatenated_img, label

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

if __name__ == "__main__":
    # input_folder = '/content/drive/MyDrive/csci535/videos'
    # input_folder_spec = '/content/drive/MyDrive/csci535/melspec'

    if len(sys.argv) != 3:
        print("Usage: python video_to_features_cnn.py video_folder spectrogram_folder")
        sys.exit(1)

    input_folder = sys.argv[1]
    input_folder_spec = sys.argv[2]

    # Check if input folder exists
    if not os.path.exists(input_folder):
        print("Input folder does not exist.")
        sys.exit(1)
    # Check if input folder exists
    if not os.path.exists(input_folder_spec):
        print("Input folder does not exist.")
        sys.exit(1)

    # Load dataset and split into train and test sets
    X, y = load_dataset(input_folder)
    X_spec, y_spec = load_spectrogram_dataset(input_folder_spec)

    print(f"Total number of samples: {len(X)}")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    print(f"Number of train samples (video): {len(X_train)}", f"Number of test samples: {len(X_test)}")
    X_train_spec, X_test_spec, y_train_spec, y_test_spec = train_test_split(X_spec, y_spec, test_size=0.3, random_state=42)
    print(f"Number of train samples (audio): {len(X_train_spec)}", f"Number of test samples: {len(X_test_spec)}")

    # Initialize the model
    model = CNN(num_classes=3)  # 3 classes for HAPPY, SAD, ANGRY
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Define loss function and optimizer
    _lr = 0.001
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=_lr)

    # Concatenate datasets
    # train_dataset = ConcatDataset(X_train, X_train_spec, y_train)
    test_dataset = ConcatDataset(X_test, X_test_spec, y_test)

    # Create data loaders
    _bs = 32

    # Create data loaders
    # train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=_bs, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=_bs)


    print(f"Batch size: {_bs}", f"lr: {_lr}")

    # # Training loop
    # num_epochs = 50
    # for epoch in range(num_epochs):
    #     print("Epoch " + str(epoch))
    #     train_loss, train_accuracy = train_model(model, criterion, optimizer, train_loader, device)
    #     test_loss, test_accuracy = test_model(model, criterion, test_loader, device)
    #     print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Train Accuracy: {train_accuracy:.4f}, Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.4f}")

    model = CNN(num_classes=3)  # 3 classes for HAPPY, SAD, ANGRY
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    test_loss, test_accuracy = test_model(model, criterion, test_loader, device)
    print(f"Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.4f}")

    # torch.save(model.state_dict(), 'ResNet18_audio_video_'+str(num_epochs)+'_'+str(_bs)+'_'+str(_lr))

    # !ls -lh /content/

    # !cp  'ResNet18_audio_video_50_32_0.001' '/content/drive/MyDrive/csci535/models'

