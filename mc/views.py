from django.shortcuts import render, redirect
from sklearn.externals import joblib
from django.http import Http404, HttpResponse
import praw
import datetime
from operator import attrgetter
import sys
import numpy as np
from mc.forms import subs, EmailNewPass, Usersubs
from mc.models import UserList
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from lxml import html
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, permissions, status, authentication
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from mc.serializers import CommentSerializer
from google.cloud import vision

reddit = praw.Reddit(client_id='r7gDiisP6rFi7g',
                     client_secret='nLEQAhbP34dCQNBNzy_brxE_zGI',
                     user_agent='pythonscript:com.example.frontandrisingchecker:v0.1 (by /u/redditpirateroberts)',
                     username='redditpirateroberts',
                     password='aDreamer24')

class Post:
        def __init__(self, subreddit, author, title, score, numOfComments, permalink, diff_minutes):
                self.subreddit = subreddit
                self.author = author
                self.title = title
                self.score = score
                self.numOfComments = numOfComments
                self.permalink = permalink
                self.diff_minutes = diff_minutes

class PostAPI:
        def __init__(self, subreddit, author, title, score, numOfComments, permalink, diff_minutes, url, domain, selftext):
                self.subreddit = subreddit
                self.author = author
                self.title = title
                self.score = score
                self.numOfComments = numOfComments
                self.permalink = permalink
                self.diff_minutes = diff_minutes
                self.url = url
                self.domain = domain
                self.selftext = selftext

class HotPost:
        def __init__(self, subreddit, title, permalink, rating):
                self.subreddit = subreddit
                self.title = title
                self.permalink = permalink
                self.rating = rating

class BestPost:
        def __init__(self, subreddit, author, title, score, numOfComments, permalink, diff_minutes, chance_to_go_viral):
                self.subreddit = subreddit
                self.author = author
                self.title = title
                self.score = score
                self.numOfComments = numOfComments
                self.permalink = permalink
                self.diff_minutes = diff_minutes
                self.chance_to_go_viral = chance_to_go_viral



rfc = joblib.load('/home/connlloc/sites/mc/modelSvm.pkl')
trendingPosts = []

def apiDocs(request):
    return render(request,'apiDocs.html')

