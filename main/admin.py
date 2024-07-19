from django.contrib import admin
from .models import playlist_user, playlist_song, SubscriptionPlan, UserSubscription

admin.site.register(playlist_user)
admin.site.register(playlist_song)
admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
