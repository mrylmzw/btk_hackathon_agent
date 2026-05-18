import os
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import DuckDuckGoSearchResults
from langchain.agents import create_agent
from langchain_core.tools import tool
import yfinance as yf
from tavily import TavilyClient
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.rate_limiters import InMemoryRateLimiter


def setup_environment():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tavily_api_key_path = os.path.join(current_dir, "tavilyapi_key.txt")
    gemini_api_key_path = os.path.join(current_dir, "geminiapi_key.txt")
    langchain_api_key_path = os.path.join(current_dir, "langchainapi_key.txt")
 
    with open(gemini_api_key_path, "r") as f:
        GEMINI_API_KEY = f.read().strip()
 
    with open(langchain_api_key_path, "r") as f:
        LANGSMITH_API_KEY = f.read().strip()
    
    with open(tavily_api_key_path, "r") as f:
        TAVILY_API_KEY = f.read().strip()
 
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_PROJECT"] = "agent_deneme"
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

@tool
def zamana_duyarli_haber_bulucu(ticker: str, gun_sayisi: int) -> str:
    """
    Bu araç, bir şirketin borsa kodu (ticker) için, geçmişe dönük belirtilen gün sayısı 
    (gun_sayisi) kadar arama yapar. Sadece finansal Tier-1 kaynaklardan haberleri çeker.
    """
    try:
        # Tavily Client'i başlatıyoruz
        tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        
        # Tavily'nin harika filtreleme özellikleri: topic="news" ve days parametresi
        response = tavily.search(
            query=f"{ticker} financial news mergers acquisitions crisis",
            topic="news",
            days=gun_sayisi,
            include_domains=["reuters.com", "bloomberg.com", "finance.yahoo.com", "wsj.com", "cnbc.com", "ft.com"],
            max_results=5
        )
        
        if not response.get("results"):
            return f"Hata: {ticker} kodu için son {gun_sayisi} günde güvenilir bir haber bulunamadı."
            
        formatli_cikti = f"--- {ticker.upper()} İÇİN SON {gun_sayisi} GÜNÜN HABERLERİ ---\n\n"
        
        for i, haber in enumerate(response["results"], 1):
            formatli_cikti += f"Haber #{i}:\n"
            formatli_cikti += f"- Başlık: {haber.get('title')}\n"
            formatli_cikti += f"- Yayın Tarihi: {haber.get('published_date', 'Bilinmiyor')}\n"
            formatli_cikti += f"- Bağlantı (URL): {haber.get('url')}\n"
            formatli_cikti += f"- İçerik Özeti: {haber.get('content')}\n"
            formatli_cikti += f"--------------------------------------------------\n"
            
        return formatli_cikti
    except Exception as e:
        return f"Arama aracı çalışırken hata oluştu: {str(e)}" 

def agent2(hedef_sirket):
    setup_environment()
 
    # 1. BEYİN: LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2, 
    )
 
    # 2. ELLER: Arama aracı
    tools = [zamana_duyarli_haber_bulucu]
 
    # 3. KİŞİLİK: Sistem mesajı
    system_message = """Sen acımasız ve detaycı bir M&A (Birleşme ve Satın Alma) Haber Analistisin. 
    GÖREV AKIŞIN:
        1. Kullanıcıdan gelen metindeki 'Şirket Adını' tespit et ve resmi borsa koduna (Ticker) çevir.
        2. Kullanıcıdan gelen metindeki 'Zaman Aralığını' (Örn: Son 3 ay, 1 hafta, 6 ay) tespit et ve bunu matematiksel olarak 'GÜN SAYISINA' çevir. (Örn: 3 ay = 90 gün, 1 hafta = 7 gün, 1 yıl = 365 gün).
        3. Elindeki 'zamana_duyarli_haber_bulucu' aracına bu iki veriyi (ticker ve gun_sayisi) göndererek haberleri çek.
        4. Gelen verileri analiz et, duygu skoru ver ve linkleri KESİNLİKLE ekle.
    
    Cevabını doğrudan jüriye sunulacak kalitede, profesyonel bir finansal rapor formatında ve madde madde yaz."""
 
    # 4. AJANI YARATMAK (LangChain 1.x / LangGraph mimarisi)
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_message
    )
 
    # 5. TEST SENARYOSU
    # hedef_sirket = "Tesla"
    zaman_araligi = "son 6 ay"
    print(f"\n--- {hedef_sirket} İçin {zaman_araligi.upper()}LIK Gündem ve Risk Analizi Başlatılıyor ---\n")
 
    try:
        response = agent.invoke({
            "messages": [
                HumanMessage(content=f"{hedef_sirket} şirketinin {zaman_araligi} içindeki tüm önemli piyasa gelişmelerini, krizlerini ve stratejik hamlelerini araştır. Önceliğin büyük finansal haber siteleri olsun. Bana detaylı, linkleri (URL) eklenmiş bir risk analizi raporu çıkar.")
            ]
        },
        config={"recursion_limit": 15}
        )
 
        # Son mesajı (ajanın nihai cevabı) yazdır
        final_message = response["messages"][-1]
        print("\n--- NİHAİ RAPOR ---")
        if isinstance(final_message.content, list):
            content = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in final_message.content])
        else:
            content = final_message.content

        return(content.replace("\\n", "\n"))
 
    except Exception as e:
        print(f"\nSistem çalışırken bir hata oluştu: {e}")
 
 
if __name__ == "__main__":
    #sadece agent2 fonksiyonunu test ediyoruz
    print(agent2("Tesla"))