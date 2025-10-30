# pages/3_Policy_Portal.py
import streamlit as st
import requests

# --- Import shared functions ---
from utils import apply_custom_css, t, language_toggle
from project_bot import render_project_bot # (NEW) Import floating bot

# --- Apply CSS and Language Toggle ---
apply_custom_css()
with st.sidebar:
    language_toggle()

# Get current language
lang = st.session_state.lang

# ----------------- Policies List (Links to real PDFs) -----------------
POLICIES = [
    {"year": "2004", "title": "Organic Farming Policy", "amount": "90% on inputs (Rs. 10,000/ha)", "free": "Free certification training", "desc": "Promotes organic clusters and eco-practices.", "pdf_url": "http://ofai.s3.amazonaws.com/Kar_OF_policy_2004.pdf"},
    {"year": "2006", "title": "Agricultural Policy", "amount": "Rs. 5,000/ha for hybrids", "free": "Free soil testing", "desc": "Targets 4.5% growth with WTO adaptations.", "pdf_url": "https://raitamitra.karnataka.gov.in/storage/pdf-files/Agri%20Policy%20eng.pdf"},
    {"year": "2017", "title": "Organic Crop Cluster Development", "amount": "50% certification (Rs. 1 lakh/group)", "free": "Free market linkages", "desc": "Supply chain for certified organics.", "pdf_url": "https://bangalorerural.nic.in/en/agriculture/"},
    {"year": "2022", "title": "Samagra Krishi Abhiyaana", "amount": "Rs. 25,000 for milch animals (50%)", "free": "Free crop insurance for small farmers", "desc": "Rs. 5 lakh suicide relief; poly tarpal (90% subsidy).", "pdf_url": "https://www.manage.gov.in/fpoacademy/SGSchemes/karnataka.pdf"},
    {"year": "2023", "title": "Annual Agriculture Report", "amount": "Rs. 50,000 for pump sets (50%)", "free": "Free ATMA extension services", "desc": "Rainfed crop support, Krishi Honda (90% subsidy).", "pdf_url": "https.raitamitra.karnataka.gov.in/info-4/ANNUAL+REPORT/en"},
    {"year": "2024", "title": "Raitha Samruddhi Yojane", "amount": "Rs. 1 crore for harvester hubs (50-70%)", "free": "Free food processing training", "desc": "Consolidated schemes for sustainable farming.", "pdf_url": "https://www.thehindubusinessline.com/economy/agri-business/karnatakas-new-agri-scheme-to-make-farming-sustainable-lucrative/article67853797.ece"},
    {"year": "2024", "title": "Farm Machinery Hubs", "amount": "Rs. 50 lakh for harvesters (50%)", "free": "Free labor shortage support", "desc": "Addresses harvest issues; 70% for FPOs.", "pdf_url": "https://www.thehindu.com/news/national/karnataka/karnataka-government-issues-guidelines-for-farm-machinery-hubs-to-address-problem-of-labour-shortage-during-harvest-season/article67768663.ece"},
    {"year": "2025", "title": "PM KISAN Supplements", "amount": "Rs. 6,000/year + Rs. 5,000 state", "free": "Free insurance integration", "desc": "Direct income for small farmers.", "pdf_url": "https.raitamitra.karnataka.gov.in/info-2/Pradhan+Mantri+KIsan+Samman+Nidhi+(PM+KISAN)/en"},
    {"year": "2025", "title": "Livestock Schemes (Pashu Bhagya)", "amount": "Rs. 1.20 lakh loan (33-50% subsidy)", "free": "Free for SC/ST widows", "desc": "Cattle/sheep units; 50% for minorities.", "pdf_url": "https://slbckarnataka.com/UserFiles/slbc/State%20Govt%20scheme%20details.pdf"},
    {"year": "2025", "title": "Fertilizer & Manure Subsidy", "amount": "50% on bio-fertilizers (Rs. 50,000 max)", "free": "Free micronutrients for small farms", "desc": "Gypsum, green manure distribution.", "pdf_url": "https.raitamitra.karnataka.gov.in/info-2/FERTILIZER+AND+MANURE/en"},
]

# ----------------- Session State (Page Specific) -----------------
if "selected_policy" not in st.session_state:
    st.session_state.selected_policy = None

# ----------------- Title -----------------
st.markdown(f"<h1 style='text-align:center;'>{t('Karnataka Agriculture Policies Portal', lang)}</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align:center;'>{t('All Government Schemes & Subsidies', lang)}</h3>", unsafe_allow_html=True)

# ----------------- Main UI (NEW SCROLLABLE BOX) -----------------
st.markdown("---")
st.markdown(f"### {t('Policy Details', lang)}")
details_container = st.container(height=350) # The stable, scrollable box

if st.session_state.selected_policy is None:
    details_container.info(t("Select a policy from the list below to see its details here.", lang))
else:
    p = st.session_state.selected_policy
    details_container.markdown(f"#### {t(p['title'], lang)} ({p['year']})")
    details_container.markdown(f"**{t('Description', lang)}:** {t(p['desc'], lang)}")
    details_container.markdown(f"**{t('Subsidy', lang)}:** {p['amount']}")
    details_container.markdown(f"**{t('Free Benefit', lang)}:** {t(p['free'], lang)}")
    
    col1, col2 = details_container.columns(2)
    with col1:
        if st.button(t("Apply for This Scheme", lang), key=f"apply_{p['title']}", type="primary"):
            st.success(t("This is a demo. In a real app, this would open an application form.", lang))
    with col2:
        st.markdown(f'<a href="{p["pdf_url"]}" target="_blank" style="text-decoration: none;">' +
                    f'<button style="background:linear-gradient(45deg,#555,#888);color:white;border:none;border-radius:30px;padding:12px 24px;font-weight:600;width:100%;cursor:pointer;">' +
                    f'{t("Read Full PDF", lang)}</button></a>',
                    unsafe_allow_html=True)

# --- 2. List of All Policies ---
st.markdown("---")
st.markdown(f"### {t('Available Schemes', lang)}")
col1, col2 = st.columns(2)
for i, p in enumerate(POLICIES):
    target_col = col1 if i % 2 == 0 else col2
    with target_col.expander(f"**{p['year']} - {t(p['title'], lang)}**", expanded=False):
        st.markdown(f"**{t('Subsidy', lang)}:** {p['amount']}")
        st.markdown(f"**{t('Benefit', lang)}:** {t(p['free'], lang)}")
        
        if st.button(t("Show Details", lang), key=f"details_{i}"):
            st.session_state.selected_policy = p
            st.rerun()

# (NEW) Render the floating bot at the end
render_project_bot()