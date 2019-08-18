from bs4 import BeautifulSoup
import requests
from urllib.error import HTTPError
import re
from pprint import pprint
import codecs
from pandas import DataFrame
from datetime import datetime


def get_content(url):
    cookies = requests.session()
    r2 = cookies.get(url)
    bs = BeautifulSoup(r2.text, 'html.parser')
    resList=list()

    topic = bs.find_all('span', class_='article-meta-value')[2].get_text()

    cln = re.compile(r'\n| |\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020|\t|\r')

    for pushes in bs.find_all('div',class_="push"):
            #resDict['pushTag']=pushes.span.get_text()
            id=pushes.find('span',class_='f3 hl push-userid').get_text()
            review=pushes.find('span',class_='f3 push-content').get_text()[2:]
            date=cln.sub('',pushes.find('span',class_='push-ipdatetime').get_text()[0:6])
            time=cln.sub('',pushes.find('span',class_='push-ipdatetime').get_text()[6:12])
            
            resList.append({
                'date':datetime.strptime(('2019/'+date), '%Y/%m/%d'),
                'time':datetime.strptime(time, '%H:%M'),
                'topic':topic,
                'review':review,
                'id':id,
                'url':url
            })

    return resList

def Save2Excel(posts):
    topics = [entry['topic'] for entry in posts]
    links = [entry['url'] for entry in posts]
    dates = [entry['date'] for entry in posts]
    times = [entry['time'] for entry in posts]
    authors = [entry['id'] for entry in posts]
    contents = [entry['review'] for entry in posts]
    df = DataFrame({
        '主題':topics,
        'URL':links,
        '日期': dates,
        '時間':times,
        'id':authors,
        '留言': contents
        })
    
    #output_name = input('請輸入輸出檔名\n')
    output_name = '123'
    final_name = output_name + '.xlsx'
    
    df.to_excel(final_name, sheet_name='sheet1', index=False, columns=['發文周','日期','時間','Series','主題','id','留言',
                                                                        '留言好感度','留言Feature','URL','留言型號','非競品品牌',
                                                                        '非競品型號','文章好感度','文章feature'])

def Read_URL():
    url_list = list()
    file_name = input('請輸入要讀取的txt檔(請加上副檔名)\n')
    file = open(file_name, 'r')
    for line in file:
        url = line.replace('\n', '').split(' ')
        url_list = url_list+url
    file.close()
    return url_list

def main():
    topic_list = list()
    all_reviews_list = list()
    
    topic_list = Read_URL()
    
    for i in range(len(topic_list)):
        temp = get_content(topic_list[i])
        all_reviews_list = all_reviews_list + temp
        
    Save2Excel(all_reviews_list)