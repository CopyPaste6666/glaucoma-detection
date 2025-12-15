# backend/utils/lime_explainer.py
import numpy as np
import torch
from lime import lime_image
from PIL import Image
from skimage.segmentation import slic

def generate_lime(model, image, transform, device):
    model.eval()
    explainer = lime_image.LimeImageExplainer()

    def predict_fn(images):
        batch = []
        for img in images:
            pil_img = Image.fromarray(img.astype("uint8"))
            batch.append(transform(pil_img))
        batch = torch.stack(batch).to(device)

        with torch.no_grad():
            outputs = model(batch)
            probs = torch.softmax(outputs, dim=1)

        return probs.cpu().numpy()

    explanation = explainer.explain_instance(
        np.array(image),
        predict_fn,
        top_labels=1,
        hide_color=0,
        num_samples=650,
        segmentation_fn=lambda x: slic(x, n_segments=50, compactness=10)
    )

    label = explanation.top_labels[0]
    segments = explanation.segments  # (H, W)

    lime_map = np.zeros(segments.shape, dtype=np.float32)

    for region, weight in explanation.local_exp[label]:
        lime_map[segments == region] += max(weight, 0)

    # normalize to 0–1
    lime_map -= lime_map.min()
    lime_map /= (lime_map.max() + 1e-8)

    # 🔴 IMPORTANT: resize to 384×384
    lime_map = np.array(
        Image.fromarray(lime_map).resize((384, 384))
    )

    return lime_map.tolist()
