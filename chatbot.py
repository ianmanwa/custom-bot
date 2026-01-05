from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import numpy as np
from sentence_transformers import SentenceTransformer



from fastapi.middleware.cors import CORSMiddleware




# =====================
# CONFIG
# =====================

app = FastAPI()

mongo = MongoClient("mongodb://localhost:27017/")
db = mongo["chatbot_db"]
products_col = db["products"]

# Load local embedding model (ONCE)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")



#--------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now (OK for learning)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# =====================
# MODELS
# =====================

class ProductRequest(BaseModel):
    name: str
    description: str
    price: float
    stock: int

class ChatRequest(BaseModel):
    message: str

# =====================
# UTILS
# =====================

def get_embedding(text):
    return embedding_model.encode(text).tolist()

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# =====================
# ADD PRODUCT
# =====================

@app.post("/add-product")
def add_product(product: ProductRequest):
    text = product.name + " " + product.description
    embedding = get_embedding(text)

    products_col.insert_one({
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "embedding": embedding
    })

    return {"status": "product added"}

# =====================
# CHAT
# =====================

@app.post("/chat")
def chat(data: ChatRequest):
    message = data.message

    convo =  {"messages": []}

    user_embedding = get_embedding(message)

    best_product = None
    best_score = -1

    for product in products_col.find():
        score = cosine_similarity(user_embedding, product["embedding"])
        if score > best_score:
            best_score = score
            best_product = product

    

    if best_score <= 0.4:
        reply = "Sorry, I don't understand. Please clarify"   
    elif best_product:
        reply = f"Yes, we have {best_product['name']} for Ksh.{best_product['price']}."
    else:
        reply = "Sorry, I couldn't find that product."
        

    convo["messages"].append({
        "user": message,
        "bot": reply
    })

   

    return {"reply": reply}
