import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

def clean_number(text):
    try:
        val = float(text.replace("%", "").replace(",", "."))
        return val if val <= 100 else val / 100
    except:
        return None

def safe_max(values):
    values = [v for v in values if isinstance(v, (int, float)) and v > 0]
    return max(values) if values else None

def scrape_fibabanka():
    try:
        tables = pd.read_html("https://www.fibabanka.com.tr/faiz-ucret-ve-komisyonlar/bireysel-faiz-oranlari/mevduat-faiz-oranlari")
        fiba_32_91 = tables[1].iloc[3, 1:]
        fiba_92 = tables[1].iloc[4, 1:]
        fiba_daily = tables[0].iloc[0:8,5]
        return (
            safe_max([clean_number(str(x)) for x in fiba_32_91]),
            safe_max([clean_number(str(x)) for x in fiba_92]),
            safe_max([clean_number(str(x)) for x in fiba_daily])
        )
    except:
        return None, None, None

def scrape_burganbank():
    try:
        url = 'https://on.com.tr/Core/GetEmevduatRates?businessLine=X&subProductCode=VDLMINT'
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
        data = requests.post(url, headers=headers).json()
        try_data = next((row for row in data if row.get("currencyCode") == "TRY"), {})
        rates = try_data.get("maturityRates", [])[0].get("rates", [])
        r32 = safe_max([x["rate"] for x in rates[3]]) if len(rates) > 3 else None
        r92 = safe_max([x["rate"] for x in rates[4]]) if len(rates) > 4 else None
        daily = None
        try:
            html = requests.get("https://on.com.tr/hesaplar/on-plus").content
            daily_text = BeautifulSoup(html, "lxml").select(".with-seperator")[0].text
            daily = clean_number(re.search(r"\d{2,3}(?:\.\d+)?", daily_text).group())
        except:
            pass
        return r32, r92, daily
    except:
        return None, None, None

def scrape_denizbank():
    try:
        tables = pd.read_html("https://www.denizbank.com/kampanya/mobildeniz-firsatlari/tl-mevduatiniza-hos-geldin-faizi-40738")
        faiz = tables[1]["Faiz Oranı"].astype(str).apply(clean_number)
        return faiz.iloc[0], faiz.iloc[1], None
    except:
        return None, None, None

def scrape_isbankasi():
    try:
        r = requests.get("https://www.isbank.com.tr/_vti_bin/DV.Isbank/PriceAndRate/PriceAndRateService.svc/GetTermRates?MethodType=TL&Lang=tr&ProductType=UzunVadeli&ChannelType=ISCEP",
                         headers={"User-Agent": "Mozilla/5.0"})
        raw_str = r.json().get("Data", [None])[0]
        parts = raw_str.split("#") if raw_str else []
        val = clean_number(parts[2]) if len(parts) > 2 else None

        r2 = requests.get("https://www.isbank.com.tr/_vti_bin/DV.Isbank/PriceAndRate/PriceAndRateService.svc/GetDailyDepositRate?Lang=tr&ChannelType=ISCEP&CurrencyCode=TRY")
        d_val = max([float(x) for x in r2.json().get("Data", {}).get("RateValue", [])])
        return val, val, d_val
    except:
        return None, None, None

def scrape_vakifbank():
    try:
        tables = pd.read_html("https://www.vakifbank.com.tr/tr/bireysel/hesaplar/vadeli-hesaplar/tanisma-faizi-kampanyasi-hesabi")
        tanisma = tables[1]
        r32 = safe_max([clean_number(str(x)) for x in tanisma.iloc[0:2,2]])
        r92 = clean_number(tanisma.iloc[2,2])

        soup = BeautifulSoup(requests.get("https://www.vakifbank.com.tr/tr/bireysel/hesaplar/vadeli-hesaplar/ari-hesabi").content, "lxml")
        rgun = clean_number(re.search(r"%\d{1,3},\d{2}", soup.select("h2")[0].text).group())
        return r32, r92, rgun
    except:
        return None, None, None

def scrape_qnb():
    try:
        soup = BeautifulSoup(requests.get("https://www.qnb.com.tr/e-vadeli-mevduat-urunleri").content, "lxml")
        rate = clean_number(re.findall(r"%\d+[,\.]?\d*", soup.select_one("#sbt1").text)[0])
        daily_tables = pd.read_html("https://www.qnb.com.tr/kazandiran-gunluk-hesap")
        d_val = safe_max([clean_number(str(x)) for x in daily_tables[1].iloc[1:3,4]])
        return rate, rate, d_val
    except:
        return None, None, None

def scrape_garanti():
    try:
        tables = pd.read_html("https://www.garantibbva.com.tr/mevduat/hos-geldin-faizi")
        garanti_data = tables[0]
        garanti_32_91 = garanti_data.iloc[2:5,1:].replace(",",".",regex=True).astype(float).values.max()
        garanti_92 = garanti_data.iloc[5,1:].replace(",",".",regex=True).astype(float).values.max()
        return garanti_32_91, garanti_92, None
    except:
        return None, None, None

def scrape_ing():
    try:
        soup = BeautifulSoup(requests.get("https://www.ing.com.tr/tr/sizin-icin/mevduat/ing-turuncu-hesap").content, "lxml")
        text = soup.select(".grey-text , strong")[1].get_text()
        return None, None, clean_number(re.search(r"%\d{1,3}(?:,\d{1,2})?", text).group())
    except:
        return None, None, None

def scrape_hsbc():
    try:
        soup = BeautifulSoup(requests.get("https://www.hsbc.com.tr/gunluk-bankacilik/mevduat-urunleri/modern-hesap").content, "lxml")
        text = soup.select("p")[1].get_text()
        return None, None, clean_number(re.search(r"%\d{1,2},\d{2}", text).group())
    except:
        return None, None, None

def scrape_anadolubank():
    try:
        soup = BeautifulSoup(requests.get("https://www.anadolubank.com.tr/sizin-icin/birikim-ve-mevduat/renkli-hesap").content, "lxml")
        text = soup.select("p , .mb-0")[4].get_text()
        return None, None, clean_number(re.search(r"%\d{1,2}", text).group())
    except:
        return None, None, None

def scrape_turkiyefinans():
    try:
        tables = pd.read_html("https://www.turkiyefinans.com.tr/tr-tr/bireysel/sayfalar/gunluk-hesap.aspx")
        turk_data = tables[0]
        tf_vals = turk_data.iloc[0:13, 4].astype(str).str.replace(r"[^0-9,]", "", regex=True)
        tf_floats = tf_vals.str.replace(",", ".").astype(float)
        return None, None, tf_floats.max()
    except:
        return None, None, None

def get_faiz_tablosu():
    banks = [
        ("Fibabank", scrape_fibabanka),
        ("Burganbank", scrape_burganbank),
        ("Denizbank", scrape_denizbank),
        ("İşbankası", scrape_isbankasi),
        ("Vakifbank", scrape_vakifbank),
        ("QNB", scrape_qnb),
        ("GarantiBbva", scrape_garanti),
        ("ING", scrape_ing),
        ("HSBC", scrape_hsbc),
        ("AnadoluBank", scrape_anadolubank),
        ("TurkiyeFinans", scrape_turkiyefinans),
        ("ZiraatBankasi", lambda: (40, 40, None))  # dummy
    ]
    records = []
    for name, func in banks:
        r32, r92, daily = func()
        records.append([name, r32, r92, daily])
    return pd.DataFrame(records, columns=["Banka", "32-91 günlük max oran", "92 günlük max oran", "günlük faiz"])

if __name__ == "__main__":
    print(get_faiz_tablosu())
