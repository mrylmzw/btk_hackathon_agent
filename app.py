import os
# Arka plan kütüphanelerinin çekirdek kavgasını en başta bitiriyoruz
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import time
import json

from orchestrator import execute_full_analysis
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

def get_api_key():
    try:
        with open("geminiapi_key.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

os.environ["GOOGLE_API_KEY"] = get_api_key()

st.set_page_config(page_title="M&A Due Diligence", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ M&A Durum Tespiti Ajanı")

def load_data():
    if os.path.exists("final_ma_decision.json"):
        with open("final_ma_decision.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_data()

tab1, tab2, tab3 = st.tabs(["🔍 Analiz Başlat", "📊 Yönetici Özeti", "💬 AI Chat"])

with tab1:
    st.subheader("Yeni Şirket Analizi")
    col1, col2 = st.columns([3, 1])
    with col1:
        ticker = st.text_input("Şirket Sembolü (Örn: AAPL, TSLA)").upper().strip()
    with col2:
        st.write("")
        st.write("")
        if st.button("🚀 Analizi Çalıştır", use_container_width=True):
            if ticker:
                animasyon_alani = st.empty()
                
                with st.spinner(""):
                    animasyon_alani.info(f"⏳ **{ticker} Analizi Başlatıldı...**\n\n"
                                         "🤖 **Ajan 1 Aktif:** SEC 10-K belgeleri yerel RAG veritabanında taranıyor...\n\n"
                                         "⬜ Ajan 2: Beklemede...\n\n"
                                         "⬜ Ajan 3: Beklemede...")
                    time.sleep(2.5) 
                    
                    animasyon_alani.info(f"⏳ **{ticker} Analizi Devam Ediyor...**\n\n"
                                         "✅ **Ajan 1:** SEC belgeleri başarıyla tarandı.\n\n"
                                         "🌐 **Ajan 2 Aktif:** Güncel borsa haberleri ve piyasa krizleri internetten çekiliyor...\n\n"
                                         "⬜ Ajan 3: Beklemede...")
                    time.sleep(2.5)
          
                    animasyon_alani.info(f"⏳ **{ticker} Analizi Son Aşamada...**\n\n"
                                         "✅ **Ajan 1:** SEC belgeleri başarıyla tarandı.\n\n"
                                         "✅ **Ajan 2:** Güncel borsa haberleri internetten çekildi.\n\n"
                                         "🧠 **Ajan 3 Aktif:** İki rapordaki veriler sentezlenip nihai yatırım kararı üretiliyor...")
                    time.sleep(1.5)
                    
                    try:
                        execute_full_analysis(ticker)
                        animasyon_alani.success("✅ Analiz başarıyla tamamlandı! Veriler vitrine aktarıldı.")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        animasyon_alani.error(f"❌ Arka Planda Hata Oluştu: {e}")
            else:
                st.warning("Ticker gir mk.")

with tab2:
    if data:
        sirket = data.get("sirket_adi", "Bilinmiyor")
        skor = data.get("genel_risk_skoru", 0)
        tavsiye = data.get("karar_tavsiyesi", "Bekleniyor")
        bayraklar = data.get("kirmizi_bayraklar", [])
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Hedef Şirket", sirket)
        c2.metric("Nihai Karar", tavsiye, "-Riskli" if skor > 70 else "+Güvenli", delta_color="inverse" if skor > 70 else "normal")
        c3.metric("Risk Skoru", f"%{skor}")
        c4.metric("Kırmızı Bayrak", f"{len(bayraklar)} Adet")
        
        st.divider()
        col_o, col_r = st.columns([1, 1])
        with col_o:
            st.subheader("📄 Yönetici Özeti")
            st.write(data.get("yonetici_ozeti", "-"))
            st.subheader("⚖️ Finansal Çelişkiler")
            st.warning(data.get("finansal_celiskiler", "-"))
        with col_r:
            st.subheader("🚩 Kırmızı Bayraklar")
            if bayraklar:
                for b in bayraklar:
                    st.error(f"• {b}")
            else:
                st.success("Risk bulunamadı.")
    else:
        st.info("Önce 'Analiz Başlat' sekmesinden bir işlem yapmalısınız.")

with tab3:
    import requests
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Bu şirketin en zayıf noktası nedir?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            ph = st.empty()
            if not data:
                ph.markdown("Rapor yok, analiz başlat.")
            elif not os.environ.get("GOOGLE_API_KEY"):
                ph.markdown("API Key eksik.")
            else:
                ph.markdown("Ajan düşünüyor (Korsan API Modu)...")
                try:
                    api_key = os.environ["GOOGLE_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
                    
                    sys_prompt = f"Sen M&A uzmanısın. Şu rapora göre cevap ver: {json.dumps(data, ensure_ascii=False)}"
                    
                    headers = {'Content-Type': 'application/json'}
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"{sys_prompt}\n\nKullanıcı Sorusu: {prompt}"
                            }]
                        }]
                    }
                    response = requests.post(url, headers=headers, json=payload)
                    res_json = response.json()
                    
                    if response.status_code == 200:
                        cevap_metni = res_json['candidates'][0]['content']['parts'][0]['text']
                        ph.markdown(cevap_metni)
                        st.session_state.messages.append({"role": "assistant", "content": cevap_metni})
                    else:
                        hata_detay = res_json.get('error', {}).get('message', 'Bilinmeyen hata')
                        ph.markdown(f"❌ Google API Reddetti ({response.status_code}): {hata_detay}")
                        
                except Exception as e:
                    ph.markdown(f"Hata: {e}")