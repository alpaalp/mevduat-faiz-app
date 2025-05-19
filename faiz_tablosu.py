import requests
import json
import re
from bs4 import BeautifulSoup
import pandas as pd

def get_faiz_tablosu():
    # Odeabank TL mevduat kampanya sayfası
    odea_url = "https://www.odeabank.com.tr/kampanyalar/odeada-tl-mevduatiniza-5000ye-varan-faiz-orani-firsati-23779"
    resp = requests.get(odea_url)
    soup = BeautifulSoup(resp.content, "lxml")
    texts = [n.get_text(strip=True) for n in soup.select(".text-center")]


    odea_vals_4_6_8 = [texts[i] for i in (3,5,7) if i < len(texts)]
    odea_nums_32_91 = [float(v.replace("%","").replace(",", ".")) for v in odea_vals_4_6_8]
    odea_32_91_max = max(odea_nums_32_91) if odea_nums_32_91 else None

    
    odea_92_max = None
    if len(texts) > 9:
        try:
            odea_92_max = float(texts[9].replace("%","").replace(",", "."))
        except ValueError:
            pass

    # On Dijital (Burganbank verisi via AJAX)
    on_url = "https://on.com.tr/Core/GetEmevduatRates?businessLine=X&subProductCode=VDLMINT"
    on_headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json"
    }
    on_resp = requests.post(on_url, headers=on_headers)
    try:
        on_data = on_resp.json()
    except ValueError:
        on_data = []
    burgan_32_91_max = None
    burgan_92_max = None
    for row in on_data:
        if row.get("currencyCode") == "TRY":
            rates = row.get("maturityRates", [])[0].get("rates", [])
            # 32-91
            if len(rates) > 3:
                seg = rates[3]
                vals = []
                if isinstance(seg, list):
                    for item in seg:
                        if isinstance(item, dict):
                            vals.append(item.get("rate", 0))
                        elif isinstance(item, (int, float)):
                            vals.append(item)
                elif isinstance(seg, dict):
                    vals.append(seg.get("rate", 0))
                elif isinstance(seg, (int, float)):
                    vals.append(seg)
                if vals:
                    burgan_32_91_max = max(vals)
            # 92
            if len(rates) > 4:
                seg2 = rates[4]
                vals2 = []
                if isinstance(seg2, list):
                    for item in seg2:
                        if isinstance(item, dict):
                            vals2.append(item.get("rate", 0))
                        elif isinstance(item, (int, float)):
                            vals2.append(item)
                elif isinstance(seg2, dict):
                    vals2.append(seg2.get("rate", 0))
                elif isinstance(seg2, (int, float)):
                    vals2.append(seg2)
                if vals2:
                    burgan_92_max = max(vals2)
            break

    # Fibabanka faiz oranları tablosu
    fiba_url = "https://www.fibabanka.com.tr/faiz-ucret-ve-komisyonlar/bireysel-faiz-oranlari/mevduat-faiz-oranlari"
    fiba_tables = pd.read_html(fiba_url)
    fiba_data = fiba_tables[1]
    fiba_row32 = fiba_data.iloc[3].iloc[1:].astype(str).str.replace(",", ".").astype(float)
    fiba_32_91_max = fiba_row32.max()
    fiba_row92 = fiba_data.iloc[4].iloc[1:].astype(str).str.replace(",", ".").astype(float)
    fiba_92_max = fiba_row92.max()

    # AlternatifBank faiz oranları
    alt_url = "https://www.alternatifbank.com.tr/bilgi-merkezi/faiz-oranlari#mevduat"
    alt_tables = pd.read_html(alt_url)
    alternatif_data = alt_tables[20]
    alternatif_32_91_max = alternatif_data.iloc[5:9].select_dtypes(include="number").values.flatten().max()
    alternatif_92_max = alternatif_data.iloc[9].select_dtypes(include="number").values.flatten().max()

    # QNB e-vadeli mevduat
    qnb_url = "https://www.qnb.com.tr/e-vadeli-mevduat-urunleri"
    qnb_resp = requests.get(qnb_url)
    qnb_text = BeautifulSoup(qnb_resp.content, "lxml").select_one("#sbt1").get_text()
    oran_nums = [float(s.replace("%","").replace(",", ".")) for s in re.findall(r"%\d+[,\.]?\d*", qnb_text)]
    qnb_32_91_max = max(oran_nums) if oran_nums else None
    qnb_92_max = qnb_32_91_max

    # Akbank faiz AJAX
    ak_url = "https://www.akbank.com/_layouts/15/Akbank/CalcTools/Ajax.aspx/GetMevduatFaiz"
    ak_headers = {"Content-Type": "application/json","User-Agent": "Mozilla/5.0","Accept": "application/json"}
    ak_payload = {"dovizKodu": "888","faizTipi": "97","faizTuru": "0","kanalKodu": "8"}
    ak_resp = requests.post(ak_url, headers=ak_headers, json=ak_payload)
    ak_data = ak_resp.json() if ak_resp.ok else {}
    rates_raw = ak_data.get("d", {}).get("Data", {}).get("ServiceData", {}).get("GrossRates", [])
    flat_rates = [x for row in rates_raw[2:5] for x in row]
    akbank_32_91_max = max([float(str(x).replace(",", ".")) for x in flat_rates[3:18]]) if flat_rates else None
    akbank_92_max = max([float(str(x).replace(",", ".")) for x in rates_raw[5][1:6]]) if len(rates_raw)>5 else None

    # Denizbank
    deniz_url = "https://www.denizbank.com/kampanya/mobildeniz-firsatlari/tl-mevduatiniza-hos-geldin-faizi-40738"
    denizbank_data = pd.read_html(deniz_url)[1]
    deniz_faiz = denizbank_data["Faiz Oranı"].astype(str).str.replace("%","").str.replace(",", ".").astype(float)
    denizbank_32_91_max, denizbank_92_max = deniz_faiz.iloc[0], deniz_faiz.iloc[1]

    # ZiraatBankasi günlük faiz (placeholder, replace with actual)
    ziraat_bank = None

    # İşbankası vadeli TL
    is_url = ("https://www.isbank.com.tr/_vti_bin/DV.Isbank/PriceAndRate/PriceAndRateService.svc/"
              "GetTermRates?MethodType=TL&Lang=tr&ProductType=UzunVadeli&ChannelType=ISCEP")
    is_resp = requests.get(is_url, headers={"User-Agent": "Mozilla/5.0","Referer": "https://www.isbank.com.tr/vadeli-tl","Accept": "application/json"})
    raw_str = json.loads(is_resp.text).get("Data", [None])[0]
    parts = raw_str.split("#") if raw_str else []
    isbankasi_32_91_max = float(parts[2]) if len(parts)>2 else None
    isbankasi_92_max = isbankasi_32_91_max

    # Vakıfbank tanışma faizi
    vakif_tables = pd.read_html("https://www.vakifbank.com.tr/tr/bireysel/hesaplar/vadeli-hesaplar/tanisma-faizi-kampanyasi-hesabi")
    vakif_data = vakif_tables[1]
    vakif_rates = vakif_data.iloc[0:2,2].astype(str).str.replace("%","").str.replace(",", ".").astype(float)
    vakifbank_32_91_max = vakif_rates.max()
    vakifbank_92_max = float(vakif_data.iloc[2,2].replace("%","").replace(",", "."))

    # Garanti BBVA
    garanti_data = pd.read_html("https://www.garantibbva.com.tr/mevduat/hos-geldin-faizi")[0]
    garanti_32_91_max = garanti_data.iloc[1:5,1:].replace(",", ".", regex=True).astype(float).values.max()
    garanti_92_max = garanti_data.iloc[5,1:].replace(",", ".", regex=True).astype(float).values.max()

    # ING
    ing_gunluk_faiz = None

    # HSBC modern hesap
    hs_text = BeautifulSoup(requests.get("https://www.hsbc.com.tr/gunluk-bankacilik/mevduat-urunleri/modern-hesap").content, "lxml").select("p")[1].get_text()
    hsbc_gunluk_faiz = float(re.search(r"%\d{1,2},\d{2}", hs_text).group().replace("%","").replace(",", "."))

    # Anadolubank renkli hesap
    ana_text = BeautifulSoup(requests.get("https://www.anadolubank.com.tr/sizin-icin/birikim-ve-mevduat/renkli-hesap").content, "lxml").select("p, .mb-0")[4].get_text()
    anadolubank_gunluk_faiz = float(re.search(r"%\d{1,2}", ana_text).group().replace("%",""))

    # Fibabanka günlük faiz (ilk tablo)
    fiba_data_2 = pd.read_html(fiba_url)[0]
    fiba_gunluk_faiz = fiba_data_2.iloc[0:8,5].astype(str).str.replace("%","").str.replace(",", ".").astype(float).max()

    # AlternatifBank günlük faiz (vov-hesap)
    alt2_soup = BeautifulSoup(requests.get("https://www.alternatifbank.com.tr/bireysel/mevduat/vadeli-mevduat/vov-hesap#faizorani").content, "lxml")
    alternatif_gunluk_faiz = float(re.search(r"\d{2,3}(?:\.\d+)?", alt2_soup.select_one(".rate").get_text()).group())

    # QNB kazandıran günlük hesap
    qnb_vals = pd.read_html("https://www.qnb.com.tr/kazandiran-gunluk-hesap")[1].iloc[1:3,4].astype(str).str.replace("%","").astype(float).max()

    # Burgan on-plus günlük faiz
    burgan_gunluk_faiz = float(re.search(r"\d{2,3}(?:\.\d+)?", BeautifulSoup(requests.get("https://on.com.tr/hesaplar/on-plus").content, "lxml").select(".with-seperator")[0].get_text()).group())

    # Akbank serbest plus hesap günlük faiz
    ak2_text = BeautifulSoup(requests.get("https://www.akbank.com/mevduat-yatirim/mevduat/hesaplar/serbest-plus-hesap").content,"lxml").find("h5").get_text()
    akbank_gunluk_faiz = float(re.search(r"%\d{1,3}(?:\.\d+)?", ak2_text).group().replace("%",""))

    # İşbankası günlük faiz
    r50 = requests.get("https://www.isbank.com.tr/_vti_bin/DV.Isbank/PriceAndRate/PriceAndRateService.svc/GetDailyDepositRate?Lang=tr&ChannelType=ISCEP&CurrencyCode=TRY", headers={"User-Agent":"Mozilla/5.0"})
    data50 = r50.json().get("Data", {}).get("RateValue", [])
    isbankasi_gunluk_faiz = max(data50) if isinstance(data50, list) else data50

    # Vakıfbank ari hesap günlük faiz
    vakif2_text = BeautifulSoup(requests.get("https://www.vakifbank.com.tr/tr/bireysel/hesaplar/vadeli-hesaplar/ari-hesabi").	content, "lxml").select("h2")[0].get_text()
    vakifbank_gunluk_faiz = float(re.search(r"%\d{1,3},\d{2}", vakif2_text).group().replace("%","").replace(",", "."))

    # ING turuncu hesap günlük faiz
    ing_nodes = BeautifulSoup(requests.get("https://www.ing.com.tr/tr/sizin-icin/mevduat/ing-turuncu-hesap").content,"lxml").select(".grey-text, strong")
    ing_gunluk_faiz = float(re.search(r"%\d{1,3}(?:,\d{1,2})?", ing_nodes[1].get_text()).group().replace("%","").replace(",", ".")) if len(ing_nodes)>1 else None

    # Türkiye Finans günlük hesap tablosu
    turk_df = pd.read_html("https://www.turkiyefinans.com.tr/tr-tr/bireysel/sayfalar/gunluk-hesap.aspx")[0]
    turkiyefinans_gunluk_faiz = turk_df.iloc[0:13,4].astype(str).str.replace(r"[^0-9,]","",regex=True).str.replace(",",".").astype(float).max()

    # Sonuç DataFrame
    faiz_tablosu = pd.DataFrame({
        "Banka": [
            "Odeabank", "Fibabank", "AlternatifBank", "QNB", "Burganbank",
            "Akbank", "Denizbank", "ZiraatBankasi", "İşbankasi", "Vakifbank",
            "GarantiBbva", "ING", "HSBC", "TurkiyeFinans", "AnadoluBank"
        ],
        "32-91 günlük max oran": [
            odea_32_91_max, burgan_32_91_max, fiba_32_91_max,
            alternatif_32_91_max, qnb_32_91_max, akbank_32_91_max,
            denizbank_32_91_max, ziraat_bank, isbankasi_32_91_max,
            vakifbank_32_91_max, garanti_32_91_max, None,
            None, None, None
        ],
        "92 günlük max oran": [
            odea_92_max, burgan_92_max, fiba_92_max,
            alternatif_92_max, qnb_92_max, akbank_92_max,
            denizbank_92_max, ziraat_bank, isbankasi_92_max,
            vakifbank_92_max, garanti_92_max, None,
            None, None, None
        ],
        "günlük faiz": [
            odea_nums_32_91, 
            fiba_gunluk_faiz, alternatif_gunluk_faiz, qnb_vals,
            burgan_gunluk_faiz, akbank_gunluk_faiz, None, None,
            isbankasi_gunluk_faiz, vakifbank_gunluk_faiz,
            None, ing_gunluk_faiz, hsbc_gunluk_faiz,
            turkiyefinans_gunluk_faiz, anadolubank_gunluk_faiz
        ]
    })
    return faiz_tablosu

if __name__ == "__main__":
    df = get_faiz_tablosu()
    print(df)
