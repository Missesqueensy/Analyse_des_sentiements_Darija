import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px

# 1. Configuration de la page
st.set_page_config(
    page_title="Darija Sentiment & Agent Hub",
    page_icon="🎯",
    layout="wide"
)

# 2. CSS personnalisé pour le Dark Mode avec texte BLANC PUR
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset et base */
    .stApp {
        background: #0a0a0f;
        font-family: 'Inter', sans-serif;
    }
    
    /* TEXTE BLANC PUR pour tout */
    * {
        color: #ffffff !important;
    }
    
    /* En-tête */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 2rem;
        box-shadow: 0 4px 30px rgba(0,0,0,0.3);
    }
    
    .main-header h1 {
        font-weight: 700;
        font-size: 2.2rem;
        background: linear-gradient(135deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .main-header p {
        color: #ffffff !important;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }
    
    /* Cartes KPI */
    .kpi-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border: 1px solid rgba(255,255,255,0.06);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(167, 139, 250, 0.3);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .kpi-card .label {
        color: #94a3b8 !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    .kpi-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff !important;
        margin-top: 0.3rem;
    }
    
    /* Tabs personnalisées */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #1a1a2e;
        padding: 0.3rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        color: #94a3b8 !important;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: rgba(255,255,255,0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e293b, #334155) !important;
        color: #ffffff !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    /* Expandeurs */
    .streamlit-expanderHeader {
        background: #1a1a2e !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        padding: 0.8rem 1.2rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(167, 139, 250, 0.3) !important;
        background: #1e1e3a !important;
    }
    
    .streamlit-expanderContent {
        background: #11111f !important;
        border-radius: 0 0 10px 10px !important;
        border-left: 1px solid rgba(255,255,255,0.05);
        border-right: 1px solid rgba(255,255,255,0.05);
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding: 1rem !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #0f0f1a !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #1e293b, #334155) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #334155, #475569) !important;
        border-color: rgba(167, 139, 250, 0.3) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Metriques Streamlit */
    .stMetric .stMetricLabel {
        color: #94a3b8 !important;
    }
    
    .stMetric .stMetricValue {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    .stMetric .stMetricDelta {
        color: #94a3b8 !important;
    }
    
    /* Badges de statut */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .badge-positif { background: rgba(34, 197, 94, 0.15); color: #4ade80 !important; }
    .badge-negatif { background: rgba(239, 68, 68, 0.15); color: #f87171 !important; }
    .badge-neutre { background: rgba(251, 191, 36, 0.15); color: #fbbf24 !important; }
    
    /* Separators */
    .custom-divider {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.05), transparent);
        margin: 2rem 0;
    }
    
    /* Info boxes */
    .stAlert {
        background: #1a1a2e !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    .stAlert p {
        color: #ffffff !important;
    }
    
    /* Tables */
    .dataframe {
        background: #1a1a2e !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    .dataframe th {
        background: #1e1e3a !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    .dataframe td {
        color: #ffffff !important;
        border-bottom: 1px solid rgba(255,255,255,0.03) !important;
    }
    
    /* Tous les textes en blanc */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Markdown text */
    .stMarkdown p, .stMarkdown div {
        color: #ffffff !important;
    }
    
    /* Alertes et infos */
    .stAlert .stMarkdown p {
        color: #ffffff !important;
    }
    
    /* Widget labels */
    .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #ffffff !important;
    }
    
    /* Code blocks */
    pre, code {
        color: #ffffff !important;
        background: rgba(255,255,255,0.05) !important;
    }
    
    /* Expander content text */
    .streamlit-expanderContent p, 
    .streamlit-expanderContent div,
    .streamlit-expanderContent span {
        color: #ffffff !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }
</style>
""", unsafe_allow_html=True)

# 3. En-tête du Dashboard
st.markdown("""
<div class="main-header">
    <h1>🎯 Tableau de Bord - Sentiment & Agent</h1>
    <p>Analyse en temps réel de 61k tweets en Darija • Hub intelligent pour la gestion des interactions</p>
</div>
""", unsafe_allow_html=True)

# 4. Connexion à MongoDB
@st.cache_resource
def get_mongo_client():
    return MongoClient("mongodb://localhost:27017/")

client = get_mongo_client()
db = client["darija_social_media"]
collection = db["tweets_sentiment"]

# 5. Données et statistiques
total_docs = collection.count_documents({})
pos_count = collection.count_documents({"analysis.sentiment": "Positive"})
neg_count = collection.count_documents({"analysis.sentiment": "Negative"})
neu_count = collection.count_documents({"analysis.sentiment": "Neutral"})
unprocessed_count = collection.count_documents({"agent_decision.action_to_take": "Aucune"})

# 6. Cartes KPI
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="label">📊 Total Tweets</div>
        <div class="value">{total_docs:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="label">🟢 Positifs</div>
        <div class="value" style="color:#4ade80 !important;">{pos_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="label">🔴 Négatifs</div>
        <div class="value" style="color:#f87171 !important;">{neg_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="label">🟡 Neutres</div>
        <div class="value" style="color:#fbbf24 !important;">{neu_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="label">⏳ En attente Agent</div>
        <div class="value" style="color:#60a5fa !important;">{unprocessed_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

# 7. Graphique des sentiments
st.markdown("### 📈 Répartition des Sentiments")

if total_docs > 0:
    p_pos = (pos_count / total_docs) * 100
    p_neg = (neg_count / total_docs) * 100
    p_neu = (neu_count / total_docs) * 100
    
    df_chart = pd.DataFrame({
        "Sentiment": ["Positive", "Negative", "Neutral"],
        "Nombre de Tweets": [pos_count, neg_count, neu_count],
        "Pourcentage": [f"{p_pos:.1f}%", f"{p_neg:.1f}%", f"{p_neu:.1f}%"]
    })
    
    fig = px.bar(
        df_chart,
        x="Sentiment",
        y="Nombre de Tweets",
        text="Pourcentage",
        color="Sentiment",
        color_discrete_map={
            "Positive": "#4ade80",
            "Negative": "#f87171",
            "Neutral": "#fbbf24"
        },
        labels={"Nombre de Tweets": "Nombre de Tweets", "Sentiment": "Classe"}
    )
    
    fig.update_traces(
        textposition='outside',
        textfont=dict(size=14, color="#ffffff", family="Inter"),
        hovertemplate="<b>%{x}</b><br>Nombre: %{y}<br>%{text}<extra></extra>"
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ffffff", family="Inter"),
        height=350,
        showlegend=False,
        xaxis=dict(
            tickfont=dict(color="#ffffff"),
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            tickfont=dict(color="#ffffff"),
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='rgba(255,255,255,0.1)'
        ),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📭 Aucune donnée disponible pour générer le graphique.")

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

# 8. Hubs par catégorie
st.markdown("### 🤖 Agent Intelligent - Hubs d'Action")

tab_neg, tab_pos, tab_neu = st.tabs([
    "🔴 Réclamations", 
    "🟢 Remerciements", 
    "🟡 Veille Standard"
])

# ----- Onglet Négatif -----
with tab_neg:
    st.markdown("##### 🚨 Tickets de Support Actifs")
    neg_tweets = list(collection.find(
        {"analysis.sentiment": "Negative", "agent_decision.action_to_take": {"$ne": "Aucune"}}
    ).sort("_id", -1).limit(10))
    
    if neg_tweets:
        for idx, doc in enumerate(neg_tweets):
            with st.expander(f"🎫 Ticket #{idx+1} - {doc.get('user', 'Inconnu')} - {doc.get('timestamp', 'N/A')}"):
                st.markdown(f"**Texte :** {doc.get('text_raw', '')}")
                score_conf = doc.get("analysis", {}).get("confidence_score", 1.0)
                st.metric("🎯 Score de Confiance", f"{score_conf:.1%}")
                st.warning(f"**Action :** {doc.get('agent_decision', {}).get('action_to_take', 'Aucune')}")
                reponse = doc.get("agent_decision", {}).get("generated_output", "")
                if not reponse:
                    reponse = doc.get("agent_decision", {}).get("reponse_automatique", "N/A")
                st.info(f"**📝 Réponse :** {reponse}")
    else:
        st.info("✅ Aucun ticket négatif en attente.")

# ----- Onglet Positif -----
with tab_pos:
    st.markdown("##### 💝 Interactions Positives")
    pos_tweets = list(collection.find(
        {"analysis.sentiment": "Positive", "agent_decision.action_to_take": {"$ne": "Aucune"}}
    ).sort("_id", -1).limit(10))
    
    if pos_tweets:
        for idx, doc in enumerate(pos_tweets):
            with st.expander(f"✨ #{idx+1} - {doc.get('user', 'Inconnu')}"):
                st.markdown(f"**Texte :** {doc.get('text_raw', '')}")
                score_conf = doc.get("analysis", {}).get("confidence_score", 1.0)
                st.metric("🎯 Score de Confiance", f"{score_conf:.1%}")
                reponse = doc.get("agent_decision", {}).get("generated_output", "")
                if not reponse:
                    reponse = doc.get("agent_decision", {}).get("reponse_automatique", "N/A")
                st.success(f"**💬 Réponse :** {reponse}")
    else:
        st.info("📭 Aucune interaction positive à afficher.")

# ----- Onglet Neutre -----
with tab_neu:
    st.markdown("##### 📋 Veille et Monitoring")
    neu_tweets = list(collection.find(
        {"analysis.sentiment": "Neutral"}
    ).sort("_id", -1).limit(10))
    
    if neu_tweets:
        data_table = []
        for doc in neu_tweets:
            score_conf = doc.get("analysis", {}).get("confidence_score", 1.0)
            data_table.append({
                "👤 Utilisateur": doc.get("user", "Inconnu"),
                "📝 Texte": doc.get("text_raw", "")[:60] + "..." if len(doc.get("text_raw", "")) > 60 else doc.get("text_raw", ""),
                "🎯 Score": f"{score_conf:.1%}",
                "📌 Statut": "Archivé"
            })
        st.dataframe(pd.DataFrame(data_table), use_container_width=True)
    else:
        st.info("📭 Aucun tweet neutre trouvé.")

# 9. Sidebar - Contrôle
st.sidebar.markdown("### ⚙️ Contrôle du Flux")
st.sidebar.markdown("---")
st.sidebar.info("🔮 Données en temps réel depuis MongoDB")
st.sidebar.markdown(f"**📊 Total indexé :** `{total_docs:,}` tweets")

if st.sidebar.button("🔄 Actualiser", use_container_width=True):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("💡 Dashboard v2.0 • Dark Mode Clean")