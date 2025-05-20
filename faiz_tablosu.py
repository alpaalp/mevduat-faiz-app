import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

def clean_number(text):
    try:
        return float(text.replace('%','').replace(',','.'))
    except:
        return None

def scrape_odeabank():
    url = "https://www.odeabank.com.tr/kampanyalar/odeada-tl-mevduatiniza-5000ye-varan-faiz-orani-firsati-23779"
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.content, 'html.parser')
    texts = [n.get_text(strip=True) for n in soup.select(".text-center")]
    vals = [clean_number(texts[i]) for i in (3,5,7) if i < len(texts)]
    odea_32_91 = max(vals) if vals else None
    odea_92 = clean_number(texts[9]) if len(texts)>9 else None
    daily_url = "https://www.odeabank.com.tr/bireysel/mevduat/oksijen-hesap"
    daily_soup = BeautifulSoup(requests.get(daily_url, timeout=10).content, 'html.parser')
    daily_vals = [clean_number(r.text) for r in daily_soup.select(".interest-rates__item-rate")]
    odea_daily = max(daily_vals) if daily_vals else None
    return odea_32_91, odea_92, odea_daily

def scrape_burganbank():
    url = 'https://on.com.tr/Core/GetEmevduatRates?businessLine=X&subProductCode=VDLMINT'
    headers = {'User-Agent':'Mozilla/5.0','Accept':'application/json','X-Requested-With':'XMLHttpRequest','Content-Type':'application/json'}
    data = requests.post(url, headers=headers, timeout=10).json()
    b32=b92=None
    for row in data:
        if row.get('currencyCode')=='TRY':
            rates = row.get('maturityRates',[{}])[0].get('rates',[])
            if len(rates)>3:
                seg=rates[3]
                vals=[]
                if isinstance(seg,list):
                    for i in seg:
                        if isinstance(i,dict): vals.append(i.get('rate',0))
                        elif isinstance(i,(int,float)): vals.append(i)
                elif isinstance(seg,(int,float)): vals.append(seg)
                b32=max(vals) if vals else None
            if len(rates)>4:
                seg=rates[4]
                vals=[]
                if isinstance(seg,list):
                    for i in seg:
                        if isinstance(i,dict): vals.append(i.get('rate',0))
                        elif isinstance(i,(int,float)): vals.append(i)
                elif isinstance(seg,(int,float)): vals.append(seg)
                b92=max(vals) if vals else None
            break
    daily_soup = BeautifulSoup(requests.get("https://on.com.tr/hesaplar/on-plus",timeout=10).content,'html.parser')
    txt = daily_soup.select_one(".with-seperator").get_text()
    bdaily=clean_number(re.search(r"\d{2,3}(?:\.\d+)?",txt).group())
    return b32,b92,bdaily

def scrape_fibabanka():
    tbls = pd.read_html("https://www.fibabanka.com.tr/faiz-ucret-ve-komisyonlar/bireysel-faiz-oranlari/mevduat-faiz-oranlari")
    df=tbls[1]
    f32=df.iloc[3,1:].astype(str).str.replace(',','.').astype(float).max()
    f92=df.iloc[4,1:].astype(str).str.replace(',','.').astype(float).max()
    dtab=tbls[0]
    fdaily=dtab.iloc[0:8,5].astype(str).str.replace('%','').str.replace(',','.').astype(float).max()
    return f32,f92,fdaily

def scrape_alternatifbank():
    tbls=pd.read_html("https://www.alternatifbank.com.tr/bilgi-merkezi/faiz-oranlari#mevduat")
    df=tbls[20]
    a32=df.iloc[5:9].select_dtypes(include='number').values.flatten().max()
    a92=df.iloc[9].select_dtypes(include='number').values.flatten().max()
    daily = clean_number(re.search(r"\d{2,3}(?:\.\d+)?", BeautifulSoup(requests.get("https://www.alternatifbank.com.tr/bireysel/mevduat/vadeli-mevduat/vov-hesap#faizorani",timeout=10).content,'html.parser').select_one(".rate").get_text()).group())
    return a32,a92,daily

def scrape_qnb():
    soup=BeautifulSoup(requests.get("https://www.qnb.com.tr/e-vadeli-mevduat-urunleri",timeout=10).content,'html.parser')
    rate=clean_number(re.findall(r"%\d+[,\.]?\d*",soup.select_one("#sbt1").get_text())[0])
    df2=pd.read_html("https://www.qnb.com.tr/kazandiran-gunluk-hesap",encoding='utf-8')[1]
    qdaily=df2.iloc[1:3,4].astype(str).str.replace('%','').astype(float).max()
    return rate,rate,qdaily

def scrape_akbank():
    resp=requests.post('https://www.akbank.com/_layouts/15/Akbank/CalcTools/Ajax.aspx/GetMevduatFaiz',
                       headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0','Accept':'application/json'},
                       json={'dovizKodu':'888','faizTipi':'97','faizTuru':'0','kanalKodu':'8'},timeout=10).json()
    rates=resp.get('d',{}).get('Data',{}).get('ServiceData',{}).get('GrossRates',[])
    flat=[x for row in rates[2:5] for x in row]
    ak32=max([clean_number(str(x)) for x in flat[3:18]]) if flat else None
    ak92=max([clean_number(str(x)) for x in rates[5][1:6]]) if len(rates)>5 else None
    daily=clean_number(re.search(r"%\d{1,3}(?:\.\d+)?",BeautifulSoup(requests.get("https://www.akbank.com/mevduat-yatirim/mevduat/hesaplar/serbest-plus-hesap",timeout=10).content,'html.parser').find('h5').get_text()).group())
    return ak32,ak92,daily