class Misc:
    

    def auth(self, authtoken):
        
        user = User.objects.get(auth_token=authtoken)
        if user.is_authenticated():
            return user
        elif user.exists() == False:
            return HttpResponse('user does not exist', status=status.HTTP_400_BAD_REQUEST)
        elif user.is_authenticated() == False:
            return HttpResponse('you must log in first', status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse('user does not exist or authtoken is incorrect', status=status.HTTP_400_BAD_REQUEST)

class redditSearch(APIView):


    def post(self, request, *args):
        auth = Misc()
        auth.auth(request.data['authtoken'])
        posts = returnTrending("politics",[])
        l = []
        for post in posts:
            entry = {
            "subreddit": post.subreddit,
        "title": post.subreddit,
        "permalink":  post.permalink,
        "rating": post.rating, 
        }
            l.append(entry)
        serializer = CommentSerializer(data=l, many=True)
        
        if serializer.is_valid(): 
            return Response(serializer.data, status=status.HTTP_200_OK)
        return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


##----Mark's additions:
class GetHottestPosts(APIView):


    def get(self, request, *args):
#       final arguments for this function:
#            args[0] - minimum_chance_to_go_viral - float - 0.91 - default: 0.0
#            args[1] - content_type - string_list - gifs,pics,videos,text,link - default: all
#            args[2] - platforms - string_list - reddit,twitter,youtube - default: all
#            args[3] - content_tags - string_list - cat,mammal,politics - default: none
#            args[4] - platform_specific_searches - string_list - reddit:politics,news,worldnews;twitter:got - default: none
#            args[5] - number_of_post_to_return - int - 10 - default: 20

#       current arguments for this function:
#            args[0] - minimum_chance_to_go_viral - float - 0.91 - default: 0.0
#            args[1] - content_type - string_list - gif,img,video,text,link - default: all
#            args[2] - specific_content_tags - string_list - cat,mammal,politics - default: none
#            args[3] - specific_subreddits - string_list - reddit:politics,news,worldnews; - default: none
#            args[4] - number_of_post_to_return - int - 10 - default: 20

        auth = Misc()
        auth.auth(args[0])
        number_of_posts_to_return = args[5]
        number_of_posts_to_return = int(number_of_posts_to_return)
        empty_list = []
        posts = returnTrendingAPI(args[1], args[2], args[3], args[4], number_of_posts_to_return, empty_list)
        l = []
        mylist = []     
        for post in posts:
            #add platform for entry 
            
                   
            entry = {
            "subreddit": post.subreddit,
            "title": post.title,
            "permalink":  post.permalink,
            "rating": post.rating, 
            }  
            l.append(entry)
        serializer = CommentSerializer(data=l, many=True)
        posts = []       
        if serializer.is_valid(): 
            return Response(serializer.data, status=status.HTTP_200_OK)
        return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


##----End of Mark's additions.

def get_hottest_subs():
        page = requests.get('http://redditlist.com/')
        tree = html.fromstring(page.content)
        hot_subs = []
        for i in range (0, 6):
                hot_sub = tree.xpath('//*[@id="listing-parent"]/div[1]/div[' + str(i+2) + ']/span[3]/a/text()')
                hot_subs.append(hot_sub)

        for subreddit in hot_subs:
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
                        prediction = rfc.predict_proba([[score,numOfComments,diff_minutes,0]])

                        if prediction[0][1] > 0.60:
                            chance_to_go_viral = prediction[0][1]
                            chance_to_go_viral=chance_to_go_viral * 100
                            chance_to_go_viral = round(chance_to_go_viral, 2)
                            return BestPost(subreddit, author, title, score, numOfComments, permalink, diff_minutes, chance_to_go_viral)


def email(request):
    if request.method == 'POST':       
        form = EmailNewPass(request.POST)
        if form.is_valid():
            email = form.cleaned_data['aemail']
            e = TheEmails(emails=email)
            e.save()
            emailSaved = True
            form = subs()
            return render(request, 'home.html',{'form':form, 'emailSaved':emailSaved})
    else:
        form = subs()
        emailSaved = False
        return render(request, 'home.html',{'form':form, 'emailSaved':emailSaved})

@never_cache
@login_required(login_url='/sign_page/')
def userView(request):
    
    try:
        customlist = UserList.objects.filter(username=request.user.username)
        
    except:
        customlist = None

    
    trendingPosts = []
    if request.method == 'POST':
        form = subs(request.POST)
        if form.is_valid():
            subreddit = form.cleaned_data['subreddits']

            subreddits = subreddit.split(',')
            if len(subreddits) > 1:
                for subreddit in subreddits:
                    TrendingPosts = returnTrending(subreddit, trendingPosts)

            else:
                trendingPosts = returnTrending(subreddit, trendingPosts)

            for post in trendingPosts:
                post.rating=post.rating * 100 
                post.rating = round(post.rating, 2)
        form = Usersubs()
        return render(request,'user.html', {'Posts':trendingPosts,'form':form,'customlist':customlist})
    form = Usersubs()

    return render(request,'user.html', {'Posts':trendingPosts,'form':form,'customlist':customlist})


@never_cache
@login_required(login_url='/sign_page/')
def deleteList(request, listuuid):
    l = UserList.objects.get(listuuid=listuuid)
    if request.user.username == l.username:
        l.delete()
    return redirect('/user-list/')

@never_cache
@login_required(login_url='/sign_page/')
def userList(request):
    try:
        customlist = UserList.objects.filter(username=request.user.username)
       
    except:
        customlist = []

    l=None   
    if request.method == 'POST' and len(customlist) <= 10:
        subs = request.POST.getlist('subreddits')
        label = request.POST.get('label')
        if len(subs) <= 10:
            itemlist = ''
            counter = False
            for item in subs:
                if item:
                    if counter == False:
                        counter = True
                        itemlist = itemlist + item
                    else:
                        itemlist = itemlist + ',' + item               
        l = UserList(username=request.user.username,subreddits=itemlist,label=label)
        l.save()
        try:
            customlist = UserList.objects.filter(username=request.user.username)
        
        except:
            customlist = []

        request.method = 'GET'
        return render(request, 'userlist.html',{'customlist':customlist})
    return render(request, 'userlist.html',{'customlist':customlist})

@never_cache
def home(request):
    trendingPosts = []


    if request.method == 'POST':
        form = subs(request.POST)
        if form.is_valid():
            subreddit = form.cleaned_data['subreddits']

            subreddits = subreddit.split(',')
            if len(subreddits) > 1:
                for subreddit in subreddits:
                    TrendingPosts = returnTrending(subreddit, trendingPosts)

            else:
                trendingPosts = returnTrending(subreddit, trendingPosts)

            for post in trendingPosts:
                post.rating=post.rating * 100
                post.rating = round(post.rating, 2)
        form = subs()
        return render(request,'home.html', {'Posts':trendingPosts,'form':form})
    form = subs()
    bestPost = get_hottest_subs()
    bestPost.subreddit = bestPost.subreddit[0]
    return render(request,'home.html', {'bestPost':bestPost,'Posts':trendingPosts,'form':form})



def get_video_id(url):
    youtube_regex = (
        r'(https?://)?(www.)?'
        '(youtube|youtu|youtube-nocookie).(com|be)/'
        '(watch?v=|embed/|v/|.+?v=)?([^&=%?]{11})')
#       current arguments for this function:
#            args[0] - minimum_chance_to_go_viral - float - 0.91 - default: 0.0
#            args[1] - content_type - string_list - gifs,pics,videos,text,link - default: all
#            args[2] - platforms - string_list - reddit,twitter,youtube - default: all
#            args[3] - content_tags - string_list - cat,mammal,politics - default: none
#            args[4] - platform_specific_searches - string_list - reddit:politics,news,worldnews;twitter:got - default: none
#            args[5] - number_of_post_to_return - int - 10 - default: 20

#       final arguments for this function:
#            args[0] - minimum_chance_to_go_viral - float - 0.91 - default: 0.0
#            args[1] - content_type - string_list - gifs,pics,videos,text,link - default: all
#            args[2] - specific_content_tags - string_list - cat,mammal,politics - default: none =====for photos, gifs, vids use google captions ; text just look for word. 
#            args[3] - specific_subreddits - string_list - reddit:politics,news,worldnews; - default: none
#            args[4] - number_of_post_to_return - int - 10 - default: 20

#for specific subreddits loop through that list, for content type and specific content tags filter as loop through posts.

def returnTrending(subreddit, trendingPosts):

    fillers = []
    for submission in reddit.subreddit(subreddit).new(limit=75):
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
            fillers.append(Post(subreddit, author, title, score, numOfComments, permalink, diff_minutes))

    for filler in fillers:
        numberOfHotterPostsInSub = 0
        for filler2 in fillers:
           if filler.score/filler.diff_minutes > filler2.score/filler2.diff_minutes:                                              
               numberOfHotterPostsInSub = numberOfHotterPostsInSub + 1

        prediction = rfc.predict_proba([[filler.score,filler.numOfComments,filler.diff_minutes,numberOfHotterPostsInSub]])
        if len(trendingPosts) >= 15:
           if trendingPosts[14].rating < prediction[0][1]:
               trendingPosts.pop()
               trendingPosts.append(HotPost(filler.subreddit, filler.title, "http://www.reddit.com/" + filler.permalink, prediction[0][1]))
               trendingPosts.sort(key=lambda x: x.rating, reverse=True)
        else:
            trendingPosts.append(HotPost(filler.subreddit, filler.title, "http://www.reddit.com/" + filler.permalink, prediction[0][1]))
            if len(trendingPosts) == 15:
                trendingPosts.sort(key=lambda x: x.rating, reverse=True)
       
    return trendingPosts

def makePredictions(fillers, minimum_chance_to_go_viral, number_of_post_to_return):
    for filler in fillers:
        numberOfHotterPostsInSub = 0
        for filler2 in fillers:
            if filler.score/filler.diff_minutes > filler2.score/filler2.diff_minutes:                                              
                numberOfHotterPostsInSub = numberOfHotterPostsInSub + 1

        prediction = rfc.predict_proba([[filler.score,filler.numOfComments,filler.diff_minutes,numberOfHotterPostsInSub]])
        if prediction[0][1] > float(minimum_chance_to_go_viral):
            if len(trendingPosts) >= number_of_post_to_return:
                if trendingPosts[number_of_post_to_return-1].rating < prediction[0][1]:
                    trendingPosts.pop()
                    trendingPosts.append(HotPost(filler.subreddit, filler.title, "http://www.reddit.com/" + filler.permalink, prediction[0][1]))
                    trendingPosts.sort(key=lambda x: x.rating, reverse=True)
            else:
                trendingPosts.append(HotPost(filler.subreddit, filler.title, "http://www.reddit.com/" + filler.permalink, prediction[0][1]))
                if len(trendingPosts) == number_of_post_to_return:
                    trendingPosts.sort(key=lambda x: x.rating, reverse=True)  
    return trendingPosts

def getFillers(submission, fillers, subreddit):
    author = submission.author
    title = submission.title
    score = submission.score
    numOfComments = submission.num_comments
    permalink = submission.permalink
    timeCreated = submission.created_utc
    url = submission.url
    domain = submission.domain
    timeOfPost = datetime.datetime.utcfromtimestamp(timeCreated)
    timeNow = datetime.datetime.utcnow()

    diff = timeNow - timeOfPost
    diff_minutes = (diff.days * 24 * 60) + (diff.seconds/60)

    if diff_minutes == 0:
        diff_minutes = 1 
    if diff_minutes < 140:
        return fillers.append(PostAPI(subreddit, author, title, score, numOfComments, permalink, diff_minutes, url, domain, submission.selftext))

def returnTrendingAPI(minimum_chance_to_go_viral, content_type, specific_content_tags, specific_subreddits, number_of_post_to_return, trendingPosts):
    if specific_subreddits == 'none':

        subreddits_to_search = [ "pics", "politics", "worldnews", "news", "videos", "gifs"]
        if content_type == 'all':

            if specific_content_tags == 'none':

                fillers = []
                for subreddit in subreddits_to_search:
                    for submission in reddit.subreddit(subreddit).new(limit=int(number_of_post_to_return)):
                        getFillers(submission, fillers, subreddit)
                return makePredictions(fillers, minimum_chance_to_go_viral,number_of_post_to_return)
            else:

                fillers = []
                for subreddit in subreddits_to_search:
                    for submission in reddit.subreddit(subreddit).new(limit=int(number_of_post_to_return)):
                        getFillers(submission, fillers, subreddit)

                fillers2 = filter_posts_with_content_tags_and_type(fillers, specific_content_tags, content_type)
                return makePredictions(fillers2, minimum_chance_to_go_viral,number_of_post_to_return)
        else:

            if specific_content_tags == 'none':

                fillers = []
                for subreddit in subreddits_to_search:
                    for submission in reddit.subreddit(subreddit).new(limit=int(number_of_post_to_return)):
                        getFillers(submission, fillers, subreddit)
                fillers2 = filter_posts_with_content_tags_and_type(fillers, specific_content_tags, content_type)   
                return makePredictions(fillers2, minimum_chance_to_go_viral,number_of_post_to_return)
            else:

                fillers = []
                for subreddit in subreddits_to_search:
                    for submission in reddit.subreddit(subreddit).new(limit=int(number_of_post_to_return)):
                        getFillers(submission, fillers, subreddit)

                    fillers2 = filter_posts_with_content_tags_and_type(fillers, specific_content_tags, 'all')
                    fillers3 = filter_posts_with_content_tags_and_type(fillers2, 'none', content_type)# ask meownow about these lines 
                    
                    return makePredictions(fillers2, minimum_chance_to_go_viral,number_of_post_to_return)
    else:

        subreddits_to_search = specific_subreddits.split(',')
        if content_type == 'all':

            if specific_content_tags == 'none':

                fillers = []
                for subreddit in subreddits_to_search:
                    for submission in reddit.subreddit(subreddit).new(limit=int(number_of_post_to_return)):
                        getFillers(submission, fillers, subreddit)

                    return makePredictions(fillers, minimum_chance_to_go_viral,number_of_post_to_return)
            else:

                fillers = []
                for subreddit in subreddits_to_search:
                    for submission in reddit.subreddit(subreddit).new(limit=int(number_of_post_to_return)):
                        getFillers(submission, fillers, subreddit)

                fillers2 = filter_posts_with_content_tags_and_type(fillers, specific_content_tags, content_type)
                    
                return makePredictions(fillers2, minimum_chance_to_go_viral,number_of_post_to_return)
        else:

            content_types_to_search = content_type.split(",")
            if specific_content_tags == 'none':

                fillers = []
                for subreddit in subreddits_to_search:
                    for submission in reddit.subreddit(subreddit).new(limit=int(number_of_post_to_return)):
                        getFillers(submission, fillers, subreddit)

                fillers2 = filter_posts_with_content_tags_and_type(fillers, specific_content_tags, content_type)
                    
                return makePredictions(fillers2, minimum_chance_to_go_viral,number_of_post_to_return)

            else:

                fillers = []
                for subreddit in subreddits_to_search:
                    for submission in reddit.subreddit(subreddit).new(limit=int(number_of_post_to_return)):
                        getFillers(submission, fillers, subreddit)

                    fillers2 = filter_posts_with_content_tags_and_type(fillers, specific_content_tags, 'all')
                    fillers3 = filter_posts_with_content_tags_and_type(fillers2, 'none', content_type)
                    
                    return makePredictions(fillers2, minimum_chance_to_go_viral,number_of_post_to_return)




def filter_posts_with_content_tags_and_type(postsToAnalyze, content_tags_to_find, content_type_to_find):
    #check if post is gif, vid or photo - if so get tags from still with detect_labels_uri - check for words in title/text(if there) of post see if they match any content tags
    filtered_posts = []

    if content_tags_to_find != 'none' and content_type_to_find == 'all':
        matched = False
        content_tags_to_find_list = content_tags_to_find.split(',')
        for cc in content_tags_to_find_list:
            print(cc)
        for post_to_analyzie in postsToAnalyze:
            title_list =  post_to_analyzie.title.split(' ')
            

            for word_in_title in title_list:
                for content_tag in content_tags_to_find_list:
                    if word_in_title == content_tag:
                        matched = True
                        filtered_posts.append(post_to_analyzie)
                        break
                if matched == True:
                    break
            if matched == True:
                matched = False
                pass

            file_format = post_to_analyzie.url[-4:]
            if file_format == '.jpg' or file_format == '.png':
                contentTags = detect_labels_uri(post_to_analyzie.url)

                for content_tag_to_find in content_tags_to_find_list:
                    for tag in contentTags:
                        print(tag)
                        if tag == content_tag_to_find:
                            matched = True
                            filtered_posts.append(post_to_analyzie)
                            break
                    if matched == True:
                        break
                if matched == True:
                    matched = False
                    pass
            #print("is image")
                kindOfPost = "image"
            elif post_to_analyzie.domain == "youtube.com" or post_to_analyzie.domain == "youtu.be" or post_to_analyzie.domain == "worldstarhiphop.com" or post_to_analyzie.domain == "viralvideos.club" or post_to_analyzie.domain == "m.worldstarhiphop.com" or post_to_analyzie.domain == "hulu.com" or post_to_analyzie.domain == "liveleak.com" or post_to_analyzie.domain == "vimeo.com" or post_to_analyzie.domain == "streamable.com" or post_to_analyzie.domain == "twitch.com" or post_to_analyzie.domain == "clips.twitch.tv" or post_to_analyzie.domain == "123hulu.com":
            #print("is video")
                kindOfPost = "video"
                if post_to_analyzie.domain == "youtube.com" or post_to_analyzie.domain == "youtu.be":
                    video_id = get_video_id(post_to_analyzie.url)
                    thumnail_url = "http://img.youtube.com/vi/%s/0.jpg" % video_id
                    contentTags = detect_labels_uri(thumnail_url)

                    for content_tag_to_find in content_tags_to_find_list:
                        for tag in contentTags:
                            if tag == content_tag_to_find:
                                matched = True
                                filtered_posts.append(post_to_analyzie)
                                break
                        if matched == True:
                            break
                    if matched == True:
                        matched = False
                        pass
                elif post_to_analyzie.domain == "worldstarhiphop.com" or post_to_analyzie.domain == "m.worldstarhiphop.com":
                    page = requests.get(post_to_analyzie.url)
                    tree = html.fromstring(page.content)
                    thumbnailURL = tree.xpath('//*[@id="main"]/div[2]/article/div[2]/link[2]/@href')
                    if len(thumbnailURL) > 0:
                        contentTags = detect_labels_uri(thumbnailURL[0])
                        for content_tag_to_find in content_tags_to_find_list:
                            for tag in contentTags:
                                if tag == content_tag_to_find:
                                    matched = True
                                    filtered_posts.append(post_to_analyzie)
                                    break
                            if matched == True:
                                break
                        if matched == True:
                            matched = False
                            pass
            elif post_to_analyzie.selftext != "":
                kindOfPost = "text"
            elif post_to_analyzie.url[-4:] == ".gif" or post_to_analyzie.url[-5:] == ".gifv" or post_to_analyzie.domain == "gfycat.com":
                contentTags = detect_labels_uri(post_to_analyzie.url)
                for content_tag_to_find in content_tags_to_find_list:
                    for tag in contentTags:
                        if tag == content_tag_to_find:
                            matched = True
                            filtered_posts.append(post_to_analyzie)
                            break
                    if matched == True:
                        break
                if matched == True:
                    matched = False
                    pass
                kindOfPost = "gif"
            elif post_to_analyzie.domain == "imgur.com" or post_to_analyzie.domain == "i.imgur.com":
                if post_to_analyzie.domain == "imgur.com":
                    if post_to_analyzie.url[4] == 's':
                        new_url = post_to_analyzie.url[:8] + 'i.' + post_to_analyzie.url[8:]
                        try:
                            content_type = requests.head(new_url + ".jpg").headers['Content-Type']
                            if content_type == 'image/jpeg':
                                kindOfPost = "image"
                                contentTags = detect_labels_uri(new_url + ".jpg")
                                for content_tag_to_find in content_tags_to_find_list:
                                    for tag in contentTags:
                                        if tag == content_tag_to_find:
                                            matched = True
                                            filtered_posts.append(post_to_analyzie)
                                            break
                                    if matched == True:
                                        break
                                if matched == True:
                                    matched = False
                                    pass
                            elif content_type == 'image/gif':
                                kindOfPost = "gif"
                                contentTags = detect_labels_uri(new_url + ".jpg")
                                for content_tag_to_find in content_tags_to_find_list:
                                    for tag in contentTags:
                                        if tag == content_tag_to_find:
                                            matched = True
                                            filtered_posts.append(post_to_analyzie)
                                            break
                                    if matched == True:
                                        break
                                if matched == True:
                                    matched = False
                                    pass
                            else:
                                kindOfPost = "link"
                        except KeyError:
                            kindOfPost = "link"
                    elif post_to_analyzie.url[4] != 's':
                        new_url = post_to_analyzie.url[:7] + 'i.' + post_to_analyzie.url[7:]
                        try:
                            content_type = requests.head(new_url + ".jpg").headers['Content-Type']
                            if content_type == 'image/jpeg':
                                kindOfPost = "image"
                                contentTags = detect_labels_uri(new_url + ".jpg")
                                for content_tag_to_find in content_tags_to_find_list:
                                    for tag in contentTags:
                                        if tag == content_tag_to_find:
                                            matched = True
                                            filtered_posts.append(post_to_analyzie)
                                            break
                                    if matched == True:
                                        break
                                if matched == True:
                                    matched = False
                                    pass
                            elif content_type == 'image/gif':
                                kindOfPost = "gif"
                                contentTags = detect_labels_uri(new_url + ".jpg")
                                for content_tag_to_find in content_tags_to_find_list:
                                    for tag in contentTags:
                                        if tag == content_tag_to_find:
                                            matched = True
                                            filtered_posts.append(post_to_analyzie)
                                            break
                                    if matched == True:
                                        break
                                if matched == True:
                                    matched = False
                                    pass
                            else:
                                kindOfPost = "link"
                        except KeyError:
                            kindOfPost = "link"
                elif post_to_analyzie.domain == "i.imgur.com":
                    new_url = post_to_analyzie.url[:7] + 'i.' + post_to_analyzie.url[7:]
                    try:
                        content_type = requests.head(post_to_analyzie.url + ".jpg").headers['Content-Type']
                        if content_type == 'image/jpeg':
                            kindOfPost = "image"
                            contentTags = detect_labels_uri(new_url + ".jpg")
                            for content_tag_to_find in content_tags_to_find_list:
                                for tag in contentTags:
                                    if tag == content_tag_to_find:
                                        matched = True
                                        filtered_posts.append(post_to_analyzie)
                                        break
                                if matched == True:
                                    break
                            if matched == True:
                                matched = False
                                pass
                        elif content_type == 'image/gif':
                            kindOfPost = "gif"
                            contentTags = detect_labels_uri(new_url + ".jpg")
                            for content_tag_to_find in content_tags_to_find_list:
                                for tag in contentTags:
                                    if tag == content_tag_to_find:
                                        matched = True
                                        filtered_posts.append(post_to_analyzie)
                                        break
                                if matched == True:
                                    break
                            if matched == True:
                                matched = False
                                pass
                        else:
                            kindOfPost = "link"
                    except KeyError:
                        kindOfPost = "link"
            else:
                kindOfPost = "link"
        return filtered_posts
    elif content_tags_to_find == 'none' and content_type_to_find != 'all':
        matched = False
        content_types_to_find_list = content_type_to_find.split(',')
        for post_to_analyzie in postsToAnalyze:
            title_list =  post_to_analyzie.title.split(' ')

            file_format = post_to_analyzie.url[-4:]

            if file_format == '.jpg' or file_format == '.png':
                kindOfPost = "image"
                for content_type_to_find in content_types_to_find_list:
                    if content_type_to_find == kindOfPost:
                        matched = True
                        filtered_posts.append(post_to_analyzie)
                        break
                if matched == True:
                    matched = False
                    pass
            #print("is image")
            elif post_to_analyzie.domain == "youtube.com" or post_to_analyzie.domain == "youtu.be" or post_to_analyzie.domain == "worldstarhiphop.com" or post_to_analyzie.domain == "viralvideos.club" or post_to_analyzie.domain == "m.worldstarhiphop.com" or post_to_analyzie.domain == "hulu.com" or post_to_analyzie.domain == "liveleak.com" or post_to_analyzie.domain == "vimeo.com" or post_to_analyzie.domain == "streamable.com" or post_to_analyzie.domain == "twitch.com" or post_to_analyzie.domain == "clips.twitch.tv" or post_to_analyzie.domain == "123hulu.com":
            #print("is video")
                kindOfPost = "video"
                for content_type_to_find in content_types_to_find_list:
                    if content_type_to_find == kindOfPost:
                        matched = True
                        filtered_posts.append(post_to_analyzie)
                        break
                if matched == True:
                    matched = False
                    pass
            elif post_to_analyzie.selftext != "":
                kindOfPost = "text"
                for content_type_to_find in content_types_to_find_list:
                    if content_type_to_find == kindOfPost:
                        matched = True
                        filtered_posts.append(post_to_analyzie)
                        break
                if matched == True:
                    matched = False
                    pass
            elif post_to_analyzie.url[-4:] == ".gif" or post_to_analyzie.url[-5:] == ".gifv" or post_to_analyzie.domain == "gfycat.com":
                kindOfPost = "gif"
                for content_type_to_find in content_types_to_find_list:
                    if content_type_to_find == kindOfPost:
                        matched = True
                        filtered_posts.append(post_to_analyzie)
                        break
                if matched == True:
                    matched = False
                    pass
            elif post_to_analyzie.domain == "imgur.com" or post_to_analyzie.domain == "i.imgur.com":
                if post_to_analyzie.domain == "imgur.com":
                    if post_to_analyzie.url[4] == 's':
                        new_url = post_to_analyzie.url[:8] + 'i.' + post_to_analyzie.url[8:]
                        try:
                            content_type = requests.head(new_url + ".jpg").headers['Content-Type']
                            if content_type == 'image/jpeg':
                                kindOfPost = "image"
                                for content_type_to_find in content_types_to_find_list:
                                    if content_type_to_find == kindOfPost:
                                        matched = True
                                        filtered_posts.append(post_to_analyzie)
                                        break
                                if matched == True:
                                    matched = False
                                    pass
                            elif content_type == 'image/gif':
                                kindOfPost = "gif"
                                for content_type_to_find in content_types_to_find_list:
                                    if content_type_to_find == kindOfPost:
                                        matched = True
                                        filtered_posts.append(post_to_analyzie)
                                        break
                                if matched == True:
                                    matched = False
                                    pass
                            else:
                                kindOfPost = "link"
                                for content_type_to_find in content_types_to_find_list:
                                    if content_type_to_find == kindOfPost:
                                        matched = True
                                        filtered_posts.append(post_to_analyzie)
                                        break
                                if matched == True:
                                    matched = False
                                    pass
                        except KeyError:
                            kindOfPost = "link"
                            for content_type_to_find in content_types_to_find_list:
                                if content_type_to_find == kindOfPost:
                                    matched = True
                                    filtered_posts.append(post_to_analyzie)
                                    break
                            if matched == True:
                                matched = False
                                pass
                    elif post_to_analyzie.url[4] != 's':
                        new_url = post_to_analyzie.url[:7] + 'i.' + post_to_analyzie.url[7:]
                        try:
                            content_type = requests.head(new_url + ".jpg").headers['Content-Type']
                            if content_type == 'image/jpeg':
                                kindOfPost = "image"
                                for content_type_to_find in content_types_to_find_list:
                                    if content_type_to_find == kindOfPost:
                                        matched = True
                                        filtered_posts.append(post_to_analyzie)
                                        break
                                if matched == True:
                                    matched = False
                                    pass
                            elif content_type == 'image/gif':
                                kindOfPost = "gif"
                                for content_type_to_find in content_types_to_find_list:
                                    if content_type_to_find == kindOfPost:
                                        matched = True
                                        filtered_posts.append(post_to_analyzie)
                                        break
                                if matched == True:
                                    matched = False
                                    pass
                            else:
                                kindOfPost = "link"
                                for content_type_to_find in content_types_to_find_list:
                                    if content_type_to_find == kindOfPost:
                                        matched = True
                                        filtered_posts.append(post_to_analyzie)
                                        break
                                if matched == True:
                                    matched = False
                                    pass
                        except KeyError:
                            kindOfPost = "link"
                            for content_type_to_find in content_types_to_find_list:
                                if content_type_to_find == kindOfPost:
                                    matched = True
                                    filtered_posts.append(post_to_analyzie)
                                    break
                            if matched == True:
                                matched = False
                                pass
                elif post_to_analyzie.domain == "i.imgur.com":
                    try:
                        content_type = requests.head(post_to_analyzie.url + ".jpg").headers['Content-Type']
                        if content_type == 'image/jpeg':
                            kindOfPost = "image"
                            for content_type_to_find in content_types_to_find_list:
                                if content_type_to_find == kindOfPost:
                                    matched = True
                                    filtered_posts.append(post_to_analyzie)
                                    break
                            if matched == True:
                                matched = False
                                pass
                        elif content_type == 'image/gif':
                            kindOfPost = "gif"
                            for content_type_to_find in content_types_to_find_list:
                                if content_type_to_find == kindOfPost:
                                    matched = True
                                    filtered_posts.append(post_to_analyzie)
                                    break
                            if matched == True:
                                matched = False
                                pass
                        else:
                            kindOfPost = "link"
                            for content_type_to_find in content_types_to_find_list:
                                if content_type_to_find == kindOfPost:
                                    matched = True
                                    filtered_posts.append(post_to_analyzie)
                                    break
                            if matched == True:
                                matched = False
                                pass
                    except KeyError:
                        kindOfPost = "link"
                        for content_type_to_find in content_types_to_find_list:
                            if content_type_to_find == kindOfPost:
                                matched = True
                                filtered_posts.append(post_to_analyzie)
                                break
                        if matched == True:
                            matched = False
                            pass
            else:
                kindOfPost = "link"
                for content_type_to_find in content_types_to_find_list:
                    if content_type_to_find == kindOfPost:
                        matched = True
                        filtered_posts.append(post_to_analyzie)
                        break
                if matched == True:
                    matched = False
                    pass
        return filtered_posts

def detect_labels_uri(uri):
    #vision_client = vision.Client()
    vision_client = vision.Client.from_service_account_json("/Users/mark/Downloads/viralai-master/ViralAI-123c69d3bd0b.json")
    image = vision_client.image(source_uri=uri)
    labels = image.detect_labels()
    #print('Labels:')
    localLabels = []
    for label in labels:
        localLabels.append(label.description)
    return localLabels

