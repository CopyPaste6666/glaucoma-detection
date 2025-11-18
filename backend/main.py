'''from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
from torchvision import transforms
from PIL import Image
import os
import io
from backend.utils.inference import load_model, predict_image

app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your trained model
model_path = os.path.join(os.path.dirname(__file__), "../model/glaucoma_model.pth")
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")

model = load_model(model_path, device="cpu")

# Image transformation
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

@app.post("/predict")
async def predict(left_eye: UploadFile = File(...), right_eye: UploadFile = File(...)):
    try:
        # Read both images
        left_img = Image.open(io.BytesIO(await left_eye.read())).convert("RGB")
        right_img = Image.open(io.BytesIO(await right_eye.read())).convert("RGB")

        # Predict glaucoma
        left_pred, left_conf = predict_image(left_img, model, transform)
        right_pred, right_conf = predict_image(right_img, model, transform)

        result = {
            "left_eye": {"isGlaucoma": bool(left_pred), "confidence": float(left_conf)},
            "right_eye": {"isGlaucoma": bool(right_pred), "confidence": float(right_conf)},
        }

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)'''
# main.py
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

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ MongoDB Connection
MONGO_URI = "mongodb+srv://nireshsingha009:vPGNAaC7UTJ0d4C8@cluster0.ezivx0z.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["mydatabase"]
users = db["users"]

# ------------------ AUTH ROUTES ------------------

@app.post("/signup")
async def signup(request: Request):
    data = await request.json()
    license_id = data.get("license_id")
    email = data.get("email")
    password = data.get("password")

    if not license_id or not email or not password:
        return {"error": "All fields are required"}

    if users.find_one({"email": email}):
        return {"error": "User already exists"}

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
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

    if not email or not password:
        return {"error": "Email and password are required"}

    user = users.find_one({"email": email})
    if not user:
        return {"error": "User not found"}

    if not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return {"error": "Invalid password"}

    return {"message": "Login successful", "user": {"email": user["email"], "license_id": user["license_id"]}}


# ------------------ PREDICTION ROUTE ------------------
'''
# Load your trained model
model_path = os.path.join(os.path.dirname(__file__), "../model/glaucoma_model.pth")
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")

model = load_model(model_path, device="cpu")

# Image transformation
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

@app.post("/predict")
async def predict(left_eye: UploadFile = File(...), right_eye: UploadFile = File(...)):
    try:
        # Read both images
        left_img = Image.open(io.BytesIO(await left_eye.read())).convert("RGB")
        right_img = Image.open(io.BytesIO(await right_eye.read())).convert("RGB")

        # Predict glaucoma
        left_pred, left_conf = predict_image(left_img, model, transform)
        right_pred, right_conf = predict_image(right_img, model, transform)

        result = {
            "left_eye": {"isGlaucoma": bool(left_pred), "confidence": float(left_conf)},
            "right_eye": {"isGlaucoma": bool(right_pred), "confidence": float(right_conf)},
        }

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)'''

# Load model and transformation
MODEL_PATH =  os.path.join(os.path.dirname(__file__), "../model/glaucoma_model.pth") # update path if needed
device = "cuda" if torch.cuda.is_available() else "cpu"
model = load_model(MODEL_PATH, device=device)


# Preprocessing transform (same used during training)
transform = transforms.Compose([
transforms.Resize((224, 224)),
transforms.ToTensor(),
transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


@app.post("/predict")
async def predict(left_eye: UploadFile = File(...), right_eye: UploadFile = File(...)):
    try:
        # Read both images
        left_img = Image.open(io.BytesIO(await left_eye.read())).convert("RGB")
        right_img = Image.open(io.BytesIO(await right_eye.read())).convert("RGB")


        # Predict glaucoma
        left_pred, left_conf = predict_image(left_img, model, transform, device=device)
        right_pred, right_conf = predict_image(right_img, model, transform, device=device)


        result = {
        "left_eye": {"isGlaucoma": bool(left_pred), "confidence": float(left_conf)},
        "right_eye": {"isGlaucoma": bool(right_pred), "confidence": float(right_conf)},
    }


        return JSONResponse(content=result)


    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

