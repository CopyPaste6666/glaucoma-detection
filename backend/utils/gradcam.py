import torch
import cv2
import numpy as np

def generate_heatmap(model, image_tensor, target_class=None):
    model.eval()
    
    # ✅ EfficientNetV2 uses `features` instead of `layer4`
    target_layer = model.features[-1]

    gradients = []
    activations = []

    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])

    def forward_hook(module, input, output):
        activations.append(output)

    # Register hooks
    target_layer.register_forward_hook(forward_hook)
    target_layer.register_backward_hook(backward_hook)

    # Forward pass
    output = model(image_tensor)
    if target_class is None:
        target_class = output.argmax(dim=1).item()

    # Backward pass for target class
    model.zero_grad()
    class_score = output[0, target_class]
    class_score.backward()

    # Get stored gradients and activations
    grads = gradients[0].cpu().data.numpy()[0]
    acts = activations[0].cpu().data.numpy()[0]

    weights = np.mean(grads, axis=(1, 2))
    cam = np.zeros(acts.shape[1:], dtype=np.float32)

    for i, w in enumerate(weights):
        cam += w * acts[i]

    cam = np.maximum(cam, 0)
    cam = cv2.resize(cam, (224, 224))
    cam = cam - np.min(cam)
    cam = cam / np.max(cam)
    return cam