def scrape_denizbank():
    df=pd.read_html("https://www.denizbank.com/kampanya/mobildeniz-firsatlari/tl-mevduatiniza-hos-geldin-faizi-40738")[1]
    rates=df['Faiz Oranı'].astype(str).str.replace('%','').str.replace(',','.').astype(float)
    return rates.iloc[0],rates.iloc[1],None

def scrape_isbankasi():
    data=requests.get("https://www.isbank.com.tr/_vti_bin/DV.Isbank/PriceAndRate/PriceAndRateService.svc/GetTermRates?MethodType=TL&Lang=tr&ProductType=UzunVadeli&ChannelType=ISCEP",
                      headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.isbank.com.tr/vadeli-tl','Accept':'application/json'},timeout=10).json()
    raw=data.get('Data',[None])[0]
    parts=raw.split('#') if raw else []
    val=float(parts[2]) if len(parts)>2 else None
    daily=requests.get("https://www.isbank.com.tr/_vti_bin/DV.Isbank/PriceAndRate/PriceAndRateService.svc/GetDailyDepositRate?Lang=tr&ChannelType=ISCEP&CurrencyCode=TRY",
                       headers={'User-Agent':'Mozilla/5.0'},timeout=10).json().get('Data',{}).get('RateValue',0)
    dval=max(daily) if isinstance(daily,list) else daily
    return val,val,dval

def scrape_vakifbank():
    df=pd.read_html("https://www.vakifbank.com.tr/tr/bireysel/hesaplar/vadeli-hesaplar/tanisma-faizi-kampanyasi-hesabi")[1]
    v32=df.iloc[0:2,2].astype(str).str.replace('%','').str.replace(',','.').astype(float).max()
    v92=clean_number(df.iloc[2,2])
    dv=clean_number(re.search(r"%\d{1,3},\d{2}",BeautifulSoup(requests.get("https://www.vakifbank.com.tr/tr/bireysel/hesaplar/vadeli-hesaplar/ari-hesabi",timeout=10).content,'html.parser').select('h2')[0].get_text()).group())
    return v32,v92,dv

def scrape_garanti():
    df=pd.read_html("https://www.garantibbva.com.tr/mevduat/hos-geldin-faizi")[0]
    g32=df.iloc[2:5,1:].replace(',','.',regex=True).astype(float).values.max()
    g92=df.iloc[5,1:].replace(',','.',regex=True).astype(float).values.max()
    return g32,g92,None

def scrape_hsbc():
    txt=BeautifulSoup(requests.get("https://www.hsbc.com.tr/gunluk-bankacilik/mevduat-urunleri/modern-hesap",timeout=10).content,'html.parser').select('p')[1].get_text()
    return None,None,clean_number(re.search(r"%\d{1,2},\d{2}",txt).group())

def scrape_anadolubank():
    txt=BeautifulSoup(requests.get("https://www.anadolubank.com.tr/sizin-icin/birikim-ve-mevduat/renkli-hesap",timeout=10).content,'html.parser').select("p, .mb-0")[4].get_text()
    return None,None,clean_number(re.search(r"%\d{1,2}",txt).group())

def scrape_ing():
    txt=BeautifulSoup(requests.get("https://www.ing.com.tr/tr/sizin-icin/mevduat/ing-turuncu-hesap",timeout=10).content,'html.parser').select(".grey-text, strong")[1].get_text()
    return None,None,clean_number(re.search(r"%\d{1,3}(?:,\d{1,2})?",txt).group())

def scrape_turkiyefinans():
    df=pd.read_html("https://www.turkiyefinans.com.tr/tr-tr/bireysel/sayfalar/gunluk-hesap.aspx")[0]
    val=df.iloc[0:13,4].astype(str).str.replace(r"[^0-9,]","",regex=True).str.replace(",",".").astype(float).max()
    return None,None,val

def create_faiz_tablosu():
    banks = [
        ("Odeabank", *scrape_odeabank()),
        ("Fibabanka", *scrape_fibabanka()),
        ("AlternatifBank", *scrape_alternatifbank()),
        ("QNB", *scrape_qnb()),
        ("Burganbank", *scrape_burganbank()),
        ("Akbank", *scrape_akbank()),
        ("Denizbank", *scrape_denizbank()),
        ("ZiraatBankasi", None,None,None),
        ("İşbankasi", *scrape_isbankasi()),
        ("Vakifbank", *scrape_vakifbank()),
        ("GarantiBbva", *scrape_garanti()),
        ("ING", *scrape_ing()),
        ("HSBC", *scrape_hsbc()),
        ("TurkiyeFinans", *scrape_turkiyefinans()),
        ("AnadoluBank", *scrape_anadolubank())
    ]
    df=pd.DataFrame(banks, columns=["Banka","32-91 günlük max oran","92 günlük max oran","günlük faiz"])
    return df

if __name__=="__main__":
    df=create_faiz_tablosu()
    print(df)
