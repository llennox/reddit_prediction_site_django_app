from django import forms
from django.core.validators import EmailValidator

class EmailNewPass(forms.Form):
    aemail = forms.EmailField(required=True,label="",widget=forms.EmailInput(attrs={'placeholder': 'Email','class':'form-control input-perso','id':'email_input'}),max_length=100,error_messages={'invalid': ("Email invalid")},validators=[EmailValidator])

class subs(forms.Form):
    Choices = (
            ("AskReddit,funny,explainlikeimfive,mildlyinteresting,showerthoughts,music,pics,jokes", "popular defaults"),
            ("Art","Art"),
            ("AskReddit","AskReddit"),
("askscience","askscience"),
("aww","aww"),
("books","books"),
("creepy","creepy"),
("dataisbeautiful","dataisbeautiful"),
("DIY","DIY"),
("Documentaries","Documentaries"),
("EarthPorn","EarthPorn"),
("explainlikeimfive","explainlikeimfive"),
("food","food"),
("funny","funny"),
("gaming","gaming"),
("gifs","gifs"),
("history","history"),
("jokes","jokes"),
("LifeProTips","LifeProTips"),
("movies","movies"),
("music","music"),
("pics","pics"),
("science","science"),
("ShowerThoughts","ShowerThoughts"),
("space","space"),
("sports","sports"),
("tifu","tifu"),
("todayilearned","todayilearned"),
("videos","videos"),
("worldnews","worldnews"),
            )
    subreddits = forms.ChoiceField(choices=Choices,widget=forms.Select(attrs={'class':'btn btn-primary btn-round product-btn dropdown'}))

class Usersubs(forms.Form):
    Choices = (
("AskReddit,funny,explainlikeimfive,mildlyinteresting,showerthoughts,music,pics,jokes", "popular defaults"),
("politics,the_donald,news,worldnews,sandersforpresident,Libertarian", "political"),
("sports,nba,soccer,olympics,MLS,hockey,Tennis,Golf,mlb", "sports"),
("bitcoin,technology,programming,gaming,gadgets,android,apple", "tech"),
("pics,videos,dataisbeautiful,aww,food,oldschoolcool,earth_porn,wholesomememes", "visual media"),
            )
    subreddits = forms.ChoiceField(choices=Choices,widget=forms.Select(attrs={'class':'btn btn-primary btn-round product-btn dropdown'}))
