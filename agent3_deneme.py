import os
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from agent2_deneme import agent2
import json
from typing import List, TypedDict

def setup_environment():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    gemini_api_key_path = os.path.join(current_dir, "geminiapi_key.txt")
    langchain_api_key_path = os.path.join(current_dir, "langchainapi_key.txt")
 
    with open(gemini_api_key_path, "r") as f:
        GEMINI_API_KEY = f.read().strip()
 
    with open(langchain_api_key_path, "r") as f:
        LANGSMITH_API_KEY = f.read().strip()
    
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_PROJECT"] = "agent_deneme"


# --- 1. AŞAMA: ÇIKTI ŞABLONUNU TANIMLAMA (Hatasız TypedDict Formatı) ---
class NihaiRiskRaporu(TypedDict):
    sirket_adi: str 
    genel_risk_skoru: int 
    karar_tavsiyesi: str 
    kirmizi_bayraklar: List[str] 
    finansal_celiskiler: str 
    yonetici_ozeti: str 

# --- 2. AŞAMA: ANA ÇALIŞTIRMA FONKSİYONU ---
def run_agent3(rag_raporu: str, haber_raporu: str) -> dict:
    """
    Streamlit tarafından çağrılacak ana fonksiyon.
    İki metni alır, sentezler ve Python sözlüğü (dict) döndürür.
    """
    setup_environment()

    # BEYİN: Sentez için 0.0 sıcaklık (Asla halüsinasyon yapma, sadece olanı özetle)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
    
    # YAPI KONTROLÜ: LLM'i TypedDict şablonumuza kilitliyoruz (Zorunlu JSON Çıktısı)
    structured_llm = llm.with_structured_output(NihaiRiskRaporu)

    # KİŞİLİK VE GÖREV
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Sen kıdemli bir M&A (Birleşme ve Satın Alma) Baş Analistisin.
        Görevin, altındaki iki analistten gelen raporları okuyup birleştirmek ve nihai kararı vermektir.
        
        Analist 1 (RAG): Şirketin resmi belgelerini, bilançolarını ve gizli sözleşmelerini (JSON formatında da gelebilir) okur.
        Analist 2 (Haberler): Şirketin son aylarındaki piyasa krizlerini ve itibarını okur.
        
        ÖZELLİKLE ŞUNA DİKKAT ET:
        İki rapor arasında çelişki var mı? Şirket resmi belgesinde "her şey harika" derken, piyasa haberleri "kriz var" diyorsa bu BÜYÜK BİR KIRMIZI BAYRAKTIR ve Risk Skorunu artırmalıdır.
        
        Aşağıdaki alanları kesinlikle doldurarak cevap ver:
        - sirket_adi
        - genel_risk_skoru (0-100 arası sayı)
        - karar_tavsiyesi ('YATIRIM YAP', 'BEKLET / YENİDEN DEĞERLE', 'UZAK DUR')
        - kirmizi_bayraklar (en kritik 3 risk listesi)
        - finansal_celiskiler
        - yonetici_ozeti"""),
        ("human", "Analist 1 (RAG) Raporu:\n{rag}\n\n---\n\nAnalist 2 (Haber) Raporu:\n{haber}")
    ])

    # ZİNCİRİ KUR VE ÇALIŞTIR
    chain = prompt | structured_llm
    
    # Çalıştır (Invoke) ve sonucu döndür
    sonuc = chain.invoke({
        "rag": rag_raporu,
        "haber": haber_raporu
    })
    
    return sonuc


# --- 3. AŞAMA: TEST SENARYOSU ---
if __name__ == "__main__":
    print("Sistem Başlatılıyor...\n")
    
    # 1. Ajan 2'yi ÇALIŞTIR VE ÇIKTIYI AL
    print("Ajan 2 İnterneti Tarıyor...")
    test_haber_raporu = """
    --- Tesla İçin SON 6 AYLIK Gündem ve Risk Analizi Başlatılıyor ---


