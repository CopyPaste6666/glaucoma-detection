'''from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import bcrypt

app = FastAPI()

# ✅ Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ MongoDB Connection
MONGO_URI = "mongodb+srv://thangjamnireshwork:2ez4Niresh@cluster0.gp5kqwo.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["mydatabase"]
users = db["users"]

@app.post("/signup")
async def signup(request: Request):
    data = await request.json()
    license_id = data.get("license_id")
    email = data.get("email")
    password = data.get("password")

    if not license_id or not email or not password:
        return {"error": "All fields are required"}

    # Check if user already exists
    if users.find_one({"email": email}):
        return {"error": "User already exists"}

    # Hash password before storing
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

    # Check password
    if not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return {"error": "Invalid password"}

    return {"message": "Login successful", "user": {"email": user["email"], "license_id": user["license_id"]}}'''
