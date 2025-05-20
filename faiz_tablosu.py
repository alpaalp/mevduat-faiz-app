import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

def clean_number(text):
    try:
        return float(text.replace("%","").replace(",","."))
    except:
        return None

def scrape_odeabank():
    try:
        url = "https://www.odeabank.com.tr/kampanyalar/odeada-tl-mevduatiniza-5000ye-varan-faiz-orani-firsati-23779"
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, 'html.parser')
        texts = [n.get_text(strip=True) for n in soup.select(".text-center")]
        
        odea_32_91 = [clean_number(texts[i]) for i in (3,5,7) if i < len(texts)]
        odea_32_91_max = max(odea_32_91) if odea_32_91 else None
        
        odea_92_max = clean_number(texts[9]) if len(texts) > 9 else None
        
        daily_url = "https://www.odeabank.com.tr/bireysel/mevduat/oksijen-hesap"
        daily_page = requests.get(daily_url, timeout=10)
        daily_soup = BeautifulSoup(daily_page.content, 'html.parser')
        daily_rates = [clean_number(r.text) for r in daily_soup.select(".interest-rates__item-rate")]
        odea_daily = max(daily_rates) if daily_rates else None
        
        return odea_32_91_max, odea_92_max, odea_daily
    except:
        return None, None, None

def scrape_burganbank():
    try:
        url = 'https://on.com.tr/Core/GetEmevduatRates?businessLine=X&subProductCode=VDLMINT'
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, timeout=10)
        data = response.json()
        
        burgan_32_91_max = burgan_92_max = None
        
        try_row = next((item for item in data if item.get('currencyCode') == 'TRY'), None)
        if try_row and try_row.get('maturityRates'):
            maturities = try_row['maturityRates'][0]
            rates = maturities.get('rates', [])
            
            if len(rates) > 3:
                rate_data = rates[3]
                if isinstance(rate_data, list):
                    burgan_32_91_max = max(float(item.get('rate', 0)) for item in rate_data)
                elif isinstance(rate_data, dict):
                    burgan_32_91_max = float(rate_data.get('rate', 0))
                elif isinstance(rate_data, (int, float, str)):
                    burgan_32_91_max = float(rate_data)
            
            if len(rates) > 4:
                rate_data = rates[4]
                if isinstance(rate_data, list):
                    burgan_92_max = max(float(item.get('rate', 0)) for item in rate_data)
                elif isinstance(rate_data, dict):
                    burgan_92_max = float(rate_data.get('rate', 0))
                elif isinstance(rate_data, (int, float, str)):
                    burgan_92_max = float(rate_data)

        daily_url = "https://on.com.tr/hesaplar/on-plus"
        daily_page = requests.get(daily_url, timeout=10)
        daily_soup = BeautifulSoup(daily_page.content, 'html.parser')
        daily_text = daily_soup.select(".with-seperator")[0].get_text()
        burgan_daily = float(re.search(r"\d{2,3}(?:\.\d+)?", daily_text).group())
        
        return burgan_32_91_max, burgan_92_max, burgan_daily
    except Exception as e:
        print(f"Error in scrape_burganbank: {e}")
        return None, None, None

def scrape_fibabanka():
    try:
        url = "https://www.fibabanka.com.tr/faiz-ucret-ve-komisyonlar/bireysel-faiz-oranlari/mevduat-faiz-oranlari"
        tables = pd.read_html(url)
        
        fiba_data = tables[1]
        fiba_32_91 = fiba_data.iloc[3].iloc[1:].astype(str).str.replace(",",".").astype(float)
        fiba_32_91_max = fiba_32_91.max()
        fiba_92 = fiba_data.iloc[4].iloc[1:].astype(str).str.replace(",",".").astype(float)
        fiba_92_max = fiba_92.max()
        
        fiba_daily_data = tables[0]
        fiba_daily = fiba_daily_data.iloc[0:8,5].astype(str).str.replace("%","").str.replace(",",".").astype(float).max()
        
        return fiba_32_91_max, fiba_92_max, fiba_daily
    except:
        return None, None, None

def scrape_alternatifbank():
    try:
        url = "https://www.alternatifbank.com.tr/bilgi-merkezi/faiz-oranlari#mevduat"
        tables = pd.read_html(url)
        alt_data = tables[20]
        
        alt_32_91_max = alt_data.iloc[5:9].select_dtypes(include="number").values.flatten().max()
        alt_92_max = alt_data.iloc[9].select_dtypes(include="number").values.flatten().max()
        
        daily_url = "https://www.alternatifbank.com.tr/bireysel/mevduat/vadeli-mevduat/vov-hesap#faizorani"
        daily_page = requests.get(daily_url, timeout=10)
        daily_soup = BeautifulSoup(daily_page.content, 'html.parser')
        daily_text = daily_soup.select_one(".rate").get_text()
        alt_daily = float(re.search(r"\d{2,3}(?:\.\d+)?", daily_text).group())
        
        return alt_32_91_max, alt_92_max, alt_daily
    except:
        return None, None, None

