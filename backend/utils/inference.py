'''import torch
from torch.nn import functional as F
from torchvision import models


def load_model(model_path, device="cpu"):
    # 1️⃣ Create the same architecture used in training (EfficientNetV2-S)
    model = models.efficientnet_v2_s(weights=None)
    
    # 2️⃣ Replace final layer for your number of output classes (2 = Glaucoma / Normal)
    num_features = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(num_features, 2)

    # 3️⃣ Load the saved state dict
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)

    # 4️⃣ Send to device and evaluation mode
    model.to(device)
    model.eval()
    return model


def predict_image(image, model, transform, device="cpu"):
    # Apply preprocessing and move to device
    x = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(x)
        probs = F.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probs, 1)
    return predicted.item(), confidence.item()'''
import torch
from torch.nn import functional as F
from torchvision import models


def load_model(model_path, device="cpu"):
    # 1️⃣ Create the same architecture used in training (EfficientNetV2-S)
    model = models.efficientnet_v2_s(weights=None)

    # 2️⃣ Replace final layer for 2 classes (Normal / Glaucoma)
    num_features = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(num_features, 2)

    # 3️⃣ Load trained weights
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)

    # 4️⃣ Send to device and evaluation mode
    model.to(device)
    model.eval()
    return model


def predict_image(image, model, transform, device="cpu", return_probs=False):
    """
    Returns:
      - predicted class (0 or 1)
      - confidence score
      - (optional) class probabilities
    """
    x = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(x)
        probs = F.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probs, 1)

    if return_probs:
        return (
            predicted.item(),
            confidence.item(),
            {
                "normal": float(probs[0][0]),
                "glaucoma": float(probs[0][1]),
            }
        )

    return predicted.item(), confidence.item()

