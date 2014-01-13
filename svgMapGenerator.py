import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import random,pickle

#Color: 00FF15	FFFB00	FFBF00	FF6A00	FF0000 960000
#Range: 50 		100 	150 	200 	300
 
svgLoc = 'SVG/BlankChinaMap.svg'
# styleFormat = 'fill: rgb(128, 128, 128); stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 0.731572; stroke-miterlimit: 4; stroke-dasharray: none; fill-opacity: 1;'
styleFormat = 'fill:#%s;stroke:rgb(255, 255, 255);stroke-width:0.73157200000000000;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;fill-opacity:1'
pm25Color = ['00FF15','FFFB00','FFBF00','FF6A00','C70000','590000']

# Map the district code to post code
def loadDisPost():
	disPost = {}
	areaNum = 0
	infile = open('postMapping.list','r')
	for iline in infile.readlines():
		iline = iline.replace('\r\n','')
		if len(iline)<=2 or iline[0] == '#':
			continue
		else:
			areaNum = areaNum +1
			inCityP = iline.split(' ')
			for iPostCode in inCityP[2:]:
				disPost[iPostCode] = inCityP[1]
	print 'Total area:'+str(areaNum)
	return disPost

def getColor(pm25):
	colorIdx = 0
	if pm25<=50:
		colorIdx = 0
	elif pm25<=100:
		colorIdx = 1
	elif pm25<=150:
		colorIdx = 2
	elif pm25 <=200:
		colorIdx =3
	elif pm25<=300:
		colorIdx =4
	else:
		colorIdx = 5
	return colorIdx

def getAreaPM25(disPost,postPM25):
	areaPM25 = {}
	areaCNT = {}
	for iCity in postPM25:
		print 'Proc '+iCity[0]
		areaCode = disPost[iCity[1][0:2]]
		if areaCode not in disPost:
			areaPM25[areaCode] = int(iCity[2])
			areaCNT[areaCode] = 1
		else:
			areaPM25[areaCode] = (areaPM25[areaCode]*areaCNT[areaCode] + int(iCity[2]))/(areaCNT[areaCode]+1)
			areaCNT[areaCode] = areaCNT[areaCode]+1
	print len(areaPM25)
	print disPost['13']
	print areaPM25['_40576568']
	return areaPM25


def svgGenerator(areaPM25):
	tree = ET.parse(svgLoc)
	root = tree.getroot()
	for inode in root.iter('{http://www.w3.org/2000/svg}path'):
		iCityID = inode.get('id') 
		if iCityID in areaPM25:
			# print inode.get('style')
			idx = getColor(areaPM25[iCityID])# random.randint(0,5)
			iStyle = styleFormat%(pm25Color[idx])
			# print iStyle
			inode.set('style',iStyle)
	tree.write('output.svg')

def pm25MapGenerator():
	postPM25 = pickle.load(open('PM25Current.p','rb'))
	# print postPM25
	disPost = loadDisPost()
	areaPM25 = getAreaPM25(disPost,postPM25)
	print areaPM25
	svgGenerator(areaPM25)

if __name__=='__main__':
	pm25MapGenerator()
	# loadCityPostID()
	# svgGenerator()
	# tree = ET.parse(svgLoc)
	# root = tree.getroot()
	# # for inode in list(root):
	# # 	print inode.tag
	# for inode in root.iter('{http://www.w3.org/2000/svg}path'):
	# 	print inode.get('id')
	# 	print inode.get('style')
