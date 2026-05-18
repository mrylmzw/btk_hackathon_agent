import requests
import json

def get_all_sec_tickers(save_to_file=False):
    """
    SEC'in resmi sunucularından tüm aktif ticker ve şirket isimlerini çeker.
    """
    # SEC, veri çekerken kendinizi tanıtmanızı (User-Agent) zorunlu tutar.
    headers = {
        'User-Agent': 'CavitYilmazCorp (cavityilmaz@example.com)'
    }
    url = "https://www.sec.gov/files/company_tickers.json"

    try:
        print("🌐 SEC sunucularına bağlanılıyor...")
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Hata varsa fırlat
        
        data = response.json()
        
        # SEC verisi şu formatta gelir: {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ...}
        # Biz bunu daha kullanışlı bir sözlüğe çevirelim: {"AAPL": "Apple Inc."}
        company_map = {item['ticker']: item['title'] for item in data.values()}
        
        if save_to_file:
            with open("all_sec_companies.json", "w", encoding="utf-8") as f:
                json.dump(company_map, f, indent=4, ensure_ascii=False)
            print(f"💾 Toplam {len(company_map)} şirket 'all_sec_companies.json' dosyasına kaydedildi.")
        
        return company_map

    except Exception as e:
        print(f"❌ Liste çekilirken bir hata oluştu: {e}")
        return None

if __name__ == "__main__":
    all_companies = get_all_sec_tickers(save_to_file=True)
    
    if all_companies:
        print(f"\n✅ Başarıyla {len(all_companies)} şirket bulundu.")
        
        # Kontrol için ilk 15 tanesini listeleyelim
        print("\n--- İLK 15 ŞİRKET ÖRNEĞİ ---")
        for i, (ticker, name) in enumerate(list(all_companies.items())[:15]):
            print(f"{i+1}. [{ticker}] {name}")