def scrape_qnb():
    try:
        url = "https://www.qnb.com.tr/e-vadeli-mevduat-urunleri"
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, 'html.parser')
        text = soup.select_one("#sbt1").get_text()
        rate = clean_number(re.findall(r"%\d+[,\.]?\d*", text)[0])
        qnb_32_91_max = qnb_92_max = rate
        
        daily_url = "https://www.qnb.com.tr/kazandiran-gunluk-hesap"
        daily_tables = pd.read_html(daily_url)
        qnb_daily = daily_tables[1].iloc[0:3,4].astype(str).str.replace("%","").astype(float).max()
        
        return qnb_32_91_max, qnb_92_max, qnb_daily
    except:
        return None, None, None

def scrape_akbank():
    try:
        url = 'https://www.akbank.com/_layouts/15/Akbank/CalcTools/Ajax.aspx/GetMevduatFaiz'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }
        payload = {
            'dovizKodu': '888',
            'faizTipi': '97',
            'faizTuru': '0',
            'kanalKodu': '8'
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        
        rates_raw = data.get("d", {}).get("Data", {}).get("ServiceData", {}).get("GrossRates", [])
        akbank_32_91_max = max([float(str(x).replace(",",".")) for x in rates_raw[3:5]]) if len(rates_raw) > 5 else None
        akbank_92_max = max([float(str(x).replace(",",".")) for x in rates_raw[5][1:6]]) if len(rates_raw) > 5 else None
        
        daily_url = "https://www.akbank.com/mevduat-yatirim/mevduat/hesaplar/serbest-plus-hesap"
        daily_page = requests.get(daily_url, timeout=10)
        daily_soup = BeautifulSoup(daily_page.content, 'html.parser')
        daily_text = daily_soup.find("h5").get_text()
        akbank_daily = clean_number(re.search(r"%\d{1,3}(?:\.\d+)?", daily_text).group())
        
        return akbank_32_91_max, akbank_92_max, akbank_daily
    except:
        return None, None, None

def scrape_denizbank():
    try:
        url = "https://www.denizbank.com/kampanya/mobildeniz-firsatlari/tl-mevduatiniza-hos-geldin-faizi-40738"
        tables = pd.read_html(url)
        deniz_data = tables[1]
        
        deniz_faiz = deniz_data["Faiz Oranı"].astype(str).str.replace("%","").str.replace(",",".").astype(float)
        deniz_32_91 = deniz_faiz.iloc[0]
        deniz_92 = deniz_faiz.iloc[1]
        
        return deniz_32_91, deniz_92, None
    except:
        return None, None, None

def scrape_isbankasi():
    try:
        url = "https://www.isbank.com.tr/_vti_bin/DV.Isbank/PriceAndRate/PriceAndRateService.svc/GetTermRates?MethodType=TL&Lang=tr&ProductType=UzunVadeli&ChannelType=ISCEP"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.isbank.com.tr/vadeli-tl',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        raw_str = data.get("Data", [None])[0]
        parts = raw_str.split("#") if raw_str else []
        isbank_32_91 = float(parts[2]) if len(parts)>2 else None
        
        daily_url = "https://www.isbank.com.tr/_vti_bin/DV.Isbank/PriceAndRate/PriceAndRateService.svc/GetDailyDepositRate?Lang=tr&ChannelType=ISCEP&CurrencyCode=TRY"
        daily_response = requests.get(daily_url, headers={'User-Agent':'Mozilla/5.0'}, timeout=10)
        daily_data = daily_response.json().get("Data", {}).get("RateValue", [])
        isbank_daily = max(daily_data) if isinstance(daily_data, list) else daily_data
        
        return isbank_32_91, isbank_32_91, isbank_daily
    except:
        return None, None, None

def scrape_vakifbank():
    try:
        url = "https://www.vakifbank.com.tr/tr/bireysel/hesaplar/vadeli-hesaplar/tanisma-faizi-kampanyasi-hesabi"
        tables = pd.read_html(url)
        vakif_data = tables[1]
        
        vakif_32_91 = vakif_data.iloc[0:2,2].astype(str).str.replace("%","").str.replace(",",".").astype(float).max()
        vakif_92 = clean_number(vakif_data.iloc[2,2])
        
        daily_url = "https://www.vakifbank.com.tr/tr/bireysel/hesaplar/vadeli-hesaplar/ari-hesabi"
        daily_page = requests.get(daily_url, timeout=10)
        daily_soup = BeautifulSoup(daily_page.content, 'html.parser')
        daily_text = daily_soup.select("h2")[0].get_text()
        vakif_daily = clean_number(re.search(r"%\d{1,3},\d{2}", daily_text).group())
        
        return vakif_32_91, vakif_92, vakif_daily
    except:
        return None, None, None

def scrape_garanti():
    try:
        url = "https://www.garantibbva.com.tr/mevduat/hos-geldin-faizi"
        tables = pd.read_html(url)
        garanti_data = tables[0]
        
        garanti_32_91 = garanti_data.iloc[2:5,1:].replace(",",".",regex=True).astype(float).values.max()
        garanti_92 = garanti_data.iloc[5,1:].replace(",",".",regex=True).astype(float).values.max()
        
        return garanti_32_91, garanti_92, None
    except:
        return None, None, None

def scrape_hsbc():
    try:
        url = "https://www.hsbc.com.tr/gunluk-bankacilik/mevduat-urunleri/modern-hesap"
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, 'html.parser')
        text = soup.select("p")[1].get_text()
        hsbc_daily = clean_number(re.search(r"%\d{1,2},\d{2}", text).group())
        
        return None, None, hsbc_daily
    except:
        return None, None, None

