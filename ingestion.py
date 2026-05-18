import os
import re
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader

def download_sec_filings(ticker="AAPL", amount=1):
    """SEC sisteminden belirtilen şirkete ait en güncel 10-K belgesini indirir."""
    dl = Downloader("CavitYilmazCorp", "cavityilmaz@example.com")
    print(f"\n[{ticker}] için son {amount} adet 10-K raporu indiriliyor...")
    dl.get("10-K", ticker, after="2020-01-01", limit=amount)
    print(f"[{ticker}] indirme işlemi tamamlandı.")

def find_full_submission_path(ticker):
    """İndirilen 'full-submission.txt' dosyasının yolunu otomatik bulur."""
    base_path = os.path.join("sec-edgar-filings", ticker, "10-K")
    if not os.path.exists(base_path):
        return None
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file == "full-submission.txt":
                return os.path.join(root, file)
    return None

def html_to_markdown_table(table_tag):
    """HTML tablolarını temiz bir Markdown tablosuna dönüştürür."""
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
    """SEC dökümanını okur ve Item 1A, 3 ve 7 bölümlerini ayrıştırır."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    
    for table in soup.find_all('table'):
        md_text = html_to_markdown_table(table)
        table.replace_with(md_text)
        
    full_text = soup.get_text(separator="\n")
    
    full_text = full_text.replace('\xa0', ' ')
    full_text = full_text.replace('\u2019', "'")
    full_text = full_text.replace('\u201c', '"').replace('\u201d', '"')
    
    sections = {"hukuk": [], "finans": []}
    
    item_1a_3_pattern = re.compile(r'^\s*ITEM\s+(1A|3)\b', re.IGNORECASE)
    item_7_pattern = re.compile(r'^\s*ITEM\s+7\b', re.IGNORECASE)
    item_end_pattern = re.compile(r'^\s*ITEM\s+(1B|2|4|5|6|8|9)\b', re.IGNORECASE)
    
    current_category = None
    
    for line in full_text.split("\n"):
        clean_line = line.strip()
        if not clean_line:
            continue
            
        if item_1a_3_pattern.match(clean_line):
            current_category = "hukuk"
        elif item_7_pattern.match(clean_line):
            current_category = "finans"
        elif item_end_pattern.match(clean_line):
            current_category = None
            
        if current_category:
            sections[current_category].append(line)
            
    return {
        "hukuk_metni": "\n".join(sections["hukuk"]),
        "finans_metni": "\n".join(sections["finans"])
    }

# === YENİ EKLEDİĞİMİZ ORKESTRASYON FONKSİYONU ===
def get_company_data(ticker):
    """
    Dışarıdan çağrılabilen ana fonksiyon.
    Verilen borsa kodu yerelde yoksa indirir, varsa doğrudan ayrıştırıp veriyi sözlük olarak döner.
    """
    ticker = ticker.upper().strip()
    sample_path = find_full_submission_path(ticker)
    
    if not sample_path:
        download_sec_filings(ticker, amount=1)
        sample_path = find_full_submission_path(ticker)
    
    if sample_path and os.path.exists(sample_path):
        print(f"[{ticker}] Dökümanı başarıyla yüklendi, metin ayrıştırma başlıyor...")
        return parse_and_categorize_sec(sample_path)
    
    print(f"[Hata] {ticker} için döküman indirilemedi veya bulunamadı.")
    return None

# Test etmek için yine eski mantığı koruyoruz
if __name__ == "__main__":
    TARGET_TICKER = "AAPL"
    data = get_company_data(TARGET_TICKER)
    if data:
        print(f"\nBulunan Hukuk Karakter Sayısı : {len(data['hukuk_metni'])}")
        print(f"Bulunan Finans Karakter Sayısı: {len(data['finans_metni'])}")