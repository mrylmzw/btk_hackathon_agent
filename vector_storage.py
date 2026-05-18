import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
# Faz 1'deki güncellediğimiz yeni fonksiyonu içeri aktarıyoruz
from ingestion import get_company_data

def prepare_documents(parsed_data, ticker):
    """
    Hukuk ve finans metinlerini daha küçük parçalara (chunk) ayırır
    ve her parçaya hem BÖLÜM hem de ŞİRKET KODU (ticker) etiketini basar.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = []
    ticker = ticker.upper().strip()

    # Hukuk metnini parçala ve çift etiketle (ticker eklendi)
    if parsed_data and parsed_data.get("hukuk_metni"):
        chunks = text_splitter.split_text(parsed_data["hukuk_metni"])
        for chunk in chunks:
            documents.append(Document(
                page_content=chunk, 
                metadata={"bölüm": "hukuk", "ticker": ticker}
            ))

    # Finans metnini parçala ve çift etiketle (ticker eklendi)
    if parsed_data and parsed_data.get("finans_metni"):
        chunks = text_splitter.split_text(parsed_data["finans_metni"])
        for chunk in chunks:
            documents.append(Document(
                page_content=chunk, 
                metadata={"bölüm": "finans", "ticker": ticker}
            ))

    return documents

def create_vector_db(documents, db_directory="./chroma_db"):
    """
    Döküman parçalarını mevcut ChromaDB havuzuna ekler veya sıfırdan oluşturur.
    Chroma.from_documents yapısı dizin zaten varsa verileri silmez, ekleme yapar.
    """
    print("\n[Embedding] Model yükleniyor ve vektörler hesaplanıyor...")
    
    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={'device': 'cpu'}, # Varsa 'cuda' yapılabilir
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print(f"[ChromaDB] {len(documents)} adet döküman parçası veritabanı havuzuna indeksleniyor...")
    
    # Mevcut veritabanını bozmadan üzerine yeni şirket dökümanlarını ekler
    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=db_directory
    )
    
    print(f"[Başarılı] Veriler '{db_directory}' içerisindeki ortak havuza kalıcı olarak eklendi.")
    return vector_db

# === DIŞARIDAN (AGENT'TAN) ÇAĞRILACAK ANA ORKESTRASYON FONKSİYONU ===
def ingest_and_store_ticker(ticker, db_directory="./chroma_db"):
    """
    Belirtilen ticker için akıllı kontrol yapar: Yerelde varsa HİÇBİR ŞEY YAPMAZ,
    yoksa indirme, parçalama ve veritabanına ekleme adımlarını yürütür.
    """
    ticker = ticker.upper().strip()
    
    # --- ⏱️ KRİTİK OPTİMİZASYON KONTROLÜ ---
    # Eğer veritabanı klasörü zaten varsa, içinde bu şirkete ait veri var mı kontrol et
    if os.path.exists(db_directory):
        # Kontrol için embedding modelini ve mevcut DB'yi geçici olarak ayağa kaldırıyoruz
        embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-en-v1.5",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        db = Chroma(persist_directory=db_directory, embedding_function=embedding_model)
        
        # .get() metodu metadata filtresiyle doğrudan indeks kontrolü yapar (Çok hızlıdır)
        existing_data = db.get(where={"ticker": ticker}, limit=1)
        
        # Eğer bu şirkete ait tek bir döküman parçası bile bulursak işlemi anında bitiriyoruz!
        if existing_data and existing_data.get('ids'):
            print(f"✅ [Sistem Hafızası] '{ticker}' verileri zaten yerel ChromaDB içinde mevcut.")
            print(f"⚡ [Hızlandırma] Tekrar embedding hesaplanmadı, doğrudan mevcut hafıza kullanılacak.")
            return db

    # --- EĞER VERİTABANINDA YOKSA ÇALIŞACAK ESKİ AKIŞ ---
    print(f"⚠️  [Hafıza Eksik] '{ticker}' veritabanında bulunamadı. İlk kurulum başlatılıyor...")
    
    # 1. Ingestion modülünü tetikle (Yoksa indirir, varsa yerelden okur)
    raw_data = get_company_data(ticker)
    
    if not raw_data:
        print(f"[Hata] {ticker} için ham veri alınamadığından veritabanı işlemi iptal edildi.")
        return None
        
    # 2. Metinleri şirket koduyla birlikte çift etiketli chunk'lara böl
    processed_docs = prepare_documents(raw_data, ticker)
    
    if not processed_docs:
        print(f"[Uyarı] {ticker} dökümanından anlamlı bir metin parçası üretilemedi.")
        return None
        
    # 3. Ortak ChromaDB havuzuna ekle
    return create_vector_db(processed_docs, db_directory)


# Tek başına bu dosyayı çalıştırıp test etmek istersek:
if __name__ == "__main__":
    TARGET_TICKER = "AAPL"
    
    print(f"--- Yerel {TARGET_TICKER} İndeksleme ve Test Süreci Başladı ---")
    
    # İLK ÇALIŞTIRMA: Veritabanını oluşturur veya dökümanı işler
    db_instance = ingest_and_store_ticker(TARGET_TICKER)
    
    print("\n--- 🔄 İKİNCİ ÇALIŞTIRMA TESTİ (HIZ KONTROLÜ) ---")
    # İKİNCİ ÇALIŞTIRMA: Az önce eklediğimiz optimizasyon sayesinde 1 saniyede "zaten var" deyip geçecek!
    db_instance_fast = ingest_and_store_ticker(TARGET_TICKER)