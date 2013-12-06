
from bs4 import BeautifulSoup
from datetime import date,datetime
from time import sleep
import urllib2,os,shutil
import pickle,urlparse
import re

webSiteURL = "http://www.cnpm25.cn"
# cityList and Detail Read from Internet 1 for true, 0 for false
FORCEUPDATE = 0
cityListMode = 0
cityDetailMode = 0
#Whether save the raw data
cityDetailSave = 0
# Daily City PM2.5 Save
cityDailySave = 1

def dataLoading():
	print 'Begin to Read City List'
	if cityListMode or FORCEUPDATE == 1:
		data = urllib2.urlopen(webSiteURL).read()
		pickle.dump(data,open("cityList.p","wb"))
	else:
		data = pickle.load(open("cityList.p","rb"))
	return data

def getCityURL(data):
	# return the city and its url in [['cityname','url']] form
	ingreds = data.find('div', {'class': 'warp'})
	cityURL = [[s.getText().replace(u'\xa0','').replace(' ',''),s.get("href")] for s in ingreds.findAll('a')]
	return cityURL

def getCityPM25(cityURL):
	cityRawDir = 'cityRawData'
	cityPM25 = []
	if not os.path.exists(cityRawDir):
		os.mkdir(cityRawDir)

	dateDirName = os.path.join(cityRawDir,datetime.today().strftime('%Y%m%d'))

	if cityDetailMode or FORCEUPDATE == 1:
		if os.path.exists(dateDirName):
			shutil.rmtree(dateDirName)
		os.mkdir(dateDirName)

	for iCity in cityURL:
		cityNameReg = re.compile('[\w]*')
		iCityName = cityNameReg.findall(iCity[1])[2]
		# if iCityName !='yibin':
		# 	continue
		if cityDetailMode or FORCEUPDATE == 1:
			iCityURL = urlparse.urljoin(webSiteURL,iCity[1])
			try:
				cityData = urllib2.urlopen(iCityURL).read()
				if cityDetailSave == 1:
					open(os.path.join(dateDirName,iCityName+'_'+datetime.today().strftime('%Y%m%d%H')+'.html'),'w').write(cityData)
			except urllib2.HTTPError:
				print iCityName +' Not found'
				continue
			except:
				print 'Something went wrong'
			sleep(0.1)
		else:
			#print iCity[1].split('/')[1].split('.')[0]
			try:
				cityData = open(os.path.join(dateDirName,iCityName+'_'+datetime.today().strftime('%Y%m%d%H')+'.html'),'r').read()
			except IOError:
				print iCity[1]+' Not found'
		iCitypm25 = re.compile('[\d]+').findall(\
			re.compile('jin_value = "[\d]*"').findall(cityData)[1])[0]
		cityPM25.append([iCity[0],iCityName,iCitypm25])
		print iCityName

	return cityPM25

def PM25Crawler():
	rawdata = dataLoading()
	bsData = BeautifulSoup(rawdata)

	cityURL = getCityURL(bsData)

	todayDataPath = os.path.join('cityDailyData',datetime.today().strftime('%y%m%d%H')+'.p')
	if os.path.exists(todayDataPath) and not FORCEUPDATE:
		cityPM25 = pickle.load(open(todayDataPath,'rb'))
	else:
		cityPM25 = getCityPM25(cityURL)
		if cityDailySave:
			if not os.path.exists('cityDailyData'):
				os.mkdir('cityDailyData')
			pickle.dump(cityPM25,open(todayDataPath,'wb'))

	# for iCity in cityPM25:
		# if iCity[1] == 'zigong':
		# 	print iCity
		# print '%s %s'%(iCity[0].encode('utf8'),iCity[2])

if __name__=="__main__":
	PM25Crawler()
