library(rvest)
library(dplyr)
library(httr)
library(jsonlite)
library(RSelenium)
library(reticulate)
library(jsonlite)
library(stringr)
odea_data <- read_html("https://www.odeabank.com.tr/kampanyalar/odeada-tl-mevduatiniza-5000ye-varan-faiz-orani-firsati-23779")
odea_data %>% html_nodes(".text-center") %>% html_text() %>% .[c(4,6,8,10)]
odea_32_91_max <- odea_data %>% html_nodes(".text-center") %>% html_text() %>% .[c(4,6,8)] %>% 
  gsub(",", ".", .) %>%    
  gsub("%", "", .) %>%     
  as.numeric() %>% max() 
odea_92_max <- odea_data %>% html_nodes(".text-center") %>% html_text() %>% .[10] %>% 
  gsub(",", ".", .) %>%    
  gsub("%", "", .) %>%     
  as.numeric()



odea_32_91_max #######
odea_92_max #########
##################

on_dijital_data <- read_html("https://on.com.tr/hesaplar/e-mevduat-hesabi")
py_config()

py_run_string("
import requests
import json

url = 'https://on.com.tr/Core/GetEmevduatRates?businessLine=X&subProductCode=VDLMINT'

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers)

if response.status_code == 200:
    with open('faiz.json', 'w') as f:
        json.dump(response.json(), f, indent=2)
")

veri <- fromJSON("faiz.json")
try_row <- veri[veri$currencyCode == "TRY", ]
maturities_burgan <- try_row$maturityRates[[1]]
gunlukrate_32_91 <- maturities_burgan$rates %>% .[4] 
burgan_32_91_max <- gunlukrate_32_91[[1]]$rate %>% max
gunlukrate_92 <- maturities_burgan$rates %>% .[5] 
burgan_92_max <- gunlukrate_92[[1]]$rate %>% max


burgan_92_max   #####
burgan_32_91_max #####

##############

fiba_data <- read_html("https://www.fibabanka.com.tr/faiz-ucret-ve-komisyonlar/bireysel-faiz-oranlari/mevduat-faiz-oranlari") %>% html_table() %>% .[[2]]
fiba_32_91_tablo <- fiba_data[4,]
fiba_92_tablo <- fiba_data[5,]
numbers_chr_32 <- as.character(fiba_32_91_tablo[ , -1])  
numbers_num_32 <- as.numeric(gsub(",", ".", numbers_chr_32))
numbers_chr_92 <- as.character(fiba_92_tablo[ , -1])  
numbers_num_92 <- as.numeric(gsub(",", ".", numbers_chr_92))
fiba_32_91_max <- numbers_num_32 %>% max()
fiba_92_max <- numbers_num_92 %>% max()


fiba_32_91_max ###### 
fiba_92_max  #########

###############

alternatif_data <- read_html("https://www.alternatifbank.com.tr/bilgi-merkezi/faiz-oranlari#mevduat") %>% html_table() %>% .[[21]]
alternatif_32_91_max <- alternatif_data[6:9, ] %>%
  select(where(is.numeric)) %>%
  unlist() %>%
  max()
alternatif_92_max <- alternatif_data[10, ] %>%
  select(where(is.numeric)) %>%
  unlist() %>%
  max()
alternatif_92_max #####
alternatif_32_91_max ####

############

qnb_data <- read_html("https://www.qnb.com.tr/e-vadeli-mevduat-urunleri") %>% html_nodes("#sbt1") %>% html_text()
oran_str_qnb <- str_extract(qnb_data, "%\\d+[,\\.]?\\d*")
oran_num_qnb <- as.numeric(gsub(",", ".", str_remove(oran_str_qnb, "%")))

qnb_32_91_max <- oran_num_qnb 
qnb_92_max <- oran_num_qnb 
qnb_32_91_max. ######
qnb_92_max #######

#########

akbank_data <- read_html("https://www.akbank.com/kampanyalar/vadeli-mevduat-tanisma-kampanyasi") 



