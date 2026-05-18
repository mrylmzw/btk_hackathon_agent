from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool

# === 🧠 GLOBAL BAĞLANTILAR ===
# Embedding modeli ve veritabanı bağlantısı sadece bir kez, globalde ayağa kalkar.
print("[Araçlar] Ortak embedding modeli hafızaya yükleniyor...")
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-en-v1.5",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

print("[Araçlar] Yerel ChromaDB havuzuna bağlantı kuruluyor...")
db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)


def get_agent_tools(target_ticker: str):
    """
    Ajanın kullanacağı arama araçlarını dinamik olarak üretir.
    İçerideki katı '$and' filtresi sayesinde ajan asla aranan şirketin dışına çıkamaz.
    """
    ticker_clean = target_ticker.upper().strip()

    @tool
    def legal_risk_search_tool(query: str) -> str:
        """
        Use this tool to search for legal risks, ongoing lawsuits, patent claims, 
        government regulations, fines, and legal proceedings about the company.
        Input should be a specific search query related to legal issues.
        """
        # ⚖️ ÇİFT KRİTERLİ KATI FİLTRE: Hem hukuk bölümü olacak HEM DE sadece bu şirket olacak!
        docs = db.similarity_search(
            query, 
            k=4, 
            filter={"$and": [{"bölüm": "hukuk"}, {"ticker": ticker_clean}]}
        )
        
        if not docs:
            return f"No relevant legal records found for {ticker_clean} regarding this query."
            
        results = []
        for i, doc in enumerate(docs):
            results.append(f"[Legal Source {i+1}]:\n{doc.page_content}\n")
        
        return "\n---\n".join(results)

    @tool
    def financial_risk_search_tool(query: str) -> str:
        """
        Use this tool to search for financial health, revenues, balance sheet details, 
        debts, losses, liquidity issues, and financial risks.
        Input should be a specific search query related to accounting or financial metrics.
        """
        # 💰 ÇİFT KRİTERLİ KATI FİLTRE: Hem finans bölümü olacak HEM DE sadece bu şirket olacak!
        docs = db.similarity_search(
            query, 
            k=4, 
            filter={"$and": [{"bölüm": "finans"}, {"ticker": ticker_clean}]}
        )
        
        if not docs:
            return f"No relevant financial records found for {ticker_clean} regarding this query."
            
        results = []
        for i, doc in enumerate(docs):
            results.append(f"[Financial Source {i+1}]:\n{doc.page_content}\n")
        
        return "\n---\n".join(results)

    # Ajan yürütücüsüne (Executor) teslim edilecek dinamik araç listesi
    return [legal_risk_search_tool, financial_risk_search_tool]


# === DOSYA DOĞRULAMA TEST ALANI ===
if __name__ == "__main__":
    print("\n--- Dinamik Araç Fonksiyonelliği Doğrulama Testi ---")
    
    # Test etmek istediğimiz şirketi seçiyoruz
    TEST_TICKER = "AAPL"
    
    # Fabrikadan o şirkete özel kısıtlanmış araç listesini alıyoruz
    test_tools = get_agent_tools(TEST_TICKER)
    legal_tool = test_tools[0]
    financial_tool = test_tools[1]
    
    print(f"\n[Test 1] {TEST_TICKER} için Legal_Risk_Search_Tool çalıştırılıyor...")
    legal_output = legal_tool.invoke({"query": "patent infringement and government fines"})
    print(legal_output[:300] + "\n... (Devamı Var) ...")
    
    print(f"\n[Test 2] {TEST_TICKER} için Financial_Risk_Search_Tool çalıştırılıyor...")
    financial_output = financial_tool.invoke({"query": "liquidity, debt and purchase obligations"})
    print(financial_output[:300] + "\n... (Devamı Var) ...")