def scrape_anadolubank():
    try:
        url = "https://www.anadolubank.com.tr/sizin-icin/birikim-ve-mevduat/renkli-hesap"
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, 'html.parser')
        text = soup.select("p , .mb-0")[4].get_text()
        anadolu_daily = clean_number(re.search(r"%\d{1,2}", text).group())
        
        return None, None, anadolu_daily
    except:
        return None, None, None

def scrape_ing():
    try:
        url = "https://www.ing.com.tr/tr/sizin-icin/mevduat/ing-turuncu-hesap"
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, 'html.parser')
        text = soup.select(".grey-text , strong")[1].get_text()
        ing_daily = clean_number(re.search(r"%\d{1,3}(?:,\d{1,2})?", text).group())
        
        return None, None, ing_daily
    except:
        return None, None, None

def scrape_turkiyefinans():
    try:
        url = "https://www.turkiyefinans.com.tr/tr-tr/bireysel/sayfalar/gunluk-hesap.aspx"
        tables = pd.read_html(url)
        turk_data = tables[0]
        
        turk_daily = turk_data.iloc[0:13,4].astype(str).str.replace(r"[^0-9,]","",regex=True).str.replace(",",".").astype(float).max()
        
        return None, None, turk_daily
    except:
        return None, None, None

def get_faiz_tablosu():
    odea_32_91, odea_92, odea_daily = scrape_odeabank()
    fiba_32_91, fiba_92, fiba_daily = scrape_fibabanka()
    alt_32_91, alt_92, alt_daily = scrape_alternatifbank()
    qnb_32_91, qnb_92, qnb_daily = scrape_qnb()
    burgan_32_91, burgan_92, burgan_daily = scrape_burganbank()
    akbank_32_91, akbank_92, akbank_daily = scrape_akbank()
    deniz_32_91, deniz_92, _ = scrape_denizbank()
    isbank_32_91, isbank_92, isbank_daily = scrape_isbankasi()
    vakif_32_91, vakif_92, vakif_daily = scrape_vakifbank()
    garanti_32_91, garanti_92, _ = scrape_garanti()
    _, _, hsbc_daily = scrape_hsbc()
    _, _, anadolu_daily = scrape_anadolubank()
    _, _, ing_daily = scrape_ing()
    _, _, turk_daily = scrape_turkiyefinans()
    
    faiz_tablosu = pd.DataFrame({
        "Banka": [
            "Odeabank", "Fibabank", "AlternatifBank", "QNB", "Burganbank",
            "Akbank", "Denizbank", "ZiraatBankasi", "İşbankasi", "Vakifbank",
            "GarantiBbva", "ING", "HSBC", "TurkiyeFinans", "AnadoluBank"
        ],
        "32-91 günlük max oran": [
            odea_32_91, fiba_32_91, alt_32_91, qnb_32_91, burgan_32_91,
            akbank_32_91, deniz_32_91, None, isbank_32_91, vakif_32_91,
            garanti_32_91, None, None, None, None
        ],
        "92 günlük max oran": [
            odea_92, fiba_92, alt_92, qnb_92, burgan_92,
            akbank_92, deniz_92, None, isbank_92, vakif_92,
            garanti_92, None, None, None, None
        ],
        "günlük faiz": [
            odea_daily, fiba_daily, alt_daily, qnb_daily, burgan_daily,
            akbank_daily, None, None, isbank_daily, vakif_daily,
            None, ing_daily, hsbc_daily, turk_daily, anadolu_daily
        ]
    })
    
    return faiz_tablosu

if __name__ == "__main__":
    df = get_faiz_tablosu()
    print(df)