py_run_string("
import requests
import json

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

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    with open('akbank_faiz.json', 'w') as f:
        json.dump(result, f, indent=2)
")
rates_raw <- veri_akbank$d$Data$ServiceData$GrossRates
akbank_32_91_max <- rates_raw[3:5, ] %>%
  unlist() %>%
  .[4:18] %>%
  unname() %>%
  str_replace(",", ".") %>%
  as.numeric() %>% max
akbank_92_max <- rates_raw[6,] %>% unlist %>% .[2:6] %>% unname %>% str_replace(",", ".") %>%
  as.numeric() %>% max

akbank_32_91_max. ##########
akbank_92_max ############

###################

denizbank_data <- read_html("https://www.denizbank.com/kampanya/mobildeniz-firsatlari/tl-mevduatiniza-hos-geldin-faizi-40738") %>% html_table() %>% .[2]
denizbank_data <- denizbank_data[[1]]
deniz_faiz <- denizbank_data$`Faiz Oranı` %>%
  str_remove("%") %>%
  str_replace(",", ".") %>%
  as.numeric()
denizbank_31_92_max <- deniz_faiz[1]
denizbank_92_max <- deniz_faiz[2]

denizbank_31_92_max ########
denizbank_92_max #########

###############
isbankasi_data <- read_html("https://www.isbank.com.tr/vadeli-tl")
library(httr)

url_isbank <- "https://www.isbank.com.tr/_vti_bin/DV.Isbank/PriceAndRate/PriceAndRateService.svc/GetTermRates?MethodType=TL&Lang=tr&ProductType=UzunVadeli&ChannelType=ISCEP"

response_is <- GET(
  url_isbank,
  add_headers(
    `User-Agent` = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    `Referer` = "https://www.isbank.com.tr/vadeli-tl",
    `Accept` = "application/json"
  )
)
json_raw_is <- content(response_is, as = "text", encoding = "UTF-8")
veri_isbankasi <- fromJSON(json_raw_is)
faiz_max_is <- veri_isbankasi$Data[1] %>%
  str_split("#") %>%
  unlist() %>%
  .[3] %>%
  as.numeric()
isbankasi_32_91_max <- faiz_max_is
isbankasi_92_max <- faiz_max_is

isbankasi_32_91_max #######
isbankasi_92_max #########


##########
vakifbank_data <- read_html("https://www.vakifbank.com.tr/tr/bireysel/hesaplar/vadeli-hesaplar/tanisma-faizi-kampanyasi-hesabi") %>% html_table %>% .[[2]]
vakifbank_32_91_max <- vakifbank_data[1:2, 3][[1]] %>%
  str_remove("%") %>%       
  str_replace(",", ".") %>% 
  as.numeric() %>% max          
vakifbank_92_max <- vakifbank_data[3,3][[1]] %>%
  str_remove("%") %>%       
  str_replace(",", ".") %>% 
  as.numeric() %>% max          

vakifbank_32_91_max #####
vakifbank_92_max  ######

################

garanti_data <- read_html("https://www.garantibbva.com.tr/mevduat/hos-geldin-faizi") %>% html_table() %>% .[[1]]

garanti_32_91_max <- garanti_data[2:5, ] %>%
  mutate(across(-1, ~ str_replace(., ",", ".") %>% as.numeric())) %>%
  select(-1) %>%
  unlist() %>%
  max(na.rm = TRUE)

garanti_92_max <- garanti_data[6, ] %>%
  mutate(across(-1, ~ str_replace(., ",", ".") %>% as.numeric())) %>%
  select(-1) %>%
  unlist() %>%
  max(na.rm = TRUE)

garanti_32_91_max   #######
garanti_92_max   #####

##############

odea_gunluk_faiz <- read_html("https://www.odeabank.com.tr/bireysel/mevduat/oksijen-hesap") %>% html_nodes(".interest-rates__item-rate") %>% html_text() %>%
  str_replace_all("%", "") %>%
  str_replace(",", ".") %>%
  as.numeric() %>% max()
odea_gunluk_faiz#####


 ########
hsbc_gunluk_faiz <- read_html("https://www.hsbc.com.tr/gunluk-bankacilik/mevduat-urunleri/modern-hesap") %>% html_nodes("p") %>% .[2] %>% html_text
hsbc_gunluk_faiz <- hsbc_gunluk_faiz %>%
  str_extract("%\\d{1,2},\\d{2}") %>%
  str_remove("%") %>%
  str_replace(",", ".") %>%
  as.numeric()
hsbc_gunluk_faiz ######

###############

anadolubank_data <- read_html("https://www.anadolubank.com.tr/sizin-icin/birikim-ve-mevduat/renkli-hesap") %>% html_nodes("p , .mb-0") %>% html_text() %>% .[5]

anadolubank_gunluk_faiz <- str_extract(anadolubank_data, "%\\d{1,2}") %>%  
  str_remove("%") %>%                                             
  as.numeric()
anadolubank_gunluk_faiz #########

##################
fiba_data_2 <- read_html("https://www.fibabanka.com.tr/faiz-ucret-ve-komisyonlar/bireysel-faiz-oranlari/mevduat-faiz-oranlari") %>% html_table() %>% .[[1]]
fiba_data_2[,6]
fiba_gunluk_faiz <- fiba_data_2[1:8, 6][[1]] %>%    
  str_remove("%") %>%                           
  str_replace(",", ".") %>%                        
  as.numeric() %>%                                 
  max(na.rm = TRUE)   
fiba_gunluk_faiz     #######

#########
alternatif_data_2 <- read_html("https://www.alternatifbank.com.tr/bireysel/mevduat/vadeli-mevduat/vov-hesap#faizorani") %>% html_nodes(".rate") %>% .[1] %>% html_text()

alternatif_gunluk_faiz <- alternatif_data_2 %>%
  str_extract("\\d{2,3}(\\.\\d+)?") %>% 
  as.numeric()

alternatif_gunluk_faiz #######

####################

qnb_data_2 <- read_html("https://www.qnb.com.tr/kazandiran-gunluk-hesap") %>% html_table() %>% .[[2]] 

qnb_gunluk_faiz <- qnb_data_2[2:3,5] %>%
  unlist() %>%
  unname() %>%
  str_remove("%") %>%
  as.numeric() %>% max()

qnb_gunluk_faiz ##########

###############

burgan_data_2 <- read_html("https://on.com.tr/hesaplar/on-plus") %>% html_nodes(".with-seperator") %>% html_text()

burgan_gunluk_faiz <- burgan_data_2[1] %>%
  str_extract("\\d{2,3}(\\.\\d+)?") %>% 
  as.numeric()

burgan_gunluk_faiz #######

################


akbank_data_2 <- read_html("https://www.akbank.com/mevduat-yatirim/mevduat/hesaplar/serbest-plus-hesap") %>% html_node("h5") %>% html_text

akbank_gunluk_faiz <- akbank_data_2 %>%
  str_extract("%\\d{1,3}(\\.\\d+)?") %>%  
  str_remove("%") %>%
  as.numeric()
akbank_gunluk_faiz ########

#############

url50 <- "https://www.isbank.com.tr/_vti_bin/DV.Isbank/PriceAndRate/PriceAndRateService.svc/GetDailyDepositRate?Lang=tr&ChannelType=ISCEP&CurrencyCode=TRY"

response <- GET(url50, add_headers(`User-Agent` = "Mozilla/5.0"))

if (status_code(response) == 200) {
  data <- content(response, as = "text", encoding = "UTF-8")
  isbank_data_2 <- fromJSON(data)
  isbank_data_2
} 
isbankasi_gunluk_faiz <- isbank_data_2$Data["RateValue"] %>% unlist %>% unname %>% as.numeric %>% max 

isbankasi_gunluk_faiz ######


#############
vakifbank_data_2 <- read_html("https://www.vakifbank.com.tr/tr/bireysel/hesaplar/vadeli-hesaplar/ari-hesabi") %>% html_nodes("h2") %>% .[1] %>% html_text
vakifbank_gunluk_faiz <- vakifbank_data_2 %>%
  str_extract("%\\d{1,3},\\d{2}") %>% 
  str_remove("%") %>%               
  str_replace(",", ".") %>%           
  as.numeric()

vakifbank_gunluk_faiz ######

##############

ing_data <- read_html("https://www.ing.com.tr/tr/sizin-icin/mevduat/ing-turuncu-hesap") %>% html_nodes(".grey-text , strong") %>% .[2] %>% html_text()

ing_gunluk_faiz <- ing_data %>%
  str_extract("TL.*?%\\d{1,3}(,\\d{1,2})?") %>% 
  str_extract("%\\d{1,3}(,\\d{1,2})?") %>%       
  str_remove("%") %>%                          
  str_replace(",", ".") %>%                     
  as.numeric()

ing_gunluk_faiz #####

#########

turkiyefinans_data <- read_html("https://www.turkiyefinans.com.tr/tr-tr/bireysel/sayfalar/gunluk-hesap.aspx") %>% html_table %>% .[[1]]
turkiyefinans_gunluk_faiz <- turkiyefinans_data[1:13, 5] %>%
  unlist() %>%
  unname() %>%
  str_remove_all("[^0-9,]") %>%  
  str_replace(",", ".") %>%
  as.numeric() %>% max

turkiyefinans_gunluk_faiz #########

#############



library(tibble)

faiz_tablosu <- tibble::tibble(
  Banka = c(
    "Odeabank", "Fibabank", "AlternatifBank", "QNB", "Burganbank", "Akbank", "Denizbank",
    "ZiraatBankasi", "İşbankasi", "Vakifbank", "GarantiBbva", "ING", "HSBC", "TurkiyeFinans", "AnadoluBank"
  ),
  `32-91 günlük max oran` = c(
    odea_32_91_max,         # Odeabank
    fiba_32_91_max,       # Fibabank
    alternatif_32_91_max,       # AlternatifBank
    qnb_32_91_max,       # QNB
    burgan_32_91_max,       # Burganbank
    akbank_32_91_max,       # Akbank
    denizbank_31_92_max,       # Denizbank
    40,         # ZiraatBankasi (örnek: yok)
    isbankasi_32_91_max,       # İşbankası
    vakifbank_32_91_max,       # Vakıfbank
    garanti_32_91_max,       # Garanti BBVA
    NA,       # ING
    NA,         # HSBC (günlük var sadece)
    NA,       # Türkiye Finans
    NA          # AnadoluBank (sadece günlük var)
  ),
  `92 günlük max oran` = c(
    odea_92_max,         # Odeabank
    fiba_92_max,         # Fibabank
    alternatif_92_max,         # AlternatifBank
    qnb_92_max,         # QNB
    burgan_92_max,         # Burganbank
    akbank_92_max,         # Akbank
    denizbank_92_max,         # Denizbank
    40,         # ZiraatBankasi
    isbankasi_92_max,         # İşbankası
    vakifbank_92_max,         # Vakıfbank
    garanti_92_max,         # Garanti BBVA
    NA,         # ING
    NA,         # HSBC
    NA,         # Türkiye Finans
    NA          # AnadoluBank
  ),
  `günlük faiz` = c(
    odea_gunluk_faiz,         # Odeabank
    fiba_gunluk_faiz,         # Fibabank
    alternatif_gunluk_faiz,         # AlternatifBank
    qnb_gunluk_faiz,         # QNB
    burgan_gunluk_faiz,         # Burganbank
    akbank_gunluk_faiz,         # Akbank
    NA,         # Denizbank
    NA,         # ZiraatBankasi
    isbankasi_gunluk_faiz,         # İşbankası (GetDailyDepositRate)
    vakifbank_gunluk_faiz,         # Vakıfbank
    NA,         # Garanti BBVA
    ing_gunluk_faiz,         # ING
    hsbc_gunluk_faiz,         # HSBC
    turkiyefinans_gunluk_faiz,         # Türkiye Finans
    anadolubank_gunluk_faiz         # AnadoluBank
  )
)
library(DT)
datatable(faiz_tablosu, filter = "top")




























