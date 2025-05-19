import requests
import json
import re
from bs4 import BeautifulSoup
import pandas as pd

def get_faiz_tablosu():
    odea_32_91_max = odea_92_max = None
    burgan_32_91_max = burgan_92_max = None
    fiba_32_91_max = fiba_92_max = fiba_gunluk_faiz = None
    alternatif_32_91_max = alternatif_92_max = alternatif_gunluk_faiz = None
    qnb_32_91_max = qnb_92_max = qnb_vals = None
    akbank_32_91_max = akbank_92_max = akbank_gunluk_faiz = None
    denizbank_32_91_max = denizbank_92_max = None
    ziraat_bank = None
    isbankasi_32_91_max = isbankasi_92_max = isbankasi_gunluk_faiz = None
    vakifbank_32_91_max = vakifbank_92_max = vakifbank_gunluk_faiz = None
    garanti_32_91_max = garanti_92_max = None
    ing_gunluk_faiz = None
    hsbc_gunluk_faiz = None
    turkiyefinans_gunluk_faiz = None
    anadolubank_gunluk_faiz = None

    try:
        # Odeabank TL mevduat kampanya sayfası
        odea_url = "https://www.odeabank.com.tr/kampanyalar/odeada-tl-mevduatiniza-5000ye-varan-faiz-orani-firsati-23779"
        resp = requests.get(odea_url, timeout=10)
        soup = BeautifulSoup(resp.content, "lxml")
        texts = [n.get_text(strip=True) for n in soup.select(".text-center")]

        odea_vals_4_6_8 = [texts[i] for i in (3,5,7) if i < len(texts)]
        odea_nums_32_91 = [float(v.replace("%","").replace(",", ".")) for v in odea_vals_4_6_8]
        odea_32_91_max = max(odea_nums_32_91) if odea_nums_32_91 else None

        if len(texts) > 9:
            try:
                odea_92_max = float(texts[9].replace("%","").replace(",", "."))
            except (ValueError, IndexError):
                pass
    except Exception as e:
        print(f"Error in Odeabank section: {e}")

    try:
        # On Dijital (Burganbank verisi via AJAX)
        on_url = "https://on.com.tr/Core/GetEmevduatRates?businessLine=X&subProductCode=VDLMINT"
        on_headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json"
        }
        on_resp = requests.post(on_url, headers=on_headers, timeout=10)
        on_data = on_resp.json() if on_resp.ok else []
        
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
    except Exception as e:
        print(f"Error in Burganbank section: {e}")

    try:
        # Fibabanka faiz oranları tablosu
        fiba_url = "https://www.fibabanka.com.tr/faiz-ucret-ve-komisyonlar/bireysel-faiz-oranlari/mevduat-faiz-oranlari"
        fiba_tables = pd.read_html(fiba_url)
        fiba_data = fiba_tables[1]
        fiba_row32 = fiba_data.iloc[3].iloc[1:].astype(str).str.replace(",", ".").astype(float)
        fiba_32_91_max = fiba_row32.max()
        fiba_row92 = fiba_data.iloc[4].iloc[1:].astype(str).str.replace(",", ".").astype(float)
        fiba_92_max = fiba_row92.max()
        
        # Fibabanka günlük faiz (ilk tablo)
        fiba_data_2 = fiba_tables[0]
        fiba_gunluk_faiz = fiba_data_2.iloc[0:8,5].astype(str).str.replace("%","").str.replace(",", ".").astype(float).max()
    except Exception as e:
        print(f"Error in Fibabanka section: {e}")

    try:
        # AlternatifBank faiz oranları
        alt_url = "https://www.alternatifbank.com.tr/bilgi-merkezi/faiz-oranlari#mevduat"
        alt_tables = pd.read_html(alt_url)
        alternatif_data = alt_tables[20] if len(alt_tables) > 20 else None
        
        if alternatif_data is not None:
            try:
                alternatif_32_91_max = alternatif_data.iloc[5:9].select_dtypes(include="number").values.flatten().max()
            except (IndexError, AttributeError):
                pass
            
            try:
                alternatif_92_max = alternatif_data.iloc[9].select_dtypes(include="number").values.flatten().max()
            except (IndexError, AttributeError):
                pass
    except Exception as e:
        print(f"Error in AlternatifBank section: {e}")

    try:
        # QNB e-vadeli mevduat
        qnb_url = "https://www.qnb.com.tr/e-vadeli-mevduat-urunleri"
        qnb_resp = requests.get(qnb_url, timeout=10)
        qnb_text = BeautifulSoup(qnb_resp.content, "lxml").select_one("#sbt1").get_text()
        oran_nums = [float(s.replace("%","").replace(",", ".")) for s in re.findall(r"%\d+[,\.]?\d*", qnb_text)]
        qnb_32_91_max = max(oran_nums) if oran_nums else None
        qnb_92_max = qnb_32_91_max
        
        # QNB kazandıran günlük hesap
        qnb_vals = pd.read_html("https://www.qnb.com.tr/kazandiran-gunluk-hesap")[1].iloc[1:3,4].astype(str).str.replace("%","").astype(float).max()
    except Exception as e:
        print(f"Error in QNB section: {e}")

    # Sonuç DataFrame
    faiz_tablosu = pd.DataFrame({
        "Banka": [
            "Odeabank", "Burganbank", "Fibabank", "AlternatifBank", "QNB", 
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
            max(odea_nums_32_91) if odea_nums_32_91 else None, 
            None, fiba_gunluk_faiz, alternatif_gunluk_faiz, qnb_vals,
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
