from tqdm import tqdm
import torch.optim as optim
from torchvision import datasets, transforms
import torch
import torch.nn.functional as F
import torchvision
from torchsummary import summary
import numpy as np
from torch.optim.lr_scheduler import StepLR,OneCycleLR
from torch.optim import Adam
from torch.optim import SGD

train_losses = []
test_losses = []
train_acc = []
test_acc = []

def train(model, device, train_loader, optimizer, epoch, train_losses, train_acc, lambda_l1=0,sched_fl=" ",scheduler=None):

    model.train()
    pbar = tqdm(train_loader)
    correct = 0
    processed = 0
    train_loss = 0

    for batch_idx, (data, target) in enumerate(pbar):
        # get samples
        data, target = data.to(device), target.to(device)

        # Init
        optimizer.zero_grad()
        # In PyTorch, we need to set the gradients to zero before starting to do backpropragation because PyTorch accumulates the gradients on subsequent backward passes. 
        # Because of this, when you start your training loop, ideally you should zero out the gradients so that you do the parameter update correctly.

        # Predict
        y_pred = model(data)

        # Calculate loss
        loss = F.cross_entropy(y_pred, target)

        if(lambda_l1 > 0):
            l1 = 0
            for p in model.parameters():
                l1 = l1 + p.abs().sum()
            loss = loss + lambda_l1*l1

        train_loss += loss.item()

        # Backpropagation
        loss.backward()
        optimizer.step()

        # Update pbar-tqdm
        if sched_fl == 'X':
            scheduler.step()
            
        pred = y_pred.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
        correct += pred.eq(target.view_as(pred)).sum().item()   
    
    train_losses.append(train_loss/len(train_loader.dataset))
    train_acc.append(100*correct/len(train_loader.dataset))

    print(f'\nAverage Training Loss={train_loss/len(train_loader.dataset)}, Accuracy={100*correct/len(train_loader.dataset)}')

def test(model, device, test_loader,test_losses, test_acc,epoch,target_acc=95,save_file=''):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.cross_entropy(output, target).item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    test_losses.append(test_loss)

    print('Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.2f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))
    accuracy_epoch = 100. * correct / len(test_loader.dataset)

    if(accuracy_epoch > target_acc) and save_file == 'X':
        model_name_file = "Model_" + str(epoch) + "_acc_" + str(round(accuracy_epoch,2)) + ".pth"
        path = "/content/drive/MyDrive/" + model_name_file
        torch.save(model.state_dict(), path)
        print(f'Saved Model weights in file:  {model_name_file}')

    test_acc.append(100. * correct / len(test_loader.dataset))
    return accuracy_epoch

def train_test_model(model, trainloader, testloader, norm_type='BN', EPOCHS=20, lr=0.001, device='cuda',sched='StepLR',lambda_l1=0,target_acc=90,optim='SGD'):
    wrong_prediction_list = []
    train_losses = []
    train_acc = []
    test_losses = []
    test_acc = []

    #torch.manual_seed(42)
    if optim == 'SGD':
        optimizer = SGD(model.parameters(), lr=lr, momentum=0.9)
    elif optim == 'ADAM':
        optimizer = Adam(model.parameters(), lr=lr, betas=(0.9, 0.999))
    else:
        optimizer = SGD(model.parameters(), lr=lr, momentum=0.9)      #fallback if nothing given

    if sched == 'StepLR':
        scheduler = StepLR(optimizer, step_size=100, gamma=0.25)    
        sched_fl = 'X'
    elif sched == 'OneCycle':
        scheduler = OneCycleLR(optimizer=optimizer, max_lr=lr, epochs=EPOCHS, steps_per_epoch=len(trainloader), pct_start=5/EPOCHS, div_factor=10,three_phase=False) 
        sched_fl = 'X'
    else:
        sched_fl = ' '

    lambda_l1 = lambda_l1
    
    for epoch in range(EPOCHS):
        print("EPOCH:", epoch+1)
        train(model, device, trainloader, optimizer, epoch, train_losses, train_acc, lambda_l1,sched_fl,scheduler)        

        eval_test_acc = test(model, device, testloader, test_losses, test_acc, epoch)
        if(eval_test_acc >= target_acc):
            break
    
    model.eval()
    for images, labels in testloader:
        images, labels = images.to(device), labels.to(device)
        output = model(images)
        pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
        match = pred.eq(labels.view_as(pred)).to('cpu').numpy()
        for j, i in enumerate(match):
            if(i == False):
                wrong_prediction_list.append((images[j], pred[j].item(), labels[j].item()))

    print(f'Total Number of incorrectly predicted images by model type {norm_type} is {len(wrong_prediction_list)}')
    return model, wrong_prediction_list, train_losses, train_acc, test_losses, test_acc
