```markdown
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

### 4. API Anahtarını Yapılandırın

Ajanın çalışabilmesi için geçerli bir Gemini API anahtarına ihtiyacınız vardır.

* `agent_brain.py` dosyasını açın.
* `os.environ["GEMINI_API_KEY"] = "AIzaSy..."` alanına kendi güncel API anahtarınızı yapıştırın ve dosyayı kaydedin.

### 5. Veritabanını İlklendirin (İlk Çalıştırma)

`.gitignore` kuralları gereği ham dökümanlar ve vektör veritabanı depoya yüklenmez. Ajanı çalıştırmadan önce veritabanının otomatik oluşturulması için `vector_storage.py` dosyasını bir kez çalıştırmalısınız. Bu işlem hedef şirketin (Örn: AAPL) dökümanlarını indirecek, akıllı chunking yapacak ve yerel ChromaDB'yi besleyecektir:

```bash
python vector_storage.py

```

*(Not: İlk çalıştırmada embedding modeli HuggingFace'den indirileceği için internet hızınıza bağlı olarak birkaç dakika sürebilir.)*

### 6. Ajanı Tetikleyin

Veritabanı başarıyla oluştuktan sonra, ReAct ajanını başlatabilir ve risk analiz raporunu üretebilirsiniz:

```bash
python agent_brain.py

```

---

## 🛠️ Proje Mimari Yapısı

* **`ingestion.py`:** SEC sisteminden 10-K raporlarını indirir, HTML etiketlerini normalleştirir, tabloları Markdown formatına çevirir ve veriyi `Item 1A/3` (Hukuk) ve `Item 7` (Finans) olarak esnek regex yapısıyla akıllıca ayırır.
* **`vector_storage.py`:** Ayrıştırılan metinleri anlamsal bütünlüğü koruyarak alt parçalara (chunks) böler, `BAAI/bge-large-en-v1.5` modeliyle embedding işlemine sokar ve metadata etiketleriyle birlikte yerel `chroma_db` klasörüne kaydeder.
* **`agent_tools.py`:** Ajanın veritabanında nokta atışı arama yapmasını sağlayan, arkasında otomatik metadata filtreleri barındıran kısıtlı arama araçlarını (`Tools`) tanımlar.
* **`agent_brain.py`:** `gemini-2.5-flash` (veya sunumda `gemini-2.5-pro`) modelini kullanarak ReAct akıl yürütme döngüsünü yönetir ve nihai çıktıyı katı bir JSON string formatında döndürür.

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