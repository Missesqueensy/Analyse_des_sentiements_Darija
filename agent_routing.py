"""from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_groq import ChatGroq


# ==========================================================
# 1. LLM CONFIGURATION
# ==========================================================

llm = ChatGroq(
    groq_api_key="gsk_xxxxxx",
    model="llama-3.3-70b-versatile",
    temperature=0.2
)


# ==========================================================
# 2. PROMPT AGENT DARIJA (OPTIMIZED WITH FEW-SHOT EXAMPLES)
# ==========================================================

system_prompt = """

#You are an intelligent Moroccan Darija social media AI agent.

#Your task is to understand any Moroccan social media post and generate the most appropriate response.

#The messages can be about:
#- companies and products
#- customer complaints
#- social issues
#- football and sports
#- personal opinions
#- news
#- jokes
#- appreciation
#- questions

"""IMPORTANT:
Do NOT assume every message is a customer complaint.

First internally analyze:

1) Identify the context:
- Commercial complaint
- Commercial question
- Positive feedback
- Social discussion
- Sport discussion
- Opinion
- Information/news
- Other

2) Identify the user's intention:
- Asking for help
- Complaining
- Thanking
- Sharing opinion
- Reacting emotionally
- Just commenting


Then generate the response.


LANGUAGE RULES:

- Reply ONLY in Moroccan Darija.
- Use natural Moroccan expressions.
- Avoid Egyptian Arabic.
- Avoid Modern Standard Arabic unless necessary.
- Sound like a real Moroccan person.


RESPONSE RULES:


IF it is a company/service complaint:
- Apologize.
- Mention you understood the issue.
- Say support/team will follow.


IF it is positive feedback:
- Thank naturally.
- Mention what was appreciated.


IF it is a question:
- Answer directly and clearly.


IF it is social/sport/opinion content:
- Do NOT open a support ticket.
- Give a natural social interaction response.


IF the message is unclear:
- Ask for clarification politely.


Never:
- Give generic answers.
- Say "شكرا على كلامك الزوين" without context.
- Invent details not present in the message.


Examples:


Post:
"الخدمة ديالكم زوينة بزاف"

Response:
"شكرا بزاف على الثقة ديالك، فرحانين بلي الخدمة عجباتك ❤️"


Post:
"بسببكم ضاع ليا الوقت ومازال ما تحلش المشكل"

Response:
"سمح لينا بزاف على هاد الإزعاج، فهمنا بلي كاين تأخير فحل المشكل وغادي نخليو الفريق يتابع معاك."


Post:
"الرجاء لعبو اليوم كان رائع"

Response:
"فعلا كانت مقابلة زوينة والأداء كان مميز 👏"


Now analyze this post:

"""
#generation_prompt = ChatPromptTemplate.from_messages(
#[
#("system", system_prompt),

#("user",
"""
Social media post:

{tweet}


Sentiment detected by model:
{sentiment}


Analyze the context and generate the appropriate Moroccan Darija response.
Return ONLY the final response.
"""
#)
#]
#)

# Chain LLM

"""response_chain = (
    generation_prompt
    | llm
    | StrOutputParser()
)



# ==========================================================
# 3. LANGGRAPH NODE (CORRECTED & OPTIMIZED)
# ==========================================================

def generate_contextual_response_node(state):
    # 1. جلب البيانات من الـ State الحالي للـ Graph
    tweet = state.get("tweet", "")
    sentiment = state.get("sentiment", "Neutral")
    score = state.get("score", 0.0)

    try:
        # 2. استدعاء الـ LLM لتوليد الرد المناسب للسياق
        response = response_chain.invoke(
            {
                "tweet": tweet,
                "sentiment": sentiment
            }
        )
        # تنظيف النص من أي فراغات زائدة
        response = response.strip()

    except Exception as e:
        print("❌ LLM ERROR DURING GENERATION:", e)
        response = "سمح لينا بزاف، كاين ضغط على النظام حالياً. غادي يتواصل معاك الدعم فوراً."

    # 3. تحديد الـ Action بطريقة آمنة ومطابقة للـ Router
    if sentiment == "Positive":
        action = "Envoyer Remerciement"
    elif sentiment == "Negative":
        action = "Ouvrir Ticket Support"
    else:
        action = "Aucune"

    # 4. CRITICAL: إرجاع الـ State كامل مكمول باش الـ Pipeline فـ agent_darija ما يلقاش قيم ناقصة
    return {
        "tweet": tweet,
        "sentiment": sentiment,
        "score": score,
        "action_requise": action,
        "reponse_generee": response
    }"""

