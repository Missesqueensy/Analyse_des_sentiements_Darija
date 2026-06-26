"""import httpx
from typing import Dict, TypedDict

from pymongo import MongoClient

from langgraph.graph import StateGraph, END

from agent_routing import generate_contextual_response_node



# ==========================================================
# 1. STATE DEFINITION
# ==========================================================

class AgentState(TypedDict):

    doc_id: str

    tweet: str

    sentiment: str

    score: float

    action_requise: str

    reponse_generee: str




# ==========================================================
# 2. SENTIMENT ANALYSIS NODE
# ==========================================================

def node_analyse_sentiment(state: AgentState) -> Dict:


    url_api = "http://127.0.0.1:8000/predict"


    tweet = state["tweet"]



    if not tweet.strip():

        return {

            "sentiment": "Neutral",

            "score": 0.0

        }




    try:

        response = httpx.post(

            url_api,

            json={
                "tweet": tweet
            },

            timeout=20

        )



        if response.status_code == 200:


            data = response.json()



            sentiment = data.get(
                "sentiment",
                "Neutral"
            )


            score = data.get(
                "score_confiance",
                0.0
            )



            print(
                f"🎯 DarijaBERT : {tweet[:40]} -> {sentiment} ({score})"
            )



            return {


                "sentiment": sentiment.strip().title(),

                "score": score

            }




    except Exception as e:


        print(
            "❌ FastAPI Error:",
            e
        )




    return {


        "sentiment": "Neutral",

        "score": 0.0

    }





# ==========================================================
# 3. ROUTER
# ==========================================================

def routeur_sentiment(state: AgentState):


    sentiment = state["sentiment"]



    if sentiment == "Positive":

        return "generate"



    elif sentiment == "Negative":

        return "generate"



    else:

        return "end"





# ==========================================================
# 4. BUILD LANGGRAPH
# ==========================================================


workflow = StateGraph(AgentState)



# nodes

workflow.add_node(

    "analyse_sentiment",

    node_analyse_sentiment

)



workflow.add_node(

    "generate_response",

    generate_contextual_response_node

)




# start

workflow.set_entry_point(
    "analyse_sentiment"
)




# conditional routing

workflow.add_conditional_edges(

    "analyse_sentiment",

    routeur_sentiment,

    {


        "generate": "generate_response",


        "end": END

    }

)




workflow.add_edge(

    "generate_response",

    END

)



app_agent = workflow.compile()





# ==========================================================
# 5. RUN ON MONGODB DATASET
# ==========================================================


def run_pipeline_on_all_dataset():


    client = MongoClient(
        "mongodb://localhost:27017/"
    )



    db = client["darija_social_media"]



    collection = db["tweets_sentiment"]




    query = {


        "$or": [

            {
                "agent_decision.action_to_take": "Aucune"
            },


            {

                "agent_decision.action_to_take":
                {
                    "$exists": False
                }

            }

        ]

    }





    total = collection.count_documents(query)



    print(
        f"📊 Tweets à traiter : {total}"
    )





    cursor = collection.find(query)





    compteur = 0



    for doc in cursor:


        compteur += 1



        tweet_text = doc.get(
            "text_raw",
            doc.get("text","")
        )



        if not tweet_text:

            continue





        state = {


            "doc_id": str(doc["_id"]),


            "tweet": tweet_text,


            "sentiment": "Neutral",


            "score":0.0,


            "action_requise":"Aucune",


            "reponse_generee":""

        }






        result = app_agent.invoke(
            state
        )





        collection.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "analysis.sentiment": result.get("sentiment", "Neutral"),
                    "analysis.confidence_score": result.get("score", 0.0),
                    "agent_decision.action_to_take": result.get("action_requise", "Aucune"),
                    "agent_decision.generated_output": result.get("reponse_generee", "N/A")
                }
            }
        )




        if compteur % 50 == 0:


            print(
                f"🔄 Progress : {compteur}/{total}"
            )





    print(
        "✅ Pipeline terminé"
    )






# ==========================================================
# MAIN
# ==========================================================


if __name__ == "__main__":


    run_pipeline_on_all_dataset()"""

import httpx
import time
from typing import Dict, TypedDict
from pymongo import MongoClient
from langgraph.graph import StateGraph, END
from agent_routing import generate_contextual_response_node

