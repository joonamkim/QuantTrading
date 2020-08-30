# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from multiprocessing.pool import ThreadPool as Pool
import time
#%%

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
    return df.loc[['PER(배)', 'PBR(배)'], ['2017.12', '2018.12']]


def getPERandPBRsForAllKStocks():
    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
    ticker_list = code_df['종목코드']

    print("Total ticker list size: ", len(ticker_list))

    start = time.time()
    dic = {}

    pool_size = len(ticker_list)
    pool = Pool(pool_size)

    for i in range(len(ticker_list)):
        pool.apply_async(crawl_balance_sheet_for_stock_code, (ticker_list[i], dic,))
        print("thread " + str(i) + " started")

    pool.close()
    pool.join()
    end = time.time()
    print("########################")
    print("DONE")
    print("TOTAL TIME TAKEN = ", end - start)
    print("########################")
    return dic


def crawl_balance_sheet_for_stock_code(ticker, dic):
    balance_sheet = get_balance_sheet(ticker)
    print(balance_sheet)
    if balance_sheet is None:
        return
    if ticker not in dic:
        dic[ticker] = balance_sheet

all_dic = getPERandPBRsForAllKStocks()


#%%

d = all_dic[299900]
#%%
old_year = ['2017.12']
old_dic = {}

for key in all_dic:
    if '2017.12' not in all_dic[key].columns:
        old_dic[key] = all_dic[key]

len(old_dic)
old_dic

pebr_dic = {}
for key in old_dic:
    pebr_dic[key] = old_dic[key].loc[['PER(배)', 'PBR(배)']].iloc[:,1]
#%%
pebr_dic
