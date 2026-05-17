import os
import re
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader

def download_sec_filings(ticker="AAPL", amount=1):
    """
    SEC sisteminden belirtilen şirkete ait en güncel 10-K belgesini indirir.
    """
    dl = Downloader("CavitYilmazCorp", "cavityilmaz@example.com")
    print(f"\n[{ticker}] için son {amount} adet 10-K raporu indiriliyor...")
    dl.get("10-K", ticker, after="2020-01-01", limit=amount)
    print(f"[{ticker}] indirme işlemi tamamlandı.")

def find_full_submission_path(ticker):
    """
    İndirilen 'full-submission.txt' dosyasının yolunu otomatik bulur.
    """
    base_path = os.path.join("sec-edgar-filings", ticker, "10-K")
    if not os.path.exists(base_path):
        return None
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file == "full-submission.txt":
                return os.path.join(root, file)
    return None

def html_to_markdown_table(table_tag):
    """
    HTML tablolarını temiz bir Markdown tablosuna dönüştürür.
    """
    rows = table_tag.find_all('tr')
    md_table = []
    for i, row in enumerate(rows):
        cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
        if not any(cells): 
            continue
        md_table.append("| " + " | ".join(cells) + " |")
        if i == 0:
            md_table.append("| " + " | ".join(["---"] * len(cells)) + " |")
    return "\n".join(md_table)

def parse_and_categorize_sec(html_path):
    """
    SEC dökümanını okur, görünmez karakterleri temizler ve 
    Regex kullanarak esnek bir şekilde Item 1A, 3 ve 7 bölümlerini ayrıştırır.
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    
    # Tabloları Markdown'a çevirerek yapısal veriyi koru
    for table in soup.find_all('table'):
        md_text = html_to_markdown_table(table)
        table.replace_with(md_text)
        
    full_text = soup.get_text(separator="\n")
    
    # --- KRİTİK TEMİZLİK: Görünmez karakterleri normalleştiriyoruz ---
    full_text = full_text.replace('\xa0', ' ')  # HTML görünmez boşluklarını normal boşluk yap
    full_text = full_text.replace('\u2019', "'") # Eğik kesme işaretlerini düzelt
    full_text = full_text.replace('\u201c', '"').replace('\u201d', '"') # Tırnak işaretlerini düzelt
    
    sections = {
        "hukuk": [],
        "finans": []
    }
    
    # Esnek Regex Kalıpları: Araya kaç boşluk veya nokta girerse girsin yakalar
    # Örn: "Item 1A", "ITEM  1A.", "Item    1A - Risk Factors" hepsini yakalar.
    item_1a_3_pattern = re.compile(r'^\s*ITEM\s+(1A|3)\b', re.IGNORECASE)
    item_7_pattern = re.compile(r'^\s*ITEM\s+7\b', re.IGNORECASE)
    # Diğer bölümlere geçildiğinde durmak için bitiş kalıbı
    item_end_pattern = re.compile(r'^\s*ITEM\s+(1B|2|4|5|6|8|9)\b', re.IGNORECASE)
    
    current_category = None
    
    for line in full_text.split("\n"):
        clean_line = line.strip()
        if not clean_line:
            continue
            
        # Satır başındaki başlıkları kontrol et
        if item_1a_3_pattern.match(clean_line):
            current_category = "hukuk"
        elif item_7_pattern.match(clean_line):
            current_category = "finans"
        elif item_end_pattern.match(clean_line):
            current_category = None
            
        # Eğer aktif bir kategorinin içindeysek satırı o havuza ekle
        if current_category:
            sections[current_category].append(line)
            
    return {
        "hukuk_metni": "\n".join(sections["hukuk"]),
        "finans_metni": "\n".join(sections["finans"])
    }

if __name__ == "__main__":
    TARGET_TICKER = "AAPL"  # Hedef şirketin ticker'ı (örneğin: AAPL, MSFT, GOOGL)
    
    # Tekrar indirmemesi için eğer dosya zaten varsa indirme adımını atlayabiliriz
    sample_path = find_full_submission_path(TARGET_TICKER)
    if not sample_path:
        download_sec_filings(TARGET_TICKER, amount=1)
        sample_path = find_full_submission_path(TARGET_TICKER)
    
    if sample_path and os.path.exists(sample_path):
        print(f"\nHedef dosya işleniyor: {sample_path}")
        data = parse_and_categorize_sec(sample_path)
        
        print("\n--- YENİ AYRIŞTIRMA SONUÇLARI ---")
        print(f"Bulunan Hukuk Karakter Sayısı : {len(data['hukuk_metni'])}")
        print(f"Bulunan Finans Karakter Sayısı: {len(data['finans_metni'])}")
        
        if len(data['hukuk_metni']) > 0 or len(data['finans_metni']) > 0:
            print("\nMüthiş! Esnek regex ve temizlik işe yaradı, veriler ayrıştırıldı.")
            print("Artık Faz 2: Vektör Veritabanı (ChromaDB) ve Embedding adımına geçebiliriz.")
        else:
            print("\nHala 0 geliyor, dökümanın iç yapısını örnek bir print ile incelememiz gerekebilir.")