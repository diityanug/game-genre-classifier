from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import GameRequest     
from backend import predict                     

app = FastAPI(
    title="Multi-Label Game Genre Classifier",
    description="API for predicting game genres using NLP",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict_genre(request: GameRequest):
    result = predict.get_prediction(request.title, request.description)
    
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])
        
    return {
        "status": result["status"],
        "data": result["data"]
    }