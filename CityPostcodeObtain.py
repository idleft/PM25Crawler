import urllib2,pickle,re
from bs4 import BeautifulSoup
from time import sleep
url = 'http://www.ip138.com/post/search.asp?area='

# To be fix: the post code of Changzhi is not valid since the same
# city name. Can be filtered with length validation.
def getCityPoCode(cityName):
	enURL = url + urllib2.quote(cityName.encode('gb2312'))+'&action=area2zip'
	# print enURL
	rawdata = urllib2.urlopen(enURL).read()
	
	bsData = BeautifulSoup(rawdata)
	postItem = bsData.findAll('td',{'class':'tdc2'}) # for Baidu
	postCode = re.compile('\d+').findall(postItem[1].text)
	if len(postCode) == 0:
		postCode = ''
	else:
		postCode = postCode[0]
	return postCode	

def cityFilter(cityURL):
	fCityList = []
	for iCity in cityURL:
		iCityPostCode = getCityPoCode(iCity[0])
		if iCityPostCode =='':
			# cityURL.remove(iCity)
			print iCity[0].encode('utf8')+ ' Filtered'
		else:
			iCity.append(iCityPostCode)
			fCityList.append(iCity)
		sleep(0.1)
		# print iCity[0].encode('utf8')+iCity[1].encode('utf8')+iCityPostCode.encode('utf8')
	pickle.dump(fCityList,open('cityURLPost.p','wb'))
	return fCityList

if __name__ == '__main__':
	cityURL = pickle.load(open('cityURL.p','rb'))
	cityURL = cityFilter(cityURL)
	