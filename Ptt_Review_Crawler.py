from bs4 import BeautifulSoup
import requests
from urllib.error import HTTPError
import re
from pprint import pprint
import codecs
from pandas import DataFrame
import datetime
import sys

def get_content_main(url):
    cookies = requests.session()
    r2 = cookies.get(url)
    bs = BeautifulSoup(r2.text, 'html.parser')
    resList=list()

    topic = bs.find_all('span', class_='article-meta-value')[2].get_text()

    cln = re.compile(r'\n| |\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020|\t|\r')

    Main_post_week = bs.find_all('span', class_='article-meta-value')[3].get_text()[4:10]
    main_week_num = datetime.datetime.strptime('2019'+Main_post_week, '%Y%b %d').date().isocalendar()[1]

    raw_main_time=bs.find_all('span', class_='article-meta-value')[3].get_text()
    main_date = datetime.datetime.strptime((raw_main_time[4:7]+raw_main_time[8:11]+raw_main_time[20:24]), '%b  %d  %Y')
    main_time = datetime.datetime.strptime((raw_main_time[11:16]),'%H:%M')

    main_id = bs.find_all('span', class_='article-meta-value')[0].get_text() 
    remove_tag = main_id.find(' ')
    new_id = main_id[0:int(remove_tag)]

    #get the main content
    main_open_check = 'V'
    main_post_week = 'W'+str(main_week_num)
    
    main_content=bs.find('div',id='main-content')
    #remove tag from tree
    removes = main_content.find_all("div", class_= "article-metaline")
    for single_remove in removes:
        single_remove.extract()
    removes = main_content.find_all("div", class_="article-metaline-right")
    for single_remove in removes:
        single_remove.extract()
    removes = main_content.find_all("span", class_= "f2")
    for single_remove in removes:
        single_remove.extract()
    removes = main_content.find_all("div", class_="push")
    for single_remove in removes:
        single_remove.extract()
    main_review=cln.sub(' ',main_content.get_text())


    resList.append({
        'open_check':main_open_check,
        'post_week':main_post_week,
        'date':main_date,
        'time':main_time,
        'topic':topic,
        'review':main_review,
        'id':new_id,
        'url':url
    })

    return resList
def get_content(url):   
    cookies = requests.session()
    r2 = cookies.get(url)
    bs = BeautifulSoup(r2.text, 'html.parser')
    resList=list()

    topic = bs.find_all('span', class_='article-meta-value')[2].get_text()

    cln = re.compile(r'\n| |\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020|\t|\r')

    Main_post_week = bs.find_all('span', class_='article-meta-value')[3].get_text()[4:10]
    main_week_num = datetime.datetime.strptime('2019'+Main_post_week, '%Y%b %d').date().isocalendar()[1]

    pushes = 0
    for pushes in bs.find_all('div',class_="push"):
            #resDict['pushTag']=pushes.span.get_text()

        id = pushes.find('span',class_='f3 hl push-userid').get_text()
        review = pushes.find('span',class_='f3 push-content').get_text()[2:]
        date = datetime.datetime.strptime(('2019/'+ (cln.sub('',pushes.find('span',class_='push-ipdatetime').get_text()[0:6]))), '%Y/%m/%d')
        time = datetime.datetime.strptime((cln.sub('',pushes.find('span',class_='push-ipdatetime').get_text()[6:12])), '%H:%M')
        post_week = 'W' + str(date.date().isocalendar()[1])
        open_tag = ''

        resList.append({
            'open_check':open_tag,
            'post_week':post_week,
            'date':date,
            'time':time,
            'topic':topic,
            'review':review,
            'id':id,
            'url':url
        })
        
    return resList

def Save2Excel(posts):
    open_tag = [entry['open_check'] for entry in posts]
    post_week = [entry['post_week'] for entry in posts] 
    topics = [entry['topic'] for entry in posts]
    links = [entry['url'] for entry in posts]
    dates = [entry['date'] for entry in posts]
    times = [entry['time'] for entry in posts]
    authors = [entry['id'] for entry in posts]
    contents = [entry['review'] for entry in posts]
    df = DataFrame({
        '開文':open_tag,
        '發文周':post_week,
        '主題':topics,
        'URL':links,
        '日期': dates,
        '時間':times,
        'id':authors,
        '留言': contents
        })
    
    output_name = input('請輸入輸出檔名\n')
    #output_name = '123'
    final_name = output_name + '.xlsx'
    
    df.to_excel(final_name, sheet_name='sheet1', index=False, columns=['開文','發文周','日期','時間','Series','主題','id','留言',
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
    
    print('總共要處理 %d 篇文章\n\n' %(len(topic_list)))

    for i in range(len(topic_list)):
        temp_main = get_content_main(topic_list[i])
        all_reviews_list = all_reviews_list + temp_main
    for i in range(len(topic_list)):
        temp = get_content(topic_list[i])
        #print(temp_main)
        all_reviews_list = all_reviews_list + temp
        
        sys.stdout.write("\r目前已處理 %d 篇" % (i+1))
        sys.stdout.flush()

    print('\n')
    #print(all_reviews_list[0])
    Save2Excel(all_reviews_list)

main()