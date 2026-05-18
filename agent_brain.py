import os
from typing import Any
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# Yeni geliştirdiğimiz modülleri ve akıllı fonksiyonları içeri aktarıyoruz
from agent_tools import get_agent_tools
from vector_storage import ingest_and_store_ticker

# API Anahtarı Tanımlama (Mevcut çalışan anahtarınız korundu)
os.environ["GEMINI_API_KEY"] = "AIzaSyDCgN4CeMMzkfuIZ-_JKuiTIyP6pfFL52k"

if "GEMINI_API_KEY" not in os.environ or os.environ["GEMINI_API_KEY"].startswith("AIzaSyYour"):
    print("[Hata] Lütfen geçerli bir API anahtarı tanımlayın!")
    exit()


# === CANLI UX LOG YAKALAYICI ===
class HackathonAgentUXHandler(BaseCallbackHandler):
    """Ajanın teknik döngüsünü temiz ve kurumsal bir terminal akışına dönüştürür."""
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        tool_name = action.tool
        tool_input = action.tool_input
        
        print("\n" + "="*50)
        print(f"🤖 [AJAN DÜŞÜNÜYOR] -> Bir sonraki adıma karar verdim.")
        
        if tool_name == "legal_risk_search_tool":
            print(f"⚖️  [DURUM] Hedef şirketin yasal dökümanları ve patent davaları taranıyor...")
        elif tool_name == "financial_risk_search_tool":
            print(f"💰 [DURUM] Hedef şirketin likidite durumu, borç yapısı ve taahhütleri inceleniyor...")
        else:
            print(f"🔍 [DURUM] '{tool_name}' aracı tetikleniyor...")
            
        print(f"📌 [HEDEF SORGU]  -> \"{tool_input}\"")
        print("="*50)

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        data_length = len(str(output))
        print(f"✅ [VERİ ALINDI]  -> İlgili döküman parçaları başarıyla çekildi ({data_length} karakter veri hafızaya alındı). Analiz ediliyor...")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("      M&A DUE DILIGENCE AUTOMATED AGENT PANEL v2.0   ")
    print("="*50)
    
    # Kullanıcıdan veya jüriden dinamik borsa kodunu alıyoruz
    target_ticker = input("\n🔍 Analiz etmek istediğiniz şirket kodunu girin (Örn: AAPL, TSLA, MSFT): ").strip().upper()
    
    if not target_ticker:
        print("[Hata] Şirket kodu boş bırakılamaz!")
        exit()
        
    print(f"\n🗄️  {target_ticker} için yerel hafıza katmanı kontrol ediliyor...")
    
    # --- ⚡ AKILLI OTOMASYON TETİKLEYİCİSİ ---
    # vector_storage içindeki yeni fonksiyonumuz çalışıyor: Yerelde varsa 1 saniyede geçer, yoksa otomatik indirip indeksler!
    ingest_and_store_ticker(target_ticker)
    
    print(f"\n🚀 {target_ticker} için kısıtlanmış araç seti fabrikadan çekiliyor...")
    # Sadece girdiğimiz şirkete ait verileri okuyabilecek KATI filtreli araçları üretiyoruz
    dynamic_tools = get_agent_tools(target_ticker)
    
    print("[Beyin] Gemini 2.5 Flash modeli hazırlanıyor...")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
    
    # ReAct Şablon Yapısı
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
    
    # Ajanı ve Yürütücü Motoru dinamik araçlarla tam burada ayağa kaldırıyoruz
    agent = create_react_agent(llm, dynamic_tools, react_prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=dynamic_tools, 
        verbose=False, # Karmaşık ham logları gizle
        handle_parsing_errors=True,
        callbacks=[HackathonAgentUXHandler()] # Şık log akışımız devrede
    )
    
    print(f"\n🔥 Yapay zeka akıl yürütme döngüsü başladı. {target_ticker} analiz ediliyor...")
    
    # Gelişmiş, Skorlamalı ve Atıflı JSON Prompt Sözleşmesi
    user_query = (
        f"Analyze the corporate records and SEC filings specifically for the target company: {target_ticker}. "
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
    print(f"=== AJANIN NİHAİ RAPOR ÇIKTISI ({target_ticker}) ===")
    print("="*50)
    print(response["output"])