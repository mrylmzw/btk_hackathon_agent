import concurrent.futures
import json
import os
from agent_brain import run_agent1
from agent2_deneme import agent2
from agent3_deneme import run_agent3
from companies import SUPPORTED_COMPANIES # Merkezi listeyi çekiyoruz

def execute_full_analysis(ticker):
    ticker = ticker.upper().strip()
    
    # Şirket ismini sözlükten çekiyoruz, yoksa ticker'ın kendisini kullanıyoruz
    company_full_name = SUPPORTED_COMPANIES.get(ticker, ticker)
    print(f"🚀 {company_full_name} ({ticker}) Analiz Süreci Başlatıldı...")

    # PARALEL ÇALIŞTIRMA: A1 ve A2 aynı anda başlar
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Görevleri dağıtıyoruz
        future_a1 = executor.submit(run_agent1, ticker)
        future_a2 = executor.submit(agent2, company_full_name) # Ajan 2'ye şirketin tam adını veriyoruz, böylece haber ararken daha iyi sonuç alırız.

        print("⏳ Ajanlar verileri topluyor (SEC ve Haberler paralel işleniyor)...")
        
        # Sonuçları bekle ve al
        report_a1 = future_a1.result() # RAG JSON çıktısı
        report_a2 = future_a2.result() # Haber metni raporu
    # ARA KAYIT: Ajan 1 raporunu da dosyaya kaydedelim
    with open(f"temp_a1_output.json", "w", encoding="utf-8") as f:
        f.write(report_a1)
    # ARA KAYIT: Ajan 2 raporunu da dosyaya kaydedelim
    with open("temp_a2_output.txt", "w", encoding="utf-8") as f:
        f.write(report_a2)

    print("🧠 Ajan 3: Veriler sentezleniyor ve nihai karar veriliyor...")
    
    # AJAN 3 SENTEZİ: A1'den gelen JSON ve A2'den gelen metni birleştirir
    final_decision = run_agent3(report_a1, report_a2)

    # NİHAİ KAYIT: Streamlit arkadaşın bu dosyayı okuyup ekrana basabilir
    with open("final_ma_decision.json", "w", encoding="utf-8") as f:
        json.dump(final_decision, f, indent=4, ensure_ascii=False)

    return final_decision

if __name__ == "__main__":
    # Test için menü gösterimi
    print("\n--- DESTEKLENEN ŞİRKETLER ---")
    for t, n in SUPPORTED_COMPANIES.items():
        print(f"[{t}] {n}")
        
    ticker_input = input("Analiz edilecek Ticker girin: ").strip().upper()
    execute_full_analysis(ticker_input)