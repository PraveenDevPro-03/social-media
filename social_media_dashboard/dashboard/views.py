from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SocialMediaPost, Profile
from .forms import ProfileForm
import tweepy
import facebook
from django.conf import settings
from datetime import datetime
from django.utils import timezone
from django.contrib import messages

def get_twitter_client():
    return tweepy.Client(
        consumer_key=settings.TWITTER_CONSUMER_KEY,
        consumer_secret=settings.TWITTER_CONSUMER_SECRET,
        access_token=settings.TWITTER_ACCESS_TOKEN,
        access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
    )

@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    twitter_posts = []
    facebook_posts = []
    scheduled_posts = SocialMediaPost.objects.filter(user=request.user, posted=False)

    if profile.twitter_handle:
        try:
            twitter_client = get_twitter_client()
            # Fetch authenticated user's tweets
            user = twitter_client.get_me().data
            twitter_posts = twitter_client.get_users_tweets(id=user.id, max_results=10).data or []
        except Exception as e:
            messages.error(request, f"Twitter fetch error: {str(e)}")

    if profile.facebook_token:
        try:
            graph = facebook.GraphAPI(profile.facebook_token)
            facebook_posts = graph.get_connections(id='me', connection_name='posts', limit=10)['data']
        except Exception as e:
            messages.error(request, f"Facebook fetch error: {str(e)}")

    if request.method == 'POST':
        platform = request.POST.get('platform')
        post_text = request.POST.get('post_text')
        schedule_time_str = request.POST.get('schedule_time')

        if not post_text:
            messages.error(request, "Post content cannot be empty.")
        else:
            post = SocialMediaPost.objects.create(
                user=request.user,
                platform=platform,
                text=post_text,
                posted=False
            )

            if schedule_time_str and schedule_time_str.strip():
                try:
                    schedule_time = datetime.strptime(schedule_time_str, '%Y-%m-%dT%H:%M')
                    schedule_time = timezone.make_aware(schedule_time)
                    if schedule_time > timezone.now():
                        post.scheduled_time = schedule_time
                        post.save()
                        messages.success(request, "Post scheduled successfully!")
                    else:
                        post.delete()
                        messages.error(request, "Schedule time must be in the future.")
                except ValueError:
                    post.delete()
                    messages.error(request, "Invalid date format.")
            else:
                try:
                    if platform == 'twitter':
                        twitter_client = get_twitter_client()
                        twitter_client.create_tweet(text=post_text)
                        post.posted = True
                        post.save()
                        messages.success(request, "Posted to Twitter!")
                    elif platform == 'facebook' and profile.facebook_token:
                        graph = facebook.GraphAPI(profile.facebook_token)
                        graph.put_object(parent_object='me', connection_name='feed', message=post_text)
                        post.posted = True
                        post.save()
                        messages.success(request, "Posted to Facebook!")
                except Exception as e:
                    post.delete()
                    messages.error(request, f"Posting error: {str(e)}")

    context = {
        'profile': profile,
        'twitter_posts': twitter_posts,
        'facebook_posts': facebook_posts,
        'scheduled_posts': scheduled_posts,
    }
    return render(request, 'dashboard.html', context)

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    twitter_posts = []

    if profile.twitter_handle:
        try:
            twitter_client = get_twitter_client()
            # Fetch authenticated user's tweets
            user = twitter_client.get_me().data
            twitter_posts = twitter_client.get_users_tweets(id=user.id, max_results=10).data or []
        except Exception as e:
            messages.error(request, f"Twitter fetch error: {str(e)}")

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'twitter_posts': twitter_posts,
    }
    return render(request, 'profile.html', context)

@login_required
def like_post(request):
    if request.method == 'POST':
        platform = request.POST.get('platform')
        post_id = request.POST.get('post_id')
        profile = Profile.objects.get(user=request.user)

        try:
            if platform == 'twitter':
                twitter_client = get_twitter_client()
                twitter_client.like(tweet_id=post_id)
                messages.success(request, "Post liked on Twitter!")
            elif platform == 'facebook' and profile.facebook_token:
                graph = facebook.GraphAPI(profile.facebook_token)
                graph.put_like(object_id=post_id)
                messages.success(request, "Post liked on Facebook!")
        except Exception as e:
            messages.error(request, f"Error liking post: {str(e)}")

    return redirect('dashboard')