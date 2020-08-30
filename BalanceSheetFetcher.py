import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd


def get_balance_sheet(ticker):
    url_tmpl = 'https://finance.naver.com/item/main.nhn?code=%s'
    url = url_tmpl % (ticker)
    item_info = requests.get(url).text
    soup = BeautifulSoup(item_info, 'html.parser')

    crawled = soup.select('div.section.cop_analysis div.sub_section')

    if len(crawled) < 1:
        return
    else:
        finance_info = soup.select('div.section.cop_analysis div.sub_section')[0]
    th_data = [item.get_text().strip() for item in finance_info.select('thead th')]
    annual_date = th_data[3:7]
    quarter_date = th_data[7:13]
    finance_index = [item.get_text().strip() for item in finance_info.select('th.h_th2')][3:]
    finance_data = [item.get_text().strip() for item in finance_info.select('td')]
    finance_data = np.array(finance_data)
    finance_data.resize(len(finance_index), 10)
    finance_date = annual_date + quarter_date
    financeDF = pd.DataFrame(data=finance_data[0:, 0:], index=finance_index, columns=finance_date)

    return financeDF


def getPERandPBR(df):
    return df.loc[['PER(배)', 'PBR(배)'], ["2020.12(E)"]]


def getPERandPBRsForAllKStocks():
    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
    ticker_list = code_df['종목코드']

    print(ticker_list)

    i = 0
    dic = {}
    for ticker in ticker_list:
        if i == 10:
            break
        balance_sheet = get_balance_sheet(ticker)
        if balance_sheet is None:
            continue
        value = getPERandPBR(balance_sheet)
        dic[ticker] = value
        print(ticker, "  : ", value)
        i += 1


if __name__ == '__main__':
    # getPERandPBRsForAllKStocks()
    balance_sheet = get_balance_sheet(199800)