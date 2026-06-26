from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from transformers import pipeline

app = FastAPI(
    title="API d'Analyse de Sentiment DarijaBERT", 
    description="PROJET MASTER : Détection de sentiment (POS, NEG, NEU) pour le dialecte marocain.",
    version="1.0"
)

# Chargement sécurisé du modèle local (Vérifié pour Windows)
#model_path = os.path.abspath("darijabert_sentiment")
model_path = r"C:\Users\pop\Downloads\deeplearning\darijabert_sentiment\best_darijabert_model"
classifier = pipeline("text-classification", model=model_path, tokenizer=model_path)
labels_mapping = {"LABEL_0": "Positive", "LABEL_1": "Negative", "LABEL_2": "Neutral"}

# Structure de la requête attendue
class TweetRequest(BaseModel):
    tweet: str

@app.get("/")
def home():
    return {"status": "En ligne", "modèle": "DarijaBERT (SI2M-Lab)"}

@app.post("/predict")
def predict_sentiment(data: TweetRequest):
    if not data.tweet.strip():
        raise HTTPException(status_code=400, detail="Le texte du tweet ne peut pas être vide.")
    
    # Inférence avec le modèle fine-tuné
    prediction = classifier(data.tweet)[0]
    sentiment_final = labels_mapping.get(prediction['label'], prediction['label'])
    
    return {
        "tweet_analyse": data.tweet,
        "sentiment": sentiment_final,
        "score_confiance": round(prediction['score'], 4)
    }