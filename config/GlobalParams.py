import requests
import xmltodict
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
# 단어 시퀀스 벡터 크기
MAX_SEQ_LEN = 12
# kewords
HOS_TYPE = ['요양병원', '한방병원', '종합병원', '치과병원','정신병원','노인병원']
HOS_SUBJECT = ['진료', '진찰', '전문', '종목', '진료과목', '진찰과목', '전문과목', '과목']
HOS_LOC = ['주소','위치','가는 길','찾아가기','길찾기','네비게이션','지도','어디','어딨','어떻게 가','어딘지','가는길','네비']
HOS_TEL = ['전화','번호','전화번호','연락','연락처']
Diss_city_code = {'수원시':41111,'성남시':41131,'의정부시':41150,'안양시':41171,'부천시':41190,'광명시':41210,
                   '평택시':41220,'동두천시':41250,'안산시':41271,'고양시':41281,'과천시':41290,'구리시':41310,
                   '남양주시':41360,'오산시':41370,'시흥시':41390,'군포시':41410,'의왕시':41430,'하남시':41450,
                   '용인시':41461,'파주시':41480,'이천시':41500,'안성시':41550,'김포시':41570,'화성시':41590,
                   '광주시':41610,'양주시':41630,'포천시':41650,'여주시':41670,'연천군':41800,'가평군':41820, '양평군':41830}


def GlobalParams():
    global MAX_SEQ_LEN, HOS_TYPE, HOS_SUBJECT, HOS_LOC, HOS_TEL
    global total_jsonObj, corona_INFO, predict_INFO

def xml_to_json(url):
    content = requests.get(url).content
    dict = xmltodict.parse(content)
    jsonString = json.dumps(dict['response']['body']['items']['item'], ensure_ascii=False)
    json_url = json.loads(jsonString)
    return json_url

# api url
url = "https://openapi.gg.go.kr/GgHosptlM?KEY=337b4bebd30e4d419b85a1ba8c9c26a2&pSize=1000"
url2 = "https://openapi.gg.go.kr/GgHosptlM?KEY=337b4bebd30e4d419b85a1ba8c9c26a2&pIndex=2&pSize=1000"
corona = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson?' \
         'serviceKey=Bog2YHvLzTtptxaFrVIGt6wnrqPUlq722t3FSu50vdFwRZQMkb8q9ANWj0ZkeKa%2BZb1vZNbaqm0yIRrCjkfJDA%3D%3D'
predict_url = 'http://apis.data.go.kr/B550928/dissForecastInfoSvc/getDissForecastInfo?serviceKey=' \
              'Bog2YHvLzTtptxaFrVIGt6wnrqPUlq722t3FSu50vdFwRZQMkb8q9ANWj0ZkeKa%2BZb1vZNbaqm0yIRrCjkfJDA%3D%3D&numOfRows=1000&pageNo=1&type=xml&'

# Hospital api
content = requests.get(url).content
content2 = requests.get(url2).content

dict = xmltodict.parse(content)
dict2 = xmltodict.parse(content2)

jsonString = json.dumps(dict['GgHosptlM']['row'], ensure_ascii=False)   # <GgHosptlM> 태그의 <row> 정보
jsonString2 = json.dumps(dict2['GgHosptlM']['row'], ensure_ascii=False)

jsonObj = json.loads(jsonString)
jsonObj2 = json.loads(jsonString2)
total_jsonObj = jsonObj + jsonObj2

# corona api
def corona_api() :
    start_day = str((datetime.today() - timedelta(1)).date()).replace('-','')
    end_day = str(datetime.today().date()).replace('-','')

    control = '&startCreateDt={0}&endCreateDt={1}'.format(start_day,end_day)
    corona_url = corona + control
    corona_json = xml_to_json(corona_url)
    corona_INFO = {}

    if len(corona_json) == 2 : # 오늘자 업데이트 됐을 시
        for tag in corona_json :
            if tag['stateDt'] == end_day :
                corona_INFO['A_stateDt'] = tag['stateDt'][:4] + '-' + tag['stateDt'][4:6] + '-' + tag['stateDt'][6:]
                corona_INFO['A_stateTime'] = tag['stateTime']
                corona_INFO['A_decideCnt'] = tag['decideCnt']
                corona_INFO['A_clearCnt'] = tag['clearCnt']
                corona_INFO['A_examCnt'] = tag['examCnt']
                corona_INFO['A_deathCnt'] = tag['deathCnt']
                corona_INFO['A_careCnt'] = tag['careCnt']
                corona_INFO['A_resutlNegCnt'] = tag['resutlNegCnt']
                corona_INFO['A_accExamCnt'] = tag['accExamCnt']
                corona_INFO['A_accExamCompCnt'] = tag['accExamCompCnt']
                rate = float(tag['accDefRate'])
                rate = round(rate,2)
                corona_INFO['A_accDefRate'] = str(rate) + '%'
    else :  # 아직 업데이트 안됐을 시
        corona_INFO['A_stateDt'] = corona_json['stateDt'][:4] + '-' + corona_json['stateDt'][4:6] + '-' + corona_json['stateDt'][6:]
        corona_INFO['A_stateTime'] = corona_json['stateTime']
        corona_INFO['A_decideCnt'] = corona_json['decideCnt']
        corona_INFO['A_clearCnt'] = corona_json['clearCnt']
        corona_INFO['A_examCnt'] = corona_json['examCnt']
        corona_INFO['A_deathCnt'] = corona_json['deathCnt']
        corona_INFO['A_careCnt'] = corona_json['careCnt']
        corona_INFO['A_resutlNegCnt'] = corona_json['resutlNegCnt']
        corona_INFO['A_accExamCnt'] = corona_json['accExamCnt']
        corona_INFO['A_accExamCompCnt'] = corona_json['accExamCompCnt']
        rate = float(corona_json['accDefRate'])
        rate = round(rate,2)
        corona_INFO['A_accDefRate'] = str(rate) + '%'
    return corona_INFO
# diss_predict api
def diss_predict_api(word) :
    predict_diss = []; predict_INFO = {};
    predict_INFO['A_Risk'] = 0
    predict_keys = [i for i in Diss_city_code.keys()]
    key = ''
    end_day = str(datetime.today().date()).replace('-','')
    # url 합치기(질병1~5)
    for i in range(1, 6) :
        option = 'dissCd={0}&znCd=41'.format(i)
        predict_diss += xml_to_json(predict_url + option)

    # word로 key 검색
    for i in range(0, len(predict_keys)) :
        if predict_keys[i].startswith(word) :
            key = predict_keys[i]

    # predict_INFO 정의
    for tag in predict_diss :
        if tag['dt'] == end_day and tag['lowrnkZnCd'] == str(Diss_city_code[key]):
                if int(tag['risk']) > predict_INFO['A_Risk'] :
                    predict_INFO['A_Risk'] = int(tag['risk'])

    return predict_INFO

