from lxml import html
import requests

def get_hottest_subs():
	page = requests.get('http://redditlist.com/')
	tree = html.fromstring(page.content)
	hot_subs = []
	for i in range (0, 20):
		hot_sub = tree.xpath('//*[@id="listing-parent"]/div[1]/div[' + str(i+2) + ']/span[3]/a/text()')
		hot_subs.append(hot_sub)
	return hot_subs
