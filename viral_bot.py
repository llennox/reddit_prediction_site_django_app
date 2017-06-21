import praw
from sklearn.externals import joblib
import datetime
import os

reddit = praw.Reddit(client_id='DFMTP3Ya0_rHjw',
                     client_secret='_hOft5vgpguVkIoSXoqEbpeS5q8',
                     user_agent='pythonscript:com.example.viral_notification_bot:v0.1 (by /u/redditpirateroberts)',
                     username='username',
                     password='pword')

subredditsToScan = ["Art", "AskReddit", "askscience", "aww", "books", "creepy", "dataisbeautiful", "DIY", "Documentaries", "EarthPorn", "explainlikeimfive", "food", "funny", "gaming", "gifs", "history", "jokes", "LifeProTips", "movies", "music", "pics", "science", "ShowerThoughts", "space", "sports", "tifu", "todayilearned", "videos", "worldnews", "soccer", "news", "BlackPeopleTwitter", "Overwatch", "IAmA", "InternetIsBeautiful", "programming", "OldSchoolCool", "philosophy", "gonewild", "leagueoflegends", "trees", "Drugs", "wholesomememes", "bestof", "WTF", "WritingPrompts", "bitcoin"]
svm = joblib.load('modelSvm.pkl')


if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []
else:
    with open("posts_replied_to.txt", "r") as f:
       posts_replied_to = f.read()
       posts_replied_to = posts_replied_to.split("\n")
       posts_replied_to = list(filter(None, posts_replied_to))


for subreddit in subredditsToScan:
	for submission in reddit.subreddit(subreddit).new(limit=100):
		author = submission.author
		title = submission.title
		score = submission.score
		numOfComments = submission.num_comments
		permalink = submission.permalink
		timeCreated = submission.created_utc
		submissionId = submission.id

		already_commented_on = False
		for postRepliedTo in posts_replied_to:
			if submissionId == postRepliedTo:
				already_commented_on = True

		if already_commented_on == False:
			timeOfPost = datetime.datetime.utcfromtimestamp(timeCreated)
			timeNow = datetime.datetime.utcnow()

			diff = timeNow - timeOfPost
			diff_minutes = (diff.days * 24 * 60) + (diff.seconds/60)

			if diff_minutes == 0:
				diff_minutes = 1 

			if diff_minutes < 140:
				#writerPosts.writerow([author, subreddit.encode('utf-8').strip(), score, numOfComments, title.encode('utf-8').strip(), permalink.encode('utf-8').strip(), diff_minutes, submissionId])
				divider = diff_minutes
				if divider == 0:
					divider = 1

				prediction = svm.predict_proba([[score,numOfComments,diff_minutes,1]])
				if prediction[0][1] > 0.50:
					print("Found new post likely to go viral")
					print(title)
					print(subreddit)
					print(score)
					print(diff_minutes)
					print("\n")
					posts_replied_to.append(submissionId)
					submission.reply("Congrats, according to my super dank algorithms you're post has a " + str(prediction[0][1] " percent chance of going viral. We did it Reddit!"))


with open("posts_replied_to.txt", "w") as f:
    for post_id in posts_replied_to:
    	f.write(post_id + "\n")

#for submission in reddit.subreddit("AskReddit").new(limit=2):
#	submission.reply("Botty bot says: Me too!!")