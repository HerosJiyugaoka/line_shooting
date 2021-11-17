import csv
import os
import sys
import requests
import numpy as np

import slackweb
import pandas as pd
from bs4 import BeautifulSoup

from linebot import LineBotApi
from linebot.models import TextSendMessage

#環境変数取得
CHANNEL_ACCESS_TOKEN = 'アクセストークン'
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

def scraping():
    url = 'スクレイピングしたいURL'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    result_tit = []
    for top_news in soup.find_all(class_=['tit']):
        result_tit.append([
        top_news.text
        ])

    result_url = []
    for top_url in soup.find_all(class_=['more']):
        result_url.append([
        'https://e-gakkou.jp' + top_url.get('href')
        ])

    result = result_tit
    for i in range(9):
        result[i].extend(result_url[i])

    return result

#csvファイルを開いてリストを格納
def output_csv(result):
  with open('last_log.csv', 'w', newline='',encoding='utf_8') as file:
    headers = ['Title', 'URL']
    writer = csv.writer(file)
    writer.writerow(headers)
    for row in result:
      writer.writerow(row)

#csvファイルを開いてリストに格納
def read_csv():
  if not os.path.exists('last_log.csv'):
    raise Exception('ファイルがありません。')
  if os.path.getsize('last_log.csv') == 0:
    raise Exception('ファイルの中身が空です。')
  csv_list = pd.read_csv('last_log.csv', header=None).values.tolist()
  return csv_list

#last_log.csvから格納したリストとスクレイピングしたリストを比較し、異なる部分のみ格納
def list_diff(result, last_result):
    return_list = []
    for tmp in (result):
        if tmp not in last_result:
            return_list.append(tmp)
    return return_list

#slackに送信
def send_to_slack(diff_list):
  text = '<!channel>\n'
  for tmp in diff_list:
    text += tmp[0] + '\n' + tmp[1] + '\n'
  slack = slackweb.Slack(url='slackのwebhook URL')
  slack.notify(text=text)

def line_shooting(diff_list):
    text = 'ブログ更新しました!\n ぜひ、チェックしてみてください！\n'
    for tmp in diff_list:
        text += '「' + tmp[0] + '」' + '\n' +tmp[1]
    line_bot_api.broadcast(TextSendMessage(text=text))

result = scraping()

csv_list = read_csv()

diff_list = list_diff(result, csv_list)

if diff_list != []:
    send_to_slack(diff_list)
    line_shooting(diff_list)

else:
    line_shooting(diff_list)

output_csv(result)
