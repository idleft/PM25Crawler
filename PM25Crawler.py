
from bs4 import BeautifulSoup
from datetime import date,datetime
from time import sleep
import urllib2,os,shutil
import pickle,urlparse
import re
from ast import literal_eval

webSiteURL = "http://www.cnpm25.cn"
# cityList and Detail Read from Internet 1 for true, 0 for false
FORCEUPDATE = 0
cityListMode = 1
# Daily City PM2.5 Save
cityDailySave = 1

def getCityURL(data):
	# return the city and its url in [['cityname','url']] form
	data = urllib2.urlopen(webSiteURL).read()
	print 'Begin to Read City List'
	if cityListMode or FORCEUPDATE == 1:
		print 'Update from Internet'
		bsData = BeautifulSoup(data)
		ingreds = bsData.find('div', {'class': 'warp'})
		# The website has losing tag, which miss a </a>. Thus, the result have to be manually fixed
		# New fix. Use \n to split the city names
		cityURL = [[s.getText().split('\n')[0].replace(u'\xa0','').replace(' ',''),s.get("href")] for s in ingreds.findAll('a')]
		pickle.dump(cityURL,open("cityURL.p","wb"))
	else:
		cityURL = pickle.load(open('cityURL.p','rb'))
	return cityURL

def getCityPM25(cityURL):

	cityPM25 = []

	for iCity in cityURL:
		cityNameReg = re.compile('[\w]*')
		iCityName = cityNameReg.findall(iCity[1])[2]
		iCityURL = urlparse.urljoin(webSiteURL,iCity[1])
		# print iCityURL
		try:
			cityData = urllib2.urlopen(iCityURL).read()
		except urllib2.HTTPError:
			print iCityName +' Not found'
			continue
		except:
			print 'Something went wrong'
			sleep(0.1)
		iCitypm25 = re.compile('[\d]+').findall(\
			re.compile('jin_value = "[\d]*"').findall(cityData)[1])[0]
		# The cityPM25 contains ['utf8 Chinese name','English name','cityPostCode','PM25Value']
		cityPM25.append([iCity[0],iCityName,iCity[2],iCitypm25])
		print iCityName+' '+iCitypm25

	return cityPM25

def loadCityURLPost():
	cityURL = []
	cityURL = pickle.load(open('CityURLPost.p','rb'))
	return cityURL

def dumpPostPM25(cityPM25):
	postPM25 = []
	for iCity in cityPM25:
		postPM25.append(iCity[2:])
	pickle.dump(postPM25,open('PM25Current.p','wb'))
	# print postPM25

def PM25Crawler():

	# cityURL = getCityURL()
	cityURL = loadCityURLPost()
	todayDataPath = os.path.join('cityDailyData',datetime.today().strftime('%y%m%d%H')+'.p')
	if os.path.exists(todayDataPath) and not FORCEUPDATE:
		cityPM25 = pickle.load(open(todayDataPath,'rb'))
	else:
		cityPM25 = getCityPM25(cityURL)
		if cityDailySave:
			if not os.path.exists('cityDailyData'):
				os.mkdir('cityDailyData')
			pickle.dump(cityPM25,open(todayDataPath,'wb'))
	dumpPostPM25(cityPM25)
	# print cityPM25

if __name__=="__main__":
	PM25Crawler()