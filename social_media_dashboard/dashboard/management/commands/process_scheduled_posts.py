from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import SocialMediaPost
import tweepy
import facebook
from django.conf import settings

class Command(BaseCommand):
    help = 'Process scheduled social media posts'

    def handle(self, *args, **options):
        now = timezone.now()
        posts = SocialMediaPost.objects.filter(posted=False, scheduled_time__lte=now)

        for post in posts:
            try:
                if post.platform == 'twitter':
                    auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
                    auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
                    api = tweepy.API(auth)
                    api.update_status(post.text)
                    post.posted = True
                    post.save()
                    self.stdout.write(self.style.SUCCESS(f"Posted {post.id} to Twitter"))
                elif post.platform == 'facebook':
                    graph = facebook.GraphAPI(settings.FACEBOOK_ACCESS_TOKEN)
                    graph.put_object(parent_object='me', connection_name='feed', message=post.text)
                    post.posted = True
                    post.save()
                    self.stdout.write(self.style.SUCCESS(f"Posted {post.id} to Facebook"))
            except Exception as e:
                self.stderr.write(f"Error posting {post.id}: {str(e)}")