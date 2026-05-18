# M&A Due Diligence Agent (Agent 1)

Bu proje, Şirket Birleşme ve Devralmaları (M&A) sürecinde kurumsal belgeleri (SEC dökümanları vb.) otomatik olarak analiz eden, hukuki ve finansal riskleri ayrıştırarak yapılandırılmış JSON formatında rapor üreten ReAct (Reasoning and Acting) tabanlı bir yapay zeka ajanıdır.

---

## 🚀 Yeni Bilgisayarda Kurulum ve Çalıştırma Adımları

Projeyi yeni bir bilgisayarda sıfırdan ayağa kaldırmak için aşağıdaki adımları sırayla takip edin:

### 1. Projeyi Klonlayın
Öncelikle depoyu yerel bilgisayarınıza çekin ve proje klasörüne girin:
```bash
git clone https://github.com/mrylmzw/btk_hackathon_agent.git
cd btk_hackathon_agent

```

### 2. Sanal Ortam (Virtual Environment) Oluşturun ve Aktifleştirin

Proje bağımlılıklarının temiz bir ortamda çalışması için bir sanal ortam kurun:

**Windows için:**

```bash
python -m venv venv
venv\Scripts\activate

```

**Mac / Linux için:**

```bash
python3 -m venv venv
source venv/bin/activate

```

### 3. Bağımlılıkları Yükleyin

Gerekli tüm kütüphaneleri tek seferde yüklemek için `requirements.txt` dosyasını çalıştırın:

```bash
pip install -r requirements.txt

```

### 4. API Anahtarlarını Ayarlayın

Proje klasörünün içine aşağıdaki .txt dosyalarını oluşturun ve sadece ilgili anahtarı içine yapıştırın (tırnak işareti veya boşluk olmadan):

geminiapi_key.txt: Google Gemini API anahtarı.

tavilyapi_key.txt: Tavily AI Search API anahtarı.

langchainapi_key.txt: (Opsiyonel) LangSmith izleme anahtarı.

### 5. 🚀 Çalıştırma


Tüm süreci (indirme, arama ve sentez) tek bir komutla paralel olarak başlatmak için:

```bash
python orchestrator.py
#Sistem size desteklenen şirketlerden birini seçmenizi veya bir ticker (Örn: AAPL, TSLA) girmenizi isteyecektir.
```

### 6. 📈 Çıktılar

📈 Çıktılar
Sistem çalışırken temp_a1_output.json ve temp_a2_output.txt gibi ara raporlar üretir. Nihai analiz sonucu ise final_ma_decision.json dosyasına kaydedilir.

## 📁 Dosya Yapısı
orchestrator.py: Ana yönetim merkezi. Ajanları paralel çalıştırır.

agent_brain.py: Ajan 1'in beyin mekanizması.

agent2_deneme.py: Ajan 2'nin haber tarama mantığı.

agent3_deneme.py: Ajan 3'ün sentez ve karar verme katmanı.

vector_storage.py: RAG için veritabanı yönetimi (ChromaDB).

ingestion.py: SEC verilerinin indirilmesi ve ayrıştırılması.

companies.py: Desteklenen şirketlerin eşleşme listesi.

agent_tools.py: Ajanların kullandığı RAG araçları.

## 📦 Gereksinimler (`requirements.txt`)

Projeyi çalıştırmak için gerekli olan kütüphaneler aşağıda listelenmiştir. Kurulum adımında otomatik yüklenecektir:

```text
sec-edgar-downloader
beautifulsoup4
lxml
langchain-text-splitters
langchain-community
chromadb
langchain-huggingface
sentence-transformers
langchain-google-genai
langchain-classic
langchainhub

```