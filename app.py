import os
import time
import random  
import datetime  
from transformers import pipeline
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
    from tqdm import tqdm
except ImportError:
    os.system('pip install tqdm')
    from tqdm import tqdm

try:
    from agent_routing import agent_executable
except ImportError:
    agent_executable = None

# Cnx à MONGODB
MONGO_URI = "mongodb://localhost:27017/"

try:
    print(" Connexion à MongoDB...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print(" Connecté à MongoDB avec succès !")
    db = client["darija_social_media"]
    collection = db["tweets_sentiment"]
except ConnectionFailure:
    print(" Impossible de se connecter à MongoDB. Vérifie que le serveur est lancé.")
    exit(1)

#  CHARGEMENT DIRECT DE DARIJABERT
model_path = r"C:\Users\pop\Downloads\deeplearning\darijabert_sentiment\best_darijabert_model"
print(f"⏳ Chargement direct du modèle DarijaBERT depuis : {model_path}")

if not os.path.exists(model_path):
    print(f"❌ Erreur : Le dossier du modèle n'existe pas dans {model_path}")
    exit(1)

classifier = pipeline("text-classification", model=model_path, tokenizer=model_path)
print("Modèle DarijaBERT chargé directement avec succès ! Plus besoin d'API HTTP.")

#mapping
labels_mapping = {
    "LABEL_0": "Positive",
    "LABEL_1": "Neutral",
    "LABEL_2": "Negative"
}

# TRAITEMENT Du DATASET (61,355 TWEETS)
print("\n Lancement du traitement du Dataset...")

try:
    query = {
        "agent_decision.action_to_take": "Aucune"
    }
    
    total_tweets = collection.count_documents(query)
    print(f"📊 Nombre de tweets réels en attente : {total_tweets}")
    
    tweets_cursor = collection.find(query)
    
    for doc in tqdm(tweets_cursor, total=total_tweets, desc="Analyse et Décision Agent"):
        
        texte_brut = doc.get("text_raw", doc.get("text", ""))
        if not texte_brut or str(texte_brut).strip() == "":
            continue
            
        nom_utilisateur = doc.get("user", f"User_{random.randint(1000, 9999)}")
        
        """try:
            prediction = classifier(str(texte_brut))[0]
            sentiment_predit = labels_mapping.get(prediction['label'], "Neutral")
            score_confiance = round(prediction['score'], 4)
        except Exception:
            sentiment_predit = "Neutral"
            score_confiance = 1.0"""
        try:
            prediction = classifier(str(texte_brut))[0]
            sentiment_predit = labels_mapping.get(prediction['label'], "Neutral")
            score_confiance = round(prediction['score'], 4)
        except Exception as e:
            print(f"🚨 Error dans le modèle: {e}")  # هادي غادي توريك المشكل بالظبط فين كاين
            sentiment_predit = "Neutral"
            score_confiance = 1.0
        
        etat_initial = {
            "tweet_id": str(doc["_id"]),
            "user": nom_utilisateur,
            "text_raw": texte_brut,
            "sentiment": sentiment_predit,
            "confidence_score": score_confiance,
            "action_requise": "Aucune",
            "reponse_automatique": "N/A"
        }
        
        if agent_executable:
            try:
                etat_final_agent = agent_executable.invoke(etat_initial)
                action_agent = etat_final_agent.get("action_requise", "Aucune")
                reponse_agent = etat_final_agent.get("reponse_automatique", "N/A")
            except Exception:
                action_agent = "Ouvrir Ticket Support" if sentiment_predit == "Negative" else "Envoyer Remerciement" if sentiment_predit == "Positive" else "Aucune"
                reponse_agent = "🚨 ALERTE AUTOMATIQUE" if sentiment_predit == "Negative" else "N/A"
        else:
            action_agent = "Ouvrir Ticket Support" if sentiment_predit == "Negative" else "Envoyer Remerciement" if sentiment_predit == "Positive" else "Aucune"
            reponse_agent = "🚨 ALERTE AUTOMATIQUE" if sentiment_predit == "Negative" else "N/A"
        
        #sauvegarde ds mongoDB
        date_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        collection.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "timestamp": date_now,
                    "user": nom_utilisateur,
                    "analysis.model_used": "DarijaBERT Direct",
                    "analysis.sentiment": sentiment_predit,
                    "analysis.confidence_score": score_confiance,
                    "agent_decision.framework": "LangGraph / LangChain",
                    "agent_decision.action_to_take": action_agent,
                    "agent_decision.generated_output": reponse_agent
                }
            }
        )


except KeyboardInterrupt:
    print("\n Pipeline interrompu proprement par l'utilisateur.")
finally:
    client.close()
    print(" Connexion MongoDB fermée.")