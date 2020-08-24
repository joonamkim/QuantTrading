from time import sleep
from DailyNewsKeywordCrawler.exceptions import *
from DailyNewsKeywordCrawler.articleparser import *
from multiprocessing.pool import ThreadPool as Pool
import pandas as pd
import time


def __init__(self):
    self.categories = {'정치': 100, '경제': 101, '사회': 102, '생활문화': 103, '세계': 104, 'IT과학': 105, '오피니언': 110,
                       'politics': 100, 'economy': 101, 'society': 102, 'living_culture': 103, 'world': 104,
                       'IT_science': 105, 'opinion': 110}


word_dict = {}


def get_url_data(url, max_tries=10):
    remaining_tries = int(max_tries)
    while remaining_tries > 0:
        try:
            return requests.get(url)
        except requests.exceptions:
            sleep(60)
        remaining_tries = remaining_tries - 1
    raise ResponseTimeout()


def text_analyzer(company, tag, text):
    temp = text.split()
    for word in temp:
        ''.join(ch for ch in word if ch.isalnum())
        if word not in word_dict:
            word_dict[word] = 1
        else:
            word_dict[word] = word_dict[word] + 1
    print(len(word_dict))
    return 0


def split_into_threads():
    url = "http://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=" + "101" + "&date=20200818"
    total_page = ArticleParser.find_news_totalpage(url + "&page=10000")
    pool_size = total_page
    pool = Pool(pool_size)

    for i in range(total_page):
        pool.apply_async(crawl_a_single_page, (url + "&page=" + str(i + 1),))
        print("thread " + str(i) + " started")

    pool.close()
    pool.join()


def crawl_a_single_page(url):

    request = get_url_data(url)
    document = BeautifulSoup(request.content, 'html.parser')
    # html - newsflash_body - type06_headline, type06
    # 각 페이지에 있는 기사들 가져오기
    post_temp = document.select('.newsflash_body .type06_headline li dl')
    post_temp.extend(document.select('.newsflash_body .type06 li dl'))
    # 각 페이지에 있는 기사들의 url 저장
    # regex = re.compile("date=(\d+)")
    # news_date = regex.findall(url)[0]

    post = []
    for line in post_temp:
        post.append(line.a.get('href'))  # 해당되는 page에서 모든 기사들의 URL을 post 리스트에 넣음
    del post_temp

    for content_url in post:  # 기사 URL

        # 크롤링 대기 시간
        sleep(0.01)

        # 기사 HTML 가져옴
        request_content = get_url_data(content_url)
        try:
            document_content = BeautifulSoup(request_content.content, 'html.parser')
        except:
            continue

        try:
            # 기사 제목 가져옴
            tag_headline = document_content.find_all('h3', {'id': 'articleTitle'}, {'class': 'tts_head'})
            text_headline = ''  # 뉴스 기사 제목 초기화
            text_headline = text_headline + ArticleParser.clear_headline(str(tag_headline[0].find_all(text=True)))
            if not text_headline:  # 공백일 경우 기사 제외 처리
                continue

            # 기사 본문 가져옴
            tag_content = document_content.find_all('div', {'id': 'articleBodyContents'})
            text_sentence = ''  # 뉴스 기사 본문 초기화
            text_sentence = text_sentence + ArticleParser.clear_content(str(tag_content[0].find_all(text=True)))
            if not text_sentence:  # 공백일 경우 기사 제외 처리
                continue

            # 기사 언론사 가져옴
            tag_company = document_content.find_all('meta', {'property': 'me2:category1'})
            text_company = ''  # 언론사 초기화
            text_company = text_company + str(tag_company[0].get('content'))
            if not text_company:  # 공백일 경우 기사 제외 처리
                continue

            # print(text_sentence)

            text_analyzer(text_company, text_headline, text_sentence)
            # del text_company, text_sentence, text_headline
            # del tag_company
            # del tag_content, tag_headline
            # del request_content, document_content
            # Press the green button in the gutter to run the script.
        except Exception as ex:  # UnicodeEncodeError ..
            # wcsv.writerow([ex, content_url])
            del request_content, document_content
            pass


def toDataFrame(dict):
    df = pd.DataFrame(dict)
    df.to_csv("ranking.csv")


if __name__ == '__main__':
    start = time.time()
    split_into_threads()
    sorted = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)
    toDataFrame(sorted)
    end = time.time()
    print("Execution time: " + str(end - start))
