from django.contrib.syndication.views import Feed
from datetime import datetime
from django.utils import timezone
from .models import Song 

class LatestSongsFeed(Feed):
    title = "Songen.no"
    link = "/rss/"
    description = "Siste songar på Songen.no"

    def items(self):
        # Get the latest 10 songs, but return the related musician instead of song details
        return Song.objects.all().order_by('-created_at')[:10]

    def item_title(self, item):
        # Title should be the musician's name, not the song's title
        return item.musician.name

    def item_description(self, item):
        # Description should be the musician's bio, not the song's text
        return item.musician.bio

    def item_pubdate(self, item):
        # Ensure created_at is a datetime object (if it's a string, convert it)
        if isinstance(item.created_at, str):
            item.created_at = datetime.fromisoformat(item.created_at)
                
        # Make sure the datetime is timezone-aware
        if timezone.is_naive(item.created_at):
            item.created_at = timezone.make_aware(item.created_at, timezone.get_current_timezone())
                
        # Convert to the local time zone
        local_time = timezone.localtime(item.created_at)
        
        # Return the datetime object, not the formatted string
        return local_time