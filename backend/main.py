import numpy as np
from backend.utils.regions import generate_region_masks
from backend.utils.xai_fusion import build_xai_table
from backend.utils.explanation import generate_explanation
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import bcrypt
import torch
from torchvision import transforms
from PIL import Image
import os, io

from backend.utils.inference import load_model, predict_image
from backend.utils.gradcam import generate_gradcam
from backend.utils.lime_explainer import generate_lime



# ------------------ APP ------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ DATABASE ------------------
MONGO_URI = "mongodb+srv://nireshsingha009:vPGNAaC7UTJ0d4C8@cluster0.ezivx0z.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["mydatabase"]
users = db["users"]

# ------------------ AUTH ------------------
@app.post("/signup")
async def signup(request: Request):
    data = await request.json()
    license_id = data.get("license_id")
    email = data.get("email")
    password = data.get("password")

    if not all([license_id, email, password]):
        return {"error": "All fields are required"}

    if users.find_one({"email": email}):
        return {"error": "User already exists"}

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users.insert_one({
        "license_id": license_id,
        "email": email,
        "password": hashed_pw
    })

    return {"message": "Account created successfully"}


@app.post("/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    user = users.find_one({"email": email})
    if not user:
        return {"error": "User not found"}

    if not bcrypt.checkpw(password.encode(), user["password"]):
        return {"error": "Invalid password"}

    return {
        "message": "Login successful",
        "user": {
            "email": user["email"],
            "license_id": user["license_id"]
        }
    }

# ------------------ MODEL ------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../model/glaucoma_model.pth")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = load_model(MODEL_PATH, device=device)

transform = transforms.Compose([
    transforms.Resize((384, 384)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ------------------ PREDICTION + XAI ------------------
@app.post("/predict")
async def predict(
    left_eye: UploadFile = File(...),
    right_eye: UploadFile = File(...)
):
    result = None  # 🔒 prevent "unbound local variable" error

    try:
        # ---------- Load images ----------
        left_img = Image.open(io.BytesIO(await left_eye.read())).convert("RGB")
        right_img = Image.open(io.BytesIO(await right_eye.read())).convert("RGB")

        # ---------- Prediction ----------
        left_pred, left_conf, _ = predict_image(
            left_img, model, transform, device, return_probs=True
        )
        right_pred, right_conf, _ = predict_image(
            right_img, model, transform, device, return_probs=True
        )

        # ---------- Grad-CAM ----------
        left_gradcam = None
        right_gradcam = None

        if left_pred:
            try:
                left_gradcam = generate_gradcam(model, left_img, transform, device)
            except Exception as e:
                print("GradCAM left failed:", e)

        if right_pred:
            try:
                right_gradcam = generate_gradcam(model, right_img, transform, device)
            except Exception as e:
                print("GradCAM right failed:", e)

        # ---------- LIME ----------
        left_lime = None
        right_lime = None

        if left_pred:
            try:
                left_lime = generate_lime(model, left_img, transform, device)
            except Exception as e:
                print("LIME left failed:", e)

        if right_pred:
            try:
                right_lime = generate_lime(model, right_img, transform, device)
            except Exception as e:
                print("LIME right failed:", e)

        # ---------- XAI TABLE + EXPLANATION ----------
        region_masks = generate_region_masks()

        left_xai_table = None
        left_explanation = None

        if left_pred and left_gradcam is not None and left_lime is not None:
            grad = np.array(left_gradcam)
            lime_map = np.array(left_lime)

            left_xai_table = build_xai_table(
                grad, lime_map, region_masks
            )

            left_explanation = generate_explanation(
                left_xai_table, left_conf
            )

        right_xai_table = None
        right_explanation = None

        if right_pred and right_gradcam is not None and right_lime is not None:
            grad = np.array(right_gradcam)
            lime_map = np.array(right_lime)

            right_xai_table = build_xai_table(
                grad, lime_map, region_masks
            )

            right_explanation = generate_explanation(
                right_xai_table, right_conf
            )

        # ---------- FINAL RESPONSE ----------
        result = {
            "left_eye": {
                "isGlaucoma": bool(left_pred),
                "confidence": round(float(left_conf), 2),
                "gradcam": left_gradcam,
                "lime_heatmap": left_lime,
                "xai_table": left_xai_table,
                "explanation": left_explanation
            },
            "right_eye": {
                "isGlaucoma": bool(right_pred),
                "confidence": round(float(right_conf), 2),
                "gradcam": right_gradcam,
                "lime_heatmap": right_lime,
                "xai_table": right_xai_table,
                "explanation": right_explanation
            },
            "comparison": {
                "diagnosis": {
                    "left_eye": "Glaucoma" if left_pred else "Normal",
                    "right_eye": "Glaucoma" if right_pred else "Normal"
                },
                "confidence": {
                    "left_eye": round(left_conf * 100, 2),
                    "right_eye": round(right_conf * 100, 2)
                },
                "risk_level": {
                    "left_eye": "High" if left_pred and left_conf > 0.85 else "Low",
                    "right_eye": "High" if right_pred and right_conf > 0.85 else "Low"
                }
            }
        }

        return JSONResponse(content=result)

    except Exception as e:
        print("Prediction failed:", e)
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
