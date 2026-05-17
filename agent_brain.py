import os
# import streamlit as st  # Arayüze geçtiğimizde import edeceğimiz kütüphane
from typing import Any, Dict, List
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from agent_tools import get_agent_tools

# 1. API Anahtarı Kontrolü
# Eğer terminalden 'set' etmediyseniz, aşağıdaki satırın yorum satırını kaldırıp anahtarınızı yazabilirsiniz:
# os.environ["GEMINI_API_KEY"] = "AIzaSy..."
# KODUN BAŞINA DOĞRUDAN EKLEYİN:
os.environ["GEMINI_API_KEY"] = "AIzaSyBtWhPzT3tYkldFjBBDjxZDLKdGZTzJ92c"

if "GEMINI_API_KEY" not in os.environ or os.environ["GEMINI_API_KEY"].startswith("AIzaSyYour"):
    print("[Hata] Lütfen os.environ[\"GEMINI_API_KEY\"] alanına kendi gerçek API anahtarınızı yazın!")
    exit()

# class HackathonAgentUXHandler(BaseCallbackHandler):
#     """Ajanın adımlarını hem konsola hem de Streamlit arayüzüne CANLI akıtır."""
    
#     def __init__(self):
#         # Streamlit ekranında dönen bir yükleme animasyonu ile durum kutusu açıyoruz
#         # expanded=True sayesinde ajan çalıştıkça içi canlı olarak dolacak
#         self.status_box = st.status("🤖 Ajan işlem döngüsü başlatıldı...", expanded=True)
    
#     def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
#         tool_name = action.tool
#         tool_input = action.tool_input
        
#         # 1. Konsola basmaya devam ediyoruz (Yazılımcı takibi için)
#         print(f"\n🤖 [AJAN DÜŞÜNÜYOR] -> {tool_name} tetikleniyor...")
        
#         # 2. AYNI ANDA STREAMLIT EKRANINI GÜNCELLİYORUZ (Kullanıcı takibi için)
#         # st.status nesnesi içine yazılan her şey arayüzde anlık (real-time) belirir
#         if tool_name == "legal_risk_search_tool":
#             self.status_box.write("⚖️ **Durum:** Şirketin yasal dökümanları ve patent davaları taranıyor...")
#         elif tool_name == "financial_risk_search_tool":
#             self.status_box.write("💰 **Durum:** Şirketin likidite durumu ve borç yapısı inceleniyor...")
#         else:
#             self.status_box.write(f"🔍 **Durum:** `{tool_name}` aracı tetikleniyor...")
            
#         self.status_box.write(f"📌 *Hedef Sorgu:* `{tool_input}`")

#     def on_tool_end(self, output: Any, **kwargs: Any) -> None:
#         data_length = len(str(output))
        
#         # Konsol logu
#         print(f"✅ [VERİ ALINDI] -> {data_length} karakter.")
        
#         # Streamlit arayüzünde alt adım olarak tik işaretiyle görünür
#         self.status_box.write(f"✅ **Veri Alındı:** {data_length} karakter veri hafızaya alındı. Analiz ediliyor...")

#     def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
#         # Ajan nihai cevaba ulaştığında dönen yükleme animasyonunu durdurur 
#         # ve kutuyu yeşil bir "Başarılı" tikine çevirir
#         self.status_box.update(label="🎉 Due Diligence Risk Analizi Tamamlandı!", state="complete")