--- NİHAİ RAPOR ---
## Tesla (TSLA) Son 6 Aylık Piyasa Gelişmeleri, Krizler ve Stratejik Hamleler Risk Analizi Raporu

**Rapor Tarihi:** 17 Mayıs 2024
**Şirket:** Tesla, Inc. (TSLA)
**Zaman Aralığı:** Son 6 Ay (Yaklaşık 180 Gün)

Bu rapor, Tesla'nın son altı aylık dönemdeki önemli piyasa gelişmelerini, karşılaştığı krizleri ve stratejik hamlelerini analiz etmektedir. Analiz, Tier-1 finansal haber kaynaklarından derlenen verilere dayanmaktadır.

---

### 1. Düzenleyici Baskılar ve Yasal Sorunlar (Krizler)

Tesla, "Tam Otonom Sürüş" (Full Self-Driving - FSD) ve "Otopilot" (Autopilot) sistemlerinin pazarlanması ve yetenekleri konusunda ciddi düzenleyici ve yasal baskılarla karşı karşıyadır.

*   **FSD Pazarlama ve Düzenleyici İnceleme:**
    *   **Gelişme:** Kaliforniya Motorlu Taşıtlar Departmanı (DMV), Tesla'nın "Otopilot" ve "Tam Otonom Sürüş" gibi yanıltıcı terimler kullandığı gerekçesiyle şirkete karşı harekete geçti. DMV, Tesla'ya pazarlama dilini değiştirmesi için 60 gün süre verdi, aksi takdirde bayi lisansının askıya alınması riskiyle karşı karşıya kalabilir. Düzenleyici kurum, Tesla'nın sisteminin hala Seviye 2 olduğunu ve sürücülerin dikkatli olması gerektiğini vurguladı.
    *   **Duygu Skoru:** Negatif
    *   **Bağlantı (URL):** [https://finance.yahoo.com/news/tesla-stock-down-regulators-taking-145620972.html](https://finance.yahoo.com/news/tesla-stock-down-regulators-taking-145620972.html)

*   **Müşteri Davaları ve FSD Vaatleri:**
    *   **Gelişme:** Elon Musk'ın 2016'dan bu yana verdiği tam otonom sürüş vaatleri nedeniyle Tesla, Hollanda, Avustralya ve Kaliforniya'da müşteriler tarafından dava ediliyor. Müşteriler, binlerce dolar ödedikleri ancak tam olarak erişemedikleri otonom sürüş özellikleri için geri ödeme talep ediyor. Davaların merkezinde, Wall Street analistlerinin en gelişmiş FSD yazılımını çalıştıramadığını belirttiği eski bir bilgisayar sistemi olan "Donanım 3" (Hardware 3) yer alıyor.    *   **Duygu Skoru:** Negatif
    *   **Bağlantı (URL):** [https://finance.yahoo.com/markets/stocks/articles/elon-musk-promised-self-driving-233127759.html](https://finance.yahoo.com/markets/stocks/articles/elon-musk-promised-self-driving-233127759.html)

---

### 2. Finansal Performans ve Piyasa Gelişmeleri

Tesla'nın temel otomobil satışlarında düşüş yaşanırken, yatırımcı odağı robotaksi ve yapay zeka (AI) hedeflerine kaymıştır.

*   **Sermaye Harcamaları (Capex) Planları ve Hisse Senedi Düşüşü:**
    *   **Gelişme:** Tesla hisseleri, sermaye harcamaları planları nedeniyle düşüş yaşadı. Wells Fargo'dan Colin Langan gibi analistler, Tesla için temel göstergelerin "hala çok zorlu" olduğunu belirtiyor.
    *   **Duygu Skoru:** Negatif
    *   **Bağlantı (URL):** [https://www.cnbc.com/video/2026/04/23/tesla-stock-falls-on-capex-plans-heres-what-investors-need-to-know.html](https://www.cnbc.com/video/2026/04/23/tesla-stock-falls-on-capex-plans-heres-what-investors-need-to-know.html)

*   **Düşen Araç Satışları ve Robotaksi Umutları:**
    *   **Gelişme:** Tesla hisseleri, genel ABD piyasalarında çok az değişiklik olmasına rağmen ön piyasa işlemlerinde %1 civarında düşüş yaşadı. Yatırımcılar, şirketin düşen araç satışlarından ziyade yapay zeka (robotaksi) hedeflerine odaklanmış durumda. Dördüncü çeyrek EPS'nin geçen yıla göre daha düşük olması ve araç teslimatlarının 440.000 birim civarında tahmin edilmesi bekleniyor. Elon Musk'ın bir robotaksi hizmetini güvenlik monitörü olmadan test ettiğini belirtmesi, düzenleyici ilerleme konusunda spekülasyonları artırdı.
    *   **Duygu Skoru:** Karışık (Düşen satışlar negatif, robotaksi umutları pozitif)
    *   **Bağlantı (URL):** [https://finance.yahoo.com/news/tesla-stock-ignores-falling-car-134525026.html](https://finance.yahoo.com/news/tesla-stock-ignores-falling-car-134525026.html)

---

### 3. Stratejik Hamleler ve Potansiyel Birleşmeler

Tesla'nın gelecekteki büyüme stratejileri, yapay zeka yatırımları ve potansiyel şirket birleşmeleri etrafında şekillenmektedir.

*   **SpaceX ile Potansiyel Birleşme İddiaları:**
    *   **Gelişme:** Bloomberg News'in haberine göre, Elon Musk'ın SpaceX'i, Tesla ile potansiyel bir birleşmeyi veya yapay zeka şirketi xAI ile alternatif bir birleşmeyi değerlendiriyor. Bu haberin ardından Tesla'nın hisseleri %3 yükseldi. Bazı yatırımcılar, SpaceX ve elektrikli araç üreticisi Tesla arasında bir birleşmeyi destekliyor. Tesla ayrıca Musk'ın xAI'sine 2 milyar dolar yatırım yaptı ve Cybercab üretiminin bu yıl başlayacağını yineledi.
    *   **Duygu Skoru:** Karışık ila Pozitif (Potansiyel stratejik birleşme, hisse senedi artışı, AI yatırımı)
    *   **Bağlantı (URL):** [https://www.reuters.com/business/autos-transport/elon-musks-spacex-said-consider-merger-with-tesla-bloomberg-news-reports-2026-01-29/](https://www.reuters.com/business/autos-transport/elon-musks-spacex-said-consider-merger-with-tesla-bloomberg-news-reports-2026-01-29/)

---

### Risk Analizi ve Genel Değerlendirme

Son 6 aylık dönemde Tesla, hem önemli stratejik potansiyeller hem de ciddi risk faktörleriyle karşı karşıya kalmıştır.

*   **Ana Riskler:**
    *   **Düzenleyici ve Yasal Riskler:** "Tam Otonom Sürüş" sistemlerinin yetenekleri ve pazarlanması konusundaki düzenleyici incelemeler ve devam eden müşteri davaları, şirketin itibarını ve finansal performansını olumsuz etkileyebilir. Özellikle Kaliforniya DMV'nin bayi lisansını askıya alma tehdidi, operasyonel bir risk oluşturmaktadır.
    *   **Temel Otomobil İşletmesindeki Zayıflıklar:** Düşen araç satışları ve "çok zorlu" olarak nitelendirilen temel göstergeler, şirketin ana gelir kaynağında baskı olduğunu göstermektedir.
    *   **Teknolojik Riskler:** Eski "Donanım 3" sisteminin FSD yazılımını tam olarak çalıştıramaması, teknolojik bir darboğaz ve müşteri memnuniyetsizliği kaynağıdır.

*   **Fırsatlar ve Stratejik Hamleler:**
    *   **Robotaksi ve Yapay Zeka Odaklılık:** Yatırımcıların odağının robotaksi ve yapay zeka hedeflerine kayması, şirketin gelecekteki büyüme potansiyeli için önemli bir katalizör olabilir. Elon Musk'ın robotaksi testleri ve Cybercab üretim planları bu alandaki iddiaları güçlendirmektedir.
    *   **Potansiyel Birleşmeler:** SpaceX veya xAI ile olası bir birleşme, Tesla'nın teknolojik ekosistemini genişletebilir ve yeni sinerjiler yaratabilir, ancak bu tür birleşmelerin karmaşıklığı ve düzenleyici onay süreçleri de göz önünde bulundurulmalıdır.

**Genel Duygu Skoru:** Karışık ila Negatif. Şirket, inovasyon ve büyüme potansiyeli sunan stratejik hamleler yaparken, düzenleyici baskılar, yasal sorunlar ve temel otomobil işindeki zayıflıklar önemli risk faktörleri olarak öne çıkmaktadır. Yatırımcıların, şirketin robotaksi ve yapay zeka hedeflerine olan inancı, mevcut olumsuzlukları dengelemeye çalışmaktadır. Ancak, bu hedeflere ulaşmadaki düzenleyici ve teknolojik engeller, belirsizliği artırmaktadır.
    """
    
    # 2. Ajan 1'den (Arkadaşından) gelen GERÇEK JSON ÇIKTISI
    # Bu json formatı LLM tarafından direkt okunabilir.
    test_rag_raporu = """
    {
   "legal_risks":[
      {
         "risk_summary":"Tesla faces potential intellectual property infringement claims from competitors or third parties, which could lead to substantial costs, negative publicity, and operational limitations, regardless of the merit of such claims.",
         "severity":"Medium",
         "risk_score":7,
         "source_quote":"Our competitors or other third parties may hold or obtain patents, copyrights, trademarks or other proprietary rights that could prevent, limit or interfere with our ability to make, use, develop, sell or market our products and services, which could make it more difficult for us to operate our business. From time to time, the holders of such intellectual property rights may assert their rights and urge us to take licenses and/or may bring suits alleging infringement or misappropriation of such rights, which could result in substantial costs, negative publicity and management attention, regardless of merit.",
         "location":"Legal Source 1"
      },
      {
         "risk_summary":"The company is exposed to product liability claims, particularly for vehicles and energy products, which may result in substantial monetary damages, product recalls, or redesign efforts. Tesla generally self-insures against these risks, meaning claims would be paid from company funds.",
         "severity":"High",
         "risk_score":8,
         "source_quote":"Any product liability claim may subject us to lawsuits and substantial monetary damages, product recalls or redesign efforts, and even a meritless claim may require us to defend it, all of which may generate negative publicity and be expensive and time-consuming. In most jurisdictions, we generally self-insure against the risk of product liability claims for vehicle exposure, meaning that any product liability claims will likely have to be paid from company funds and not by insurance.",
         "location":"Legal Source 2"
      },
      {
         "risk_summary":"Effective protection for Tesla's brands, technologies, and proprietary information may be limited or unavailable in certain countries, increasing the risk of misappropriation or infringement of intellectual property and potentially affecting its competitive position.",
         "severity":"Medium",
         "risk_score":6,
         "source_quote":"In addition, the effective protection for our brands, technologies, and proprietary information may be limited or unavailable in certain countries, making it difficult to protect our intellectual property from misappropriation or infringement. Although we make reasonable efforts to maintain the confidentiality of our proprietary information, we cannot guarantee that these actions will deter or prevent misappropriation of our intellectual property.",
         "location":"Legal Source 3"
      },
      {
         "risk_summary":"Issues with advanced assistance features, including delays in enablement, legal restrictions, or performance disparities, could lead to delivery delays, product recalls, allegations of product liability, breach of warranty claims, and significant warranty and other expenses.",
         "severity":"High",
         "risk_score":8,
         "source_quote":"assistance features take longer than expected to become enabled, are legally restricted or become subject to onerous regulation, our ability to develop, market and sell our products and services may be harmed, and we may experience delivery delays, product recalls, allegations of product liability, breach of warranty and related consumer protection claims and significant warranty and other expenses.",
         "location":"Legal Source 4"
      }
   ],
   "financial_risks":[
      {
         "risk_summary":"As of December 31, 2025, Tesla had significant outstanding indebtedness of $8.18 billion (with $1.58 billion current) and total minimum lease payments of $7.96 billion (with $1.32 billion due in the succeeding 12 months).",
         "severity":"Medium",
         "risk_score":6,
         "source_quote":"As of December 31, 2025, we and our subsidiaries had outstanding $8.18 billion in aggregate principal amount of indebtedness, of which $1.58 billion is current. As of December 31, 2025, our total minimum lease payments was $7.96 billion, of which $1.32 billion is due in the succeeding 12 months.",
         "location":"Financial Source 1"
      },
      {
         "risk_summary":"Tesla operates in a cyclical industry sensitive to shifting consumer trends, regulatory uncertainty, inflationary pressures, rising energy prices, and interest rate fluctuations, which can impact vehicle affordability and sales volatility.",
         "severity":"Medium",
         "risk_score":7,
         "source_quote":"However, we operate in a cyclical industry that is sensitive to shifting consumer trends, political and regulatory uncertainty, including with respect to trade and the environment, all of which can be compounded by inflationary pressures, rising energy prices, interest rate fluctuations and the liquidity of enterprise customers. For example, as inflationary pressures increased across the markets in which we operate, central banks in developed countries raised interest rates rapidly and substantially, which impacted the affordability of vehicle lease and finance arrangements.",
         "location":"Financial Source 2"
      },
      {
         "risk_summary":"While generally generating strong operating cash flow, periods of heightened capital expenditures for capital-intensive projects, rising material prices, and increased supply chain/labor expenses may necessitate additional funding beyond operating cash flow.",
         "severity":"Low",
         "risk_score":5,
         "source_quote":"At the same time, periods of heightened levels of capital expenditures due to capital-intensive projects and other potential variables such as rising material prices and increases in supply chain and labor expenses resulting from changes in global trade conditions and labor availability, will necessitate additional funding beyond our operating cash flow.",
         "location":"Financial Source 4"
      }
   ],
   "m_and_a_summary":"Tesla (TSLA) presents a risk profile characterized by significant legal exposures, particularly concerning intellectual property protection, potential third-party infringement claims, and substantial product liability risks, exacerbated by its self-insurance policy and the complexities of its advanced assistance features. These legal challenges could lead to considerable financial outlays, reputational damage, and operational disruptions. Financially, while the company demonstrates robust liquidity with $16.51 billion in cash and cash equivalents and $27.55 billion in short-term investments as of December 31, 2025, it carries notable debt and lease obligations totaling $8.18 billion and $7.96 billion respectively. Furthermore, its financial health is susceptible to external macroeconomic factors such as industry cyclicality, inflation, and interest rate fluctuations, which can impact sales and profitability. Although current operations generally generate strong cash flow, future capital-intensive projects may require additional funding, posing a potential strain on liquidity. Overall, TSLA exhibits high operational and product-related legal risks, balanced by a strong current financial position, but remains vulnerable to market volatility and future capital demands."
}
    """
    
    # 3. İKİSİNİ AJAN 3'E YEDİR (SENTEZLE)
    print("\nAjan 3 Sentezliyor...")
    nihai_json = run_agent3(test_rag_raporu, test_haber_raporu)
    
    # 4. SONUCU EKRANA BAS
    print("\n--- NİHAİ JSON ÇIKTISI ---")
    print(json.dumps(nihai_json, indent=4, ensure_ascii=False))