# ==========================================================
# 1. STATE DEFINITION
# ==========================================================
class AgentState(TypedDict):
    doc_id: str
    tweet: str
    sentiment: str
    score: float
    action_requise: str
    reponse_generee: str

# ==========================================================
# 2. SENTIMENT ANALYSIS NODE (DarijaBERT API)
# ==========================================================
def node_analyse_sentiment(state: AgentState) -> Dict:
    url_api = "http://127.0.0.1:8000/predict"
    tweet = state["tweet"]

    if not tweet.strip():
        return {"sentiment": "Neutral", "score": 0.0}

    try:
        response = httpx.post(url_api, json={"tweet": tweet}, timeout=20)
        if response.status_code == 200:
            data = response.json()
            sentiment = data.get("sentiment", "Neutral")
            score = data.get("score_confiance", 0.0)
            
            print(f"🎯 DarijaBERT : {tweet[:40]}... -> {sentiment} ({score:.2f})")
            return {
                "sentiment": sentiment.strip().title(),
                "score": score
            }
    except Exception as e:
        print("❌ FastAPI Error, switching to Neutral:", e)

    return {"sentiment": "Neutral", "score": 0.0}

# ==========================================================
# 3. ROUTER
# ==========================================================
def routeur_sentiment(state: AgentState):
    sentiment = state["sentiment"]
    if sentiment in ["Positive", "Negative"]:
        return "generate"
    else:
        return "end"

# ==========================================================
# 4. BUILD LANGGRAPH
# ==========================================================
workflow = StateGraph(AgentState)

# الـ Nodes
workflow.add_node("analyse_sentiment", node_analyse_sentiment)
workflow.add_node("generate_response", generate_contextual_response_node)

# الـ Entry Point
workflow.set_entry_point("analyse_sentiment")

# الـ Conditional Routing
workflow.add_conditional_edges(
    "analyse_sentiment",
    routeur_sentiment,
    {
        "generate": "generate_response",
        "end": END
    }
)

workflow.add_edge("generate_response", END)
app_agent = workflow.compile()

# ==========================================================
# 5. RUN ON MONGODB DATASET
# ==========================================================
def run_pipeline_on_all_dataset():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["darija_social_media"]
    collection = db["tweets_sentiment"]

    # 🔄 الـ Query المعدل: باش يعيد صياغة الـ 50 تويتة الأولين ويورينا الرد الذكي فـ السياق
    query = {} 
    
    total = collection.count_documents(query)
    print(f"📊 Total Tweets dans la DB : {total}")
    print("⏳ Lancement du test sur les 50 premiers documents...")

    cursor = collection.find(query).limit(50)
    compteur = 0

    for doc in cursor:
        compteur += 1
        tweet_text = doc.get("text_raw", doc.get("text", ""))

        if not tweet_text:
            continue

        # إعداد الـ State للـ Graph
        state = {
            "doc_id": str(doc["_id"]),
            "tweet": tweet_text,
            "sentiment": doc.get("analysis", {}).get("sentiment", "Neutral"), # الحفاظ على الـ Sentiment القديم
            "score": doc.get("analysis", {}).get("confidence_score", 0.0),
            "action_requise": "Aucune",
            "reponse_generee": ""
        }

        # تشغيل الـ Graph الموحد
        result = app_agent.invoke(state)

        # التحديث فـ الـ MongoDB بالـ Schema الصحيحة 100% للـ Dashboard
        collection.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "analysis.sentiment": result["sentiment"],
                    "analysis.confidence_score": result["score"],
                    "agent_decision.action_to_take": result["action_requise"],
                    "agent_decision.generated_output": result["reponse_generee"] # الحقل الحاسم للـ Dashboard
                }
            }
        )

        # عطلة خفيفة باش Groq ما يضربش الـ Rate Limit (TPM) حيت الموديل كبير
        time.sleep(0.5)

        if compteur % 10 == 0:
            print(f"🔄 Progress : {compteur}/50 documents traités.")

    print("✅ Pipeline terminé! جربي شوفي الـ Dashboard دابا.")
    client.close()

if __name__ == "__main__":
    run_pipeline_on_all_dataset()