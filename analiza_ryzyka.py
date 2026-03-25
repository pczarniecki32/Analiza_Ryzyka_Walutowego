import yfinance as yf
import pandas as pd 
import numpy as np

def pobierz_dane_z_rynku(waluta):
    ticker= yf.Ticker(waluta)
    dane= ticker.history(period="2y")
    return dane[['Close']]

def polacz_i_oczysc_dane(dane_usd, dane_eur, dane_chf):
    dane_usd= dane_usd.rename(columns={'Close': 'Kurs_USD'})
    dane_eur= dane_eur.rename(columns={'Close': 'Kurs_EUR'})
    dane_chf= dane_chf.rename(columns={'Close': 'Kurs_CHF'})

    polaczone_usd_eur= pd.merge(dane_usd, dane_eur, left_index=True, right_index=True, how='outer')
    polaczone_wszystkie= pd.merge(polaczone_usd_eur, dane_chf, left_index=True, right_index=True, how='outer')

    polaczone_czyste= polaczone_wszystkie.dropna()
    polaczone_czyste.reset_index(inplace=True)
    polaczone_czyste['Date']= polaczone_czyste['Date'].dt.tz_localize(None)
    return polaczone_czyste

def wylicz_wskazniki_ryzyka(tabela, okno=30):
    waluty= ['USD', 'EUR', 'CHF']
    for i in waluty:
        kurs= f'Kurs_{i}'
        #1. Średnia krocząca
        tabela[f'SMA_{okno}_{i}']= tabela[kurs].rolling(window=okno).mean()
        #2. Zwroty logarytmiczne
        tabela[f'Zwrot_{i}']= np.log(tabela[kurs] / tabela[kurs].shift(1))
        #3. Zmienność (standardowo 252 dni w roku, pomijamy weekendy i święta)
        tabela[f'Zmiennosc_{i}']= tabela[f'Zwrot_{i}'].rolling(window=okno).std()* np.sqrt(252)
        #4. VaR 95%
        tabela[f'VaR_95%_{i}']= tabela[f'Zwrot_{i}'].rolling(window=okno).quantile(0.05)
    
    return tabela

def usun_puste_dni_i_zaokraglij(dane_final):
    dane_final= dane_final.dropna().round(4)
    return dane_final

def zapisz_do_powerbi(tabela):
    tabela.to_csv('dane_walutowe_do_powerbi.csv', index=False)

if __name__== "__main__":
    dane_usd= pobierz_dane_z_rynku('USDPLN=X')
    dane_eur= pobierz_dane_z_rynku('EURPLN=X')
    dane_chf= pobierz_dane_z_rynku('CHFPLN=X')

    dane_gotowe= polacz_i_oczysc_dane(dane_usd, dane_eur, dane_chf)
    dane_final= wylicz_wskazniki_ryzyka(dane_gotowe)
    dane_final= usun_puste_dni_i_zaokraglij(dane_final)

    zapisz_do_powerbi(dane_final)


