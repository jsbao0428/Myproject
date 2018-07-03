
# coding: utf-8

# In[3]:
#set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\huang\Desktop\LineBot\Linebot-33a6cfa20c62.json
from flask import Flask, request, abort
import re
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
'''(
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ConfirmTemplate,PostbackTemplateAction, MessageTemplateAction, URITemplateAction,
    CarouselColumn,ButtonsTemplate,CarouselTemplate,ImageSendMessage
)
'''
import requests
from bs4 import BeautifulSoup
import random
from dateutil.parser import parse
import json
import pandas as pd

#stock
import twstock
import matplotlib.pyplot as plt
import time
from datetime import timedelta, datetime
from imgurpython import ImgurClient
#api
from google.cloud import translate
import dialogflow
import googlemaps

app = Flask(__name__)

line_bot_api = LineBotApi('7quSgdi2HGlW6eHMxh5mHVaVv3/ojC4bx6ZwKYB2jMCd4SvgU5WXu/6LHQppNUAknvnzfhkPzrhDImEw9GjMEc4JVXIvHVD1gYjd4eRFGEAnTECSBIoUJD5KoTqtkqu+iMrMqPChFbrq+iQF/lVFKQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7abd763933584142f1220ddaa72a6455')


project_id = 'line-207303'
session_id = '8c0ea981768f460ca6f9481f5935d2d8' #access token
#imgur app
client_id = '5bad48390f9548d'
client_secret = 'f85b70b2cdbf4a54a187e70e8895456ea31069ac'
client = ImgurClient(client_id, client_secret)


gmaps = googlemaps.Client(key='AIzaSyCWqQPbTHwUMGxU8oNSY0DyWFVdFk24CJ8')

google_mapio = []

def mapper(road,keyword,radius):
    ids = []
    geocode_result = gmaps.geocode(road)
    loc = geocode_result[0]['geometry']['location']
    for place in gmaps.places_radar(keyword=keyword, location=loc, radius=radius)['results']:
        ids.append(place['place_id'])
        stores_info = []
        # 去除重複id
    ids = list(set(ids))
    content ='結果\n'
    for id in ids:
        stores_info.append(gmaps.place(place_id=id, language='zh-TW')['result'])
        output = pd.DataFrame.from_dict(stores_info)
    for i in range(len(output)):
        title = output["name"][i]
        add = output["formatted_address"][i]
        content += '{}\n{}\n'.format(title, add)
    return content
