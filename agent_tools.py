from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Hafızadaki veritabanı ve embedding modelini yeniden yüklüyoruz
# (Faz 2 ile aynı parametreleri kullanmak zorundayız ki vektörler eşleşsin)
print("[Araçlar] Embedding modeli yükleniyor...")
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-en-v1.5",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

print("[Araçlar] Kayıtlı ChromaDB veritabanına bağlanılıyor...")
db = Chroma(
    persist_directory="./chroma_db", 
    embedding_function=embedding_model
)

# 2. Ajanın kullanacağı filtreli araçları (Tools) tanımlıyoruz
# @tool dekoratörü ve altındaki docstring (açıklama metni) ÇOK KRİTİKTİR.
# LLM, bu açıklamaları okuyarak hangi aracı ne zaman seçeceğine karar verir.

@tool
def legal_risk_search_tool(query: str) -> str:
    """
    Use this tool to search for legal risks, ongoing lawsuits, patent claims, 
    government regulations, fines, and legal proceedings about the company.
    Input should be a specific search query related to legal issues.
    """
    # Sadece 'hukuk' etiketli chunk'lar arasında arama yapar
    docs = db.similarity_search(query, k=4, filter={"bölüm": "hukuk"})
    
    if not docs:
        return "No relevant legal documents found for this query."
        
    # Bulunan sonuçları ajanın rahat okuyabileceği tek bir metin haline getiriyoruz
    results = []
    for i, doc in enumerate(docs):
        results.append(f"[Legal Source {i+1}]:\n{doc.page_content}\n")
    
    return "\n---\n".join(results)


@tool
def financial_risk_search_tool(query: str) -> str:
    """
    Use this tool to search for financial health, revenues, balance sheet details, 
    debts, losses, liquidity issues, and management's discussion about financial risks.
    Input should be a specific search query related to accounting or financial metrics.
    """
    # Sadece 'finans' etiketli chunk'lar arasında arama yapar
    docs = db.similarity_search(query, k=4, filter={"bölüm": "finans"})
    
    if not docs:
        return "No relevant financial documents found for this query."
        
    results = []
    for i, doc in enumerate(docs):
        results.append(f"[Financial Source {i+1}]:\n{doc.page_content}\n")
    
    return "\n---\n".join(results)


# 3. Araçları bir liste altında topluyoruz (Ajanın beynine bu listeyi vereceğiz)
get_agent_tools = [legal_risk_search_tool, financial_risk_search_tool]

if __name__ == "__main__":
    print("\n--- Araç Fonksiyonelliği Doğrulama Testi ---")
    
    # Ajan gibi davranıp aracı manuel test edelim
    print("\n[Test 1] Legal_Risk_Search_Tool çalıştırılıyor...")
    legal_output = legal_risk_search_tool.invoke({"query": "patent infringement and government fines"})
    print(legal_output[:300] + "\n... (Devamı Var) ...")
    
    print("\n[Test 2] Financial_Risk_Search_Tool çalıştırılıyor...")
    financial_output = financial_risk_search_tool.invoke({"query": "liquidity, debt and net sales trends"})
    print(financial_output[:300] + "\n... (Devamı Var) ...")