# === FAZ 7: CANLI UX LOG YAKALAYICI (CALLBACK HANDLER) ===
class HackathonAgentUXHandler(BaseCallbackHandler):
    """Ajanın arka plandaki teknik adımlarını temiz ve kurumsal bir UX akışına dönüştürür."""
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """Ajan bir aracı (tool) çalıştırmaya karar verdiğinde tetiklenir."""
        tool_name = action.tool
        tool_input = action.tool_input
        
        print("\n" + "="*50)
        print(f"🤖 [AJAN DÜŞÜNÜYOR] -> Bir sonraki adıma karar verdim.")
        
        # Araç ismine göre kullanıcı dostu Türkçe durum mesajları üretiyoruz
        if tool_name == "legal_risk_search_tool":
            print(f"⚖️  [DURUM] Şirketin yasal dökümanları ve patent davaları taranıyor...")
        elif tool_name == "financial_risk_search_tool":
            print(f"💰 [DURUM] Şirketin likidite durumu, borç yapısı ve taahhütleri inceleniyor...")
        else:
            print(f"🔍 [DURUM] '{tool_name}' aracı tetikleniyor...")
            
        print(f"📌 [HEDEF SORGU]  -> \"{tool_input}\"")
        print("="*50)

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        """Çalıştırılan araç veritabanından cevabı getirip bitirdiğinde tetiklenir."""
        # Kullanıcıya dökümanın tamamını basıp ekranı kirletmiyoruz, sadece bilgi veriyoruz
        data_length = len(str(output))
        print(f"✅ [VERİ ALINDI]  -> İlgili döküman parçaları başarıyla çekildi ({data_length} karakter veri hafızaya alındı). Analiz ediliyor...")


print("[Beyin] Gemini 2.5 Flash modeli hazırlanıyor...")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.1  # Tutarlılık ve katı format uyumu için düşük sıcaklık
)

print("[Sistem] Yerel ReAct Prompt şablonu yükleniyor...")
react_template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

react_prompt = PromptTemplate.from_template(react_template)

print("[Ajan] ReAct Ajanı oluşturuluyor...")
agent = create_react_agent(llm, get_agent_tools, react_prompt)

# Yürütücü motora (Executor) kendi yazdığımız UX handler'ı teslim ediyoruz.
# verbose=False yaptık çünkü artık kalabalık loglar yerine kendi şık loglarımızı basacağız!
agent_executor = AgentExecutor(
    agent=agent, 
    tools=get_agent_tools, 
    verbose=True, 
    handle_parsing_errors=True,
    callbacks=[HackathonAgentUXHandler()] 
)

if __name__ == "__main__":
    print("\n=== AGENT 1: DUE DILIGENCE RISK ANALİZİ BAŞLADI ===")
    print("[Sistem] Ajan uyandırıldı, döküman analiz görevi başlatılıyor. Lütfen bekleyin...")
    
    # Yeni Katı ve Detaylı JSON Şeması Promptu
    user_query = (
        "Analyze the uploaded company records using your search tools. "
        "Identify critical patent infringements, legal lawsuits, and analyze financial health (liquidity, debt, purchase obligations). "
        "\n\n"
        "CRITICAL RULE: Your Final Answer MUST be ONLY a raw JSON string. Do not wrap it in markdown code blocks like ```json. "
        "The JSON structure must strictly follow this exact schema:\n"
        "{\n"
        "  'legal_risks': [\n"
        "    {\n"
        "      'risk_summary': 'Clear description of the lawsuit or patent issue',\n"
        "      'severity': 'High' or 'Medium' or 'Low',\n"
        "      'risk_score': 1 to 10 (integer),\n"
        "      'source_quote': 'The exact or core sentence from the document text showing this risk',\n"
        "      'location': 'The specific item or section name where it was found (e.g., Item 1A, Item 3)'\n"
        "    }\n"
        "  ],\n"
        "  'financial_risks': [\n"
        "    {\n"
        "      'risk_summary': 'Clear description of the debt, liquidity or commitment issue',\n"
        "      'severity': 'High' or 'Medium' or 'Low',\n"
        "      'risk_score': 1 to 10 (integer),\n"
        "      'source_quote': 'The exact or core sentence/metrics from the text showing this financial risk',\n"
        "      'location': 'The specific item or section name (e.g., Item 7)'\n"
        "    }\n"
        "  ],\n"
        "  'm_and_a_summary': 'Your overall senior M&A expert executive overview summarizing the target company risk profile.'\n"
        "}"
    )
    
    response = agent_executor.invoke({"input": user_query})
    
    print("\n" + "="*50)
    print("=== AJANIN NİHAİ YAPILANDIRILMIŞ RAPOR ÇIKTISI (FAZ 7) ===")
    print("="*50)
    print(response["output"])