import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# ==========================================================
# 1. LLM CONFIGURATION (Llama 3.3 70B)
# ==========================================================
llm = ChatGroq(
    groq_api_key="gsk_xxxx",
    model="llama-3.3-70b-versatile",
    temperature=0.2
)

# ==========================================================
# 2. PROMPT AGENT DARIJA (البرومبت ديالك كيفما خليتيه)
# ==========================================================
system_prompt = """
You are an intelligent Moroccan Darija social media AI agent.

Your task is to understand any Moroccan social media post and generate the most appropriate response.

The messages can be about:
- companies and products
- customer complaints
- social issues
- football and sports
- personal opinions
- news
- jokes
- appreciation
- questions

IMPORTANT:
Do NOT assume every message is a customer complaint.

First internally analyze:

1) Identify the context:
- Commercial complaint
- Commercial question
- Positive feedback
- Social discussion
- Sport discussion
- Opinion
- Information/news
- Other

2) Identify the user's intention:
- Asking for help
- Complaining
- Thanking
- Sharing opinion
- Reacting emotionally
- Just commenting


Then generate the response.


LANGUAGE RULES:

- Reply ONLY in Moroccan Darija.
- Use natural Moroccan expressions.
- Avoid Egyptian Arabic.
- Avoid Modern Standard Arabic unless necessary.
- Sound like a real Moroccan person.


RESPONSE RULES:


IF it is a company/service complaint:
- Apologize.
- Mention you understood the issue.
- Say support/team will follow.


IF it is positive feedback:
- Thank naturally.
- Mention what was appreciated.


IF it is a question:
- Answer directly and clearly.


IF it is social/sport/opinion content:
- Do NOT open a support ticket.
- Give a natural social interaction response.


IF the message is unclear:
- Ask for clarification politely.


Never:
- Give generic answers.
- Say "شكرا على كلامك الزوين" without context.
- Invent details not present in the message.


Examples:


Post:
"الخدمة ديالكم زوينة بزاف"

Response:
"شكرا بزاف على الثقة ديالك، فرحانين بلي الخدمة عجباتك ❤️"


Post:
"بسببكم ضاع ليا الوقت ومازال ما تحلش المشكل"

Response:
"سمح لينا بزاف على هاد الإزعاج، فهمنا بلي كاين تأخير فحل المشكل وغادي نخليو الفريق يتابع معاك."


Post:
"الرجاء لعبو اليوم كان رائع"

Response:
"فعلا كانت مقابلة زوينة والأداء كان مميز 👏"


Now analyze this post:
"""

generation_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", """
Social media post:
"{tweet}"

Sentiment detected by model:
{sentiment}

Analyze the context and generate the appropriate Moroccan Darija response.
Return ONLY the final response.
""")
])

# Chain LLM
response_chain = generation_prompt | llm | StrOutputParser()

# ==========================================================
# 3. LANGGRAPH NODE (المصلحة هندسياً)
# ==========================================================
def generate_contextual_response_node(state):
    tweet = state.get("tweet", "")
    sentiment = state.get("sentiment", "Neutral")
    score = state.get("score", 0.0)

    try:
        # استدعاء الموديل
        response = response_chain.invoke({
            "tweet": tweet,
            "sentiment": sentiment
        })
        response = response.strip().replace('"', '') # تنظيف من الـ Quotes
    except Exception as e:
        print("❌ LLM ERROR DURING GENERATION:", e)
        response = "سمح لينا بزاف، وقع مشكل تقني فالتواصل مع الموديل. الفريق غادي يتكلف بالأمر."

    # تحديد الأكشن الآمن بناء على الـ Sentiment
    if sentiment == "Positive":
        action = "Envoyer Remerciement"
    elif sentiment == "Negative":
        action = "Ouvrir Ticket Support"
    else:
        action = "Aucune"

    # إرجاع الـ State كامل مكمول باش الـ Graph يخدم بلا مشاكل
    return {
        "doc_id": state.get("doc_id", ""),
        "tweet": tweet,
        "sentiment": sentiment,
        "score": score,
        "action_requise": action,
        "reponse_generee": response
    }