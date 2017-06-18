from sklearn.externals import joblib
import praw
import datetime
from operator import attrgetter
import sys
from lxml import html
import requests

class Post:
	def __init__(self, subreddit, author, title, score, numOfComments, permalink, diff_minutes, chance_to_go_viral):
		self.subreddit = subreddit
		self.author = author
		self.title = title
		self.score = score
		self.numOfComments = numOfComments
		self.permalink = permalink
		self.diff_minutes = diff_minutes
		self.chance_to_go_viral = chance_to_go_viral


def get_hottest_subs():
	page = requests.get('http://redditlist.com/')
	tree = html.fromstring(page.content)
	hot_subs = []
	for i in range (0, 6):
		hot_sub = tree.xpath('//*[@id="listing-parent"]/div[1]/div[' + str(i+2) + ']/span[3]/a/text()')
		hot_subs.append(hot_sub)
	return hot_subs

def find_a_hot_post():
	subredditsToScan = get_hottest_subs()
	#subredditsToScan = ["AskReddit", "aww", "funny", "gaming", "gifs", "music", "pics", "politics", "sports", "todayilearned", "videos", "worldnews"]
	reddit = praw.Reddit(client_id='nom',
                     client_secret="nom",
                     user_agent='pythonscript:com.example.frontandrisingchecker:v0.1 (by /u/connlloc)',
                     username='connlloc',
                     password='nom')

	svm = joblib.load('modelSvm.pkl')



	for subreddit in subredditsToScan:
		fillers = []
		for submission in reddit.subreddit(subreddit[0]).new(limit=50):
			author = submission.author
	        title = submission.title
	        score = submission.score
	        numOfComments = submission.num_comments
	        permalink = submission.permalink
	        timeCreated = submission.created_utc

	        timeOfPost = datetime.datetime.utcfromtimestamp(timeCreated)
	        timeNow = datetime.datetime.utcnow()

	        diff = timeNow - timeOfPost
	        diff_minutes = (diff.days * 24 * 60) + (diff.seconds/60)

	        if diff_minutes == 0:
	            diff_minutes = 1 
	        if diff_minutes < 140:
	            prediction = svm.predict_proba([[score,numOfComments,diff_minutes,0]])
	            if prediction[0][1] > 0.60:
	            	return Post(subreddit, author, title, score, numOfComments, permalink, diff_minutes, prediction[0][1])

bestPost = find_a_hot_post()

print("Hottest post:")
print(bestPost.subreddit)
print('Author: ' + str(bestPost.author))
print('Title: ' + bestPost.title)
print('Score: ' + str(bestPost.score))
print('# of Comments: ' + str(bestPost.numOfComments))
print('Link: ' + bestPost.permalink)
print('Age: ' + str(bestPost.diff_minutes))
print('Viral % : ' + str(bestPost.chance_to_go_viral))
