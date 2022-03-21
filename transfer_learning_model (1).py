# -*- coding: utf-8 -*-
"""Transfer_Learning_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Gm3f4oLpwWi4dQBIPaUYlG7WjkIQj_hQ

**Transfer Learning model using VGG**
"""

import numpy as np
import time
import torch
import torch.nn as nn

import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torch.utils.data.sampler import SubsetRandomSampler
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import math
import torchvision.models as models

torch.manual_seed(1)

!unzip 'DatasetAugmented'

vgg16 = models.vgg.vgg16(pretrained=True)

data_path = 'DatasetAugmented'

def get_data(len_train_data, len_val_data, len_test_data):

    transform = transforms.Compose([transforms.Resize((224,224)), 
                                    transforms.ToTensor()])

    #Seperate for training, validation, and test data 
    dataset = torchvision.datasets.ImageFolder(data_path, transform=transform)
    num_train = math.floor(len(dataset)*len_train_data)
    num_val = math.floor(len(dataset)*len_val_data)
    num_test = math.floor(len(dataset)*len_test_data)
    print("Number of images for training: ", num_train)
    print("Number of images for validation: ", num_val)
    print("Number of images for validation: ", num_test)
    dummy_len = len(dataset) - (num_test + num_train + num_val)

    # Split into train and validation
    train_set, val_set, test_set, dummy = torch.utils.data.random_split(dataset, [num_train, num_val, num_test, dummy_len]) #80%, 10%, 10% split

    # return train_loader, val_loader, test_loader
    return train_set, val_set, test_set

print("Loading data sets...")
train_data, val_data, test_data = get_data(0.8, 0.2, 0)

classes = ['BlackAugmented', 'AsianAugmented', 'IndianAugmented', 'LatinoAugmented', 'MiddleEasternAugmented', 'WhiteAugmented']

class ANNClassifier(nn.Module):
    def __init__(self):
        super(ANNClassifier, self).__init__()
        self.name = "ANN"
        self.dropout = nn.Dropout(0.5)
        self.layer1 = nn.Linear(7 * 512 * 7, 5000) 
        self.layer2 = nn.Linear(5000, 84)
        self.layer3 = nn.Linear(84, 28)
        self.layer4 = nn.Linear(28, 6) #6 outputs


    def forward(self, img):
        flattened = img.view(-1, 7 * 512 * 7)

        activation1 = self.layer1(flattened)
        activation1 = self.dropout(activation1)

        activation1 = F.relu(activation1)
        activation1 = self.dropout(activation1)

        activation2 = self.layer2(activation1)
        activation2 = F.relu(activation2)

        activation3 = self.layer3(activation2)
        activation3 = self.dropout(activation3)

        activation3 = F.relu(activation3)
        activation3 = self.dropout(activation3)

        output = self.layer4(activation3)
        output = output.squeeze(1)
        return output

def get_accuracy(model, data, batch_size):
    correct = 0
    total = 0
    for imgs, labels in torch.utils.data.DataLoader(data, batch_size=batch_size, shuffle=True):

        #############################################
        # To Enable GPU Usage
        if torch.cuda.is_available():
          imgs = imgs.cuda()
          labels = labels.cuda()
        #############################################

        output = model(VGGC(imgs))
        
        #select index with maximum prediction score
        pred = output.max(1, keepdim=True)[1]
        correct += pred.eq(labels.view_as(pred)).sum().item()
        total += imgs.shape[0]
    return correct / total

def train(model, train_data, val_data, learning_rate=0.001, batch_size=64, num_epochs=1):
    torch.manual_seed(1000)  # set the random seed
    train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    #optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)

    iters, losses, train_acc, val_acc = [], [], [], []

    # Training
    start_time = time.time()
    n = 0 # the number of iterations
    for epoch in range(num_epochs):
        for imgs, labels in iter(train_loader):
            
            #############################################
            # To Enable GPU Usage
            if torch.cuda.is_available():
              imgs = imgs.cuda()
              labels = labels.cuda()
            #############################################
            
              
            out = model(VGGC(imgs))             # forward pass
            loss = criterion(out, labels) # compute the total loss
            loss.backward()               # backward pass (compute parameter updates)
            optimizer.step()              # make the updates for each parameter
            optimizer.zero_grad()         # a clean up step for PyTorch

            # Save the current training information
            iters.append(n)
            losses.append(float(loss)/batch_size)             # compute *average* loss
            n += 1


        train_acc.append(get_accuracy(model, train_data, batch_size)) # compute training accuracy 
        val_acc.append(get_accuracy(model, val_data, batch_size))  # compute validation accuracy
        print(("Epoch {}: Train acc: {} |"+"Validation acc: {}").format(
                epoch + 1,
                train_acc[-1],
                val_acc[-1]))
        

    print('Finished Training')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Total time elapsed: {:.2f} seconds".format(elapsed_time))

    # Plotting
    plt.title("Training Curve")
    plt.plot(iters, losses, label="Train")
    plt.xlabel("Iterations")
    plt.ylabel("Loss")
    plt.show()

    plt.title("Training Curve")
    plt.plot(range(1 ,num_epochs+1), train_acc, label="Train")
    plt.plot(range(1 ,num_epochs+1), val_acc, label="Validation")
    plt.xlabel("Epochs")
    plt.ylabel("Training Accuracy")
    plt.legend(loc='best')
    plt.show()

    print("Final Training Accuracy: {}".format(train_acc[-1]))
    print("Final Validation Accuracy: {}".format(val_acc[-1]))

model = ANNClassifier()
VGGC = vgg16.features

if torch.cuda.is_available():
    VGGC.cuda()
    model_1.cuda() 
    print('CUDA is available!  Training on GPU ...')
else:
    print('CUDA is not available.  Training on CPU ...')


torch.cuda.memory_summary(device=None, abbreviated=False)
train(model_1, train_data, val_data, 0.001, 32, 5)

train(model_1, train_data, val_data, 0.001, 32, 5)

train(model_1, train_data, val_data, 0.001, 32, 5)