def detect_intent_texts(line, language_code = 'zh-cn'):
    """Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversaion."""
    texts = line
    content = ''
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.types.TextInput(
        text=texts, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(
        session=session, query_input=query_input)
    content += '{}'.format(response.query_result.fulfillment_text)
    return content


def translator_tw(line, target = 'zh-tw'):
    # Instantiates a client
    translate_client = translate.Client()
    # The text to translate
    text = line
    # The target language
    content = '<翻譯>\n'
    # Translates some text into Russian
    translation = translate_client.translate(text,target_language=target)
    BeforeTranslate = 'Text: {}\n'.format(text)
    AfterTranslate = 'Translation: {}\n'.format(translation['translatedText'])
    content += '{}\n{}\n'.format(BeforeTranslate, AfterTranslate)
    return content
def translator_cn(line, target = 'zh-cn'):
    # Instantiates a client
    translate_client = translate.Client()
    # The text to translate
    text = line
    # The target language
    content = ''
    # Translates some text into Russian
    translation = translate_client.translate(text,target_language=target)
    content += '{}'.format(translation['translatedText'])
    return content
def Zodiac(a):
    dom = requests.get('https://www.daily-zodiac.com/mobile/zodiac/'+a).text
    soup = BeautifulSoup(dom, 'html5lib')


    filtrate = re.compile(u'[^\u4E00-\u9FA5]')#非中文
    a = soup.select('.name')[0].text.strip()
    a = filtrate.sub(r' ', a).strip()#replace
    for i in soup.select('.today'):
        b = i.select('li')
        c = soup.select('article')[0].text.strip()
    content = '{}{}\n\n{}\t{}\n\n{}'.format(a,b[0].text.strip(),b[1].text.strip(),b[2].text.strip(),c)
    return content



def apple_news():
    print('蘋果即時新聞')
    dom = requests.get('http://www.appledaily.com.tw/appledaily/hotdaily/headline').text
    soup = BeautifulSoup(dom, 'html5lib')
    content = "<今日焦點新聞>\n"
    for index,ele in enumerate(soup.find('ul', 'all').find_all('li'),0):
        if index == 10:
            return content
        title = ele.find('div', 'aht_title').text
        link = ele.find('a')['href']
        content += '{}\n{}\n'.format(title, link)
    return content


def weather1():
    print('今日天氣')
    dom = requests.get('https://tw.appledaily.com/index/weather').text
    soup = BeautifulSoup(dom, 'html5lib')
    info = []
    for index,ele in enumerate(soup.find('section', 'fillup').find_all('div'),0):
        area = ele.find('h2').text
        hid = ele.find('span','hid').text
        lwd = ele.find('span','lwd').text
        text=ele.find('p','des').text
        info += [[area,hid,lwd,text]]
    content = '<今日天氣>\n最高溫：{}\n最低溫：{}\n狀態：{}'.format(info[0][1], info[0][2], info[0][3])
    return content
def weather2():
    print('今日天氣')
    dom = requests.get('https://tw.appledaily.com/index/weather').text
    soup = BeautifulSoup(dom, 'html5lib')
    info = []
    for index,ele in enumerate(soup.find('section', 'fillup').find_all('div'),0):
        area = ele.find('h2').text
        hid = ele.find('span','hid').text
        lwd = ele.find('span','lwd').text
        text=ele.find('p','des').text
        info += [[area,hid,lwd,text]]
    content = '<今日天氣>\n最高溫：{}\n最低溫：{}\n狀態：{}'.format(info[1][1], info[1][2], info[1][3])
    return content
def weather3():
    print('今日天氣')
    dom = requests.get('https://tw.appledaily.com/index/weather').text
    soup = BeautifulSoup(dom, 'html5lib')
    info = []
    for index,ele in enumerate(soup.find('section', 'fillup').find_all('div'),0):
        area = ele.find('h2').text
        hid = ele.find('span','hid').text
        lwd = ele.find('span','lwd').text
        text=ele.find('p','des').text
        info += [[area,hid,lwd,text]]
    content = '<今日天氣>\n最高溫：{}\n最低溫：{}\n狀態：{}'.format(info[2][1], info[2][2], info[2][3])
    return content
def weather4():
    print('今日天氣')
    dom = requests.get('https://tw.appledaily.com/index/weather').text
    soup = BeautifulSoup(dom, 'html5lib')
    info = []
    for index,ele in enumerate(soup.find('section', 'fillup').find_all('div'),0):
        area = ele.find('h2').text
        hid = ele.find('span','hid').text
        lwd = ele.find('span','lwd').text
        text=ele.find('p','des').text
        info += [[area,hid,lwd,text]]
    content = '<今日天氣>\n最高溫：{}\n最低溫：{}\n狀態：{}'.format(info[3][1], info[3][2], info[3][3])
    return content

TranslatesIO = []


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)#add webhook event(Message event)object,type of message= TextMessage
def handle_message(event):
    line=event.message.text
    #content = "{}: {}".format('q', event.message.text)

   ###
    ###button template###
    if line=='每日星座':
        buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://i.imgur.com/UyQzFKl.jpg',
            text='唐老師每日星座運勢',
            actions=[
                MessageTemplateAction(
                    label='火象星座',
                    text='火象星座'
                ),
                MessageTemplateAction(
                    label='土象星座',
                    text='土象星座'
                ),
                MessageTemplateAction(
                    label='風象星座',
                    text='風象星座'
                ),
                MessageTemplateAction(
                    label='水象星座',
                    text='水象星座'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
        return 0
 

    ###
    ###button template###
    if line=='火象星座':
        buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://i.imgur.com/UyQzFKl.jpg',
            text='火象星座',
            actions=[
                MessageTemplateAction(
                    label='牡羊座',
                    text='牡羊座'
                ),
                MessageTemplateAction(
                    label='獅子座',
                    text='獅子座'
                ),
                MessageTemplateAction(
                    label='射手座',
                    text='射手座'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
        return 0
 

    ###
    ######
    if line=='土象星座':
        buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://i.imgur.com/UyQzFKl.jpg',
            text='土象星座',
            actions=[
                MessageTemplateAction(
                    label='處女座',
                    text='處女座'
                ),
                MessageTemplateAction(
                    label='金牛座',
                    text='金牛座'
                ),
                MessageTemplateAction(
                    label='摩羯座',
                    text='摩羯座'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
        return 0
 

    ###
    ######
    if line=='風象星座':
        buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://i.imgur.com/UyQzFKl.jpg',
            text='風象星座',
            actions=[
                MessageTemplateAction(
                    label='雙子座',
                    text='雙子座'
                ),
                MessageTemplateAction(
                    label='天秤座',
                    text='天秤座'
                ),
                MessageTemplateAction(
                    label='水瓶座',
                    text='水瓶座'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
        return 0
 

    ###
    ######
    if line=='水象星座':
        buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://i.imgur.com/UyQzFKl.jpg',
            text='水象星座',
            actions=[
                MessageTemplateAction(
                    label='巨蟹座',
                    text='巨蟹座'
                ),
                MessageTemplateAction(
                    label='天蠍座',
                    text='天蠍座'
                ),
                MessageTemplateAction(
                    label='雙魚座',
                    text='雙魚座'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
        return 0
 

   
    ###
    ######
    
    
    
    if line=="雙子座":
        content = Zodiac('Gemini')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    if line=="天秤座":
        content = Zodiac('Libra')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    if line=="水瓶座":
        content = Zodiac('Aquarius')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    if line=="巨蟹座":
        content = Zodiac('Cancer')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    if line=="天蠍座":
        content = Zodiac('Scorpio')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    if line=="雙魚座":
        content = Zodiac('Pisces')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    if line=="金牛座":
        content = Zodiac('Taurus')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    if line=="處女座":
        content = Zodiac('Virgo')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    if line=="摩羯座":
        content = Zodiac('Capricorn')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    if line=="牡羊座":
        content = Zodiac('Aries')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    if line=="獅子座":
        content = Zodiac('Leo')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    if line=="射手座":
        content = Zodiac('Sagittarius')
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
        return 0
    #### 
    if line=="北部":
        content = weather1()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if line=="中部":
        content = weather2()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if line=="南部":
        content = weather3()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if line=="東部":
        content = weather4()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if line == "蘋果即時新聞":
        content = apple_news()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    

    ####Confirm template###
    if line == '時事':
        confirm_template_message = TemplateSendMessage(
        alt_text='Confirm template',
        template=ConfirmTemplate(
            text='需要什麼服務？',
            actions=[
                PostbackTemplateAction(
                    label='看新聞',
                    text='蘋果即時新聞',
                    data='蘋果即時新聞'
                ),
                MessageTemplateAction(
                    label='看報紙',
                    text='科技新報'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, confirm_template_message)
        return 0
    ###
    ###button template###
    if line=='今天天氣':
        buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://example.com/image.jpg',
            title='目錄',
            text='Please select',
            actions=[
                MessageTemplateAction(
                    label='北部天氣',
                    text='北部'
                ),
                MessageTemplateAction(
                    label='中部天氣',
                    text='中部'
                ),
                MessageTemplateAction(
                    label='南部天氣',
                    text='南部'
                ),
                MessageTemplateAction(
                    label='東部天氣',
                    text='東部'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_oken, buttons_template_message)
        return 0
    ###
    ######
    if line=='carousel':
        carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item1.jpg',
                    title='this is menu1',
                    text='description1',
                    actions=[
                        PostbackTemplateAction(
                            label='postback1',
                            text='postback text1',
                            data='action=buy&itemid=1'
                        ),
                        MessageTemplateAction(
                            label='message1',
                            text='message text1'
                        ),
                        URITemplateAction(
                            label='uri1',
                            uri='http://example.com/1'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item2.jpg',
                    title='this is menu2',
                    text='description2',
                    actions=[
                        PostbackTemplateAction(
                            label='postback2',
                            text='postback text2',
                            data='action=buy&itemid=2'
                        ),
                        MessageTemplateAction(
                            label='message2',
                            text='message text2'
                        ),
                        URITemplateAction(
                            label='uri2',
                            uri='http://example.com/2'
                        )
                    ]
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, carousel_template_message)
        return 0
    
    ###
    ######
    if(line.startswith('#')):
        line = line[1:]
        content = ''

        stock_rt = twstock.realtime.get(line)
        my_datetime = datetime.fromtimestamp(stock_rt['timestamp'])
        my_time = my_datetime.strftime('%H:%M:%S')

        content += '%s (%s) %s\n' %(
            stock_rt['info']['name'],
            stock_rt['info']['code'],
            my_time)
        content += '現價: %s / 開盤: %s\n'%(
            stock_rt['realtime']['latest_trade_price'],
            stock_rt['realtime']['open'])
        content += '最高: %s / 最低: %s\n' %(
            stock_rt['realtime']['high'],
            stock_rt['realtime']['low'])
        content += '交易量: %s\n' %(stock_rt['realtime']['accumulate_trade_volume'])

        stock = twstock.Stock(line)#twstock.Stock('2330')
        content += '-----\n'
        content += '最近五日價格: \n'
        price5 = stock.price[-5:][::-1]
        date5 = stock.date[-5:][::-1]
        for i in range(len(price5)):
            content += '[%s] %s\n' %(date5[i].strftime("%Y-%m-%d"), price5[i])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content)
        )
        return 0

    if line == '主打商品':
        image_carousel_template_message = TemplateSendMessage(
        alt_text='ImageCarousel template',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url='https://imgur.com/FjgDREY.jpg',
                    action=PostbackTemplateAction(
                        label='青椒',
                        text='青椒',
                        data='action=buy&itemid=1'
                        )
                    ),
                ImageCarouselColumn(
                    image_url='https://imgur.com/IXWQqnE.jpg',
                    action=PostbackTemplateAction(
                        label='洋蔥',
                        text='洋蔥',
                        data='action=buy&itemid=2'
                        )
                    ),
                ImageCarouselColumn(
                    image_url='https://imgur.com/6Q6AjtR.jpg',
                    action=PostbackTemplateAction(
                        label='紅蘿蔔',
                        text='紅蘿蔔',
                        data='action=buy&itemid=2'
                        )
                    ),
                ImageCarouselColumn(
                    image_url='https://imgur.com/RTjzZvT.jpg',
                    action=PostbackTemplateAction(
                        label='草莓',
                        text='草莓',
                        data='action=buy&itemid=2'
                        )
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, image_carousel_template_message)
        return 0


    if line == '目前位置':
        confirm_template_message = TemplateSendMessage(
        	alt_text='Confirm Template',
        	template=ConfirmTemplate(
        		text='是否傳送目前位置?',
        		actions=[
        			URITemplateAction(
        				label='Yes',
        				uri='line://nv/location'
        			),
        			PostbackTemplateAction(
        				label='No',
        				text='Can not get location',
        				data='No_autho'
        			)
        		]
        	)
        )
        line_bot_api.reply_message(event.reply_token, confirm_template_message)
        return 0



    #圖片
    if line == '嗨抽':
        images = client.get_album_images('Pyxv0oM')
        index = random.randint(0, len(images)-1)
        url = images[index].link
        message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url)
        line_bot_api.reply_message(event.reply_token, message)
    if line == '抽':
        images = client.get_album_images('PqrhsFX')
        index = random.randint(0, len(images)-1)
        url = images[index].link
        message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url)
        line_bot_api.reply_message(event.reply_token, message)
    if line == '控肉抽':
        images = client.get_album_images('FHj8goR')
        index = random.randint(0, len(images)-1)
        url = images[index].link
        message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url)
        line_bot_api.reply_message(event.reply_token, message)
    if line == '肌肉抽':
        images = client.get_album_images('IflRmJd')
        index = random.randint(0, len(images)-1)
        url = images[index].link
        message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url)
        line_bot_api.reply_message(event.reply_token, message)

    if line == '汽車':
        images = client.get_album_images('qqPqxGy')
        index = random.randint(0, len(images)-1)
        url = images[index].link
        message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url)
        line_bot_api.reply_message(event.reply_token, message)


    if line == '開啟翻譯':
        TranslatesIO.append(line)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='請輸入需要翻譯的文字'))
        return 0
    if line == '關閉翻譯':
        TranslatesIO[:] = []
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='bye~'))
        return 0
    if TranslatesIO :
        content = translator_tw(line)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0


    if line == "開始搜尋":
        google_mapio.append(line)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text = "請輸入縣市,類型,範圍"))
        return 0
    if line == "關閉搜尋":
        google_mapio.pop()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text = "88"))
        return 0
    if google_mapio:
        content = mapper(line.split(' ',2)[0],line.split(' ',2)[1],line.split(' ',2)[2])
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text = content))
        return 0
    ###
    ###button template###
    if line=='產品訂購':
        buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://imgur.com/wSkcawC.jpg',
            title='產品訂購',
            text='請選擇類別',
            actions=[
                MessageTemplateAction(
                    label='水果類',
                    text='訂購水果'
                ),
                MessageTemplateAction(
                    label='蔬菜類',
                    text='訂購蔬菜'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
        return 0
    ####
    if line=='訂購水果':
        buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://imgur.com/LegoZBt.jpg',
            title='產品訂購',
            text='請選擇數量',
            actions=[
                URITemplateAction(
                            label='大量訂購',
                            uri='https://www.google.com.tw/'
                        ),
                URITemplateAction(
                            label='小量訂購',
                            uri='http://yahoo.com.tw/'
                        )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
        return 0
    ####
    if line=='訂購蔬菜':
        buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://i.imgur.com/ck7mQQy.jpg',
            title='產品訂購',
            text='請選擇數量',
            actions=[
                URITemplateAction(
                            label='大量訂購',
                            uri='https://www.google.com.tw/'
                        ),
                URITemplateAction(
                            label='小量訂購',
                            uri='http://yahoo.com.tw/'
                        )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
        return 0

    ####
    else:
        #line  = translator_cn(line)
        #content = detect_intent_texts(line)
        #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0


@handler.add(PostbackEvent) #add webhook event(Postback event) object
def handel_postback(event):
    if event.postback.data == 'Yes_autho':
        buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://example.com/image.jpg',
            title='目錄',
            text='Please select',
            actions=[
                URITemplateAction(
                    label='請選擇位置',
                    uri='line://nv/location'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
        return 0
    else:
        return 0

@handler.add(MessageEvent, message=LocationMessage) #add webhook event(Message event)object,type of message=LocationMessage
def handel_location_message(event):
    print('OK')
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text = event.message.address))



if __name__ == "__main__":
    app.run()

