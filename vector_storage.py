import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
# Faz 1'deki ayrıştırma fonksiyonumuzu içeri aktarıyoruz
from ingestion import find_full_submission_path, parse_and_categorize_sec

def prepare_documents(parsed_data):
    """
    Hukuk ve finans metinlerini daha küçük parçalara (chunk) ayırır
    ve her parçaya ait olduğu bölümün etiketini (metadata) basar.
    """
    # 1000 karakterlik parçalar, 200 karakter birbiri üzerine binecek (bağlam kaybolmasın diye)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = []

    # Hukuk metnini parçala ve etiketle
    if parsed_data["hukuk_metni"]:
        chunks = text_splitter.split_text(parsed_data["hukuk_metni"])
        for chunk in chunks:
            documents.append(Document(page_content=chunk, metadata={"bölüm": "hukuk"}))

    # Finans metnini parçala ve etiketle
    if parsed_data["finans_metni"]:
        chunks = text_splitter.split_text(parsed_data["finans_metni"])
        for chunk in chunks:
            documents.append(Document(page_content=chunk, metadata={"bölüm": "finans"}))

    return documents

def create_vector_db(documents, db_directory="./chroma_db"):
    """
    Dökümanları BAAI/bge-large-en-v1.5 modeli ile embedding işlemine sokar
    ve ChromaDB'ye kalıcı (persistent) olarak kaydeder.
    """
    print("\n[Embedding] Model yükleniyor ve vektörler hesaplanıyor...")
    print("Not: İlk çalıştırmada model HuggingFace'den indirileceği için biraz sürebilir.")
    
    # Kararlaştırdığımız güçlü genel embedding modeli
    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={'device': 'cpu'}, # Eğer GPU varsa 'cuda' yazılabilir
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print(f"[ChromaDB] {len(documents)} adet döküman parçası veritabanına indeksleniyor...")
    
    # Veritabanını oluştur ve diske kaydet
    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=db_directory
    )
    
    print(f"[Başarılı] Veritabanı '{db_directory}' klasörüne kalıcı olarak kaydedildi.")
    return vector_db

if __name__ == "__main__":
    TARGET_TICKER = "AAPL"
    
    # Faz 1'deki mekanizma ile dosyayı bulup ayrıştırıyoruz
    sample_path = find_full_submission_path(TARGET_TICKER)
    
    if sample_path and os.path.exists(sample_path):
        # 1. Metinleri hukuk/finans diye ayır
        raw_data = parse_and_categorize_sec(sample_path)
        
        # 2. Bu metinleri etiketli küçük parçalara (Document nesnelerine) dönüştür
        processed_docs = prepare_documents(raw_data)
        
        # 3. Vektör veritabanını oluştur
        db = create_vector_db(processed_docs)
        
        # 4. Küçük bir test araması yapalım (Filtreleme çalışıyor mu?)
        print("\n--- Veritabanı Filtreleme Testi ---")
        # Sadece hukuk bölümünde "lawsuit" (dava) kelimesini aratalım
        test_results = db.similarity_search(
            "lawsuit", 
            k=2, 
            filter={"bölüm": "hukuk"}
        )
        
        print(f"Hukuk filtresiyle bulunan sonuç sayısı: {len(test_results)}")
        if test_results:
            print(f"İlk sonuç örneği (Metadata: {test_results[0].metadata}):")
            print(test_results[0].page_content[:150] + "...")
            
    else:
        print(f"Hata: {TARGET_TICKER} dökümanı bulunamadığı için Faz 2 başlatılamadı.")