import torch
import numpy as np
import cv2

def generate_gradcam(model, image, transform, device):
    model.eval()

    # ✅ Correct last convolutional layer for EfficientNetV2
    target_layer = model.features[-2]

    activations = []
    gradients = []

    def forward_hook(module, input, output):
        activations.append(output)

    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])

    # ✅ Use safe hooks
    fh = target_layer.register_forward_hook(forward_hook)
    bh = target_layer.register_full_backward_hook(backward_hook)

    # Forward pass
    x = transform(image).unsqueeze(0).to(device)
    output = model(x)
    class_idx = output.argmax(dim=1).item()

    # Backward pass
    model.zero_grad()
    output[0, class_idx].backward()

    # Get data
    acts = activations[0]        # [1, C, H, W]
    grads = gradients[0]         # [1, C, H, W]

    # Global Average Pooling on gradients
    weights = grads.mean(dim=(2, 3), keepdim=True)

    # Weighted sum
    cam = (weights * acts).sum(dim=1, keepdim=False)

    # ReLU
    cam = torch.relu(cam)

    # Normalize
    cam = cam.squeeze().detach().cpu().numpy()
    cam -= cam.min()
    cam /= (cam.max() + 1e-8)

    # Resize to input size
    cam = cv2.resize(cam, (384, 384))

    # Cleanup hooks
    fh.remove()
    bh.remove()

    return cam.tolist()
