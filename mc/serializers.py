from rest_framework import serializers

class CommentSerializer(serializers.Serializer):
    subreddit = serializers.CharField(max_length=200, required=False)
    author = serializers.CharField(max_length=200, required=False)
    title = serializers.CharField(max_length=200, required=False)
    score = serializers.FloatField(required=False)
    numOfComments = serializers.FloatField(required=False)
    permalink = serializers.URLField(max_length=200, min_length=None, required=False)
    diff_minutes = serializers.FloatField(required=False)
    rating = serializers.FloatField(required=False)
