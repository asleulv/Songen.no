import os
import re
from django.db import models
from PIL import Image
from django.utils.text import slugify
from django.urls import reverse
import io
import uuid
from dotenv import load_dotenv
from django.core.files.uploadedfile import InMemoryUploadedFile

load_dotenv()
BASE_URL = os.getenv('PROD_URL') if os.getenv('DJANGO_ENV') == 'production' else os.getenv('DEV_URL')

class Band(models.Model):
    name = models.CharField(max_length=200, unique=True)
    hashtag = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.hashtag:
            # Generate hashtag from the band name (remove spaces and lowercase)
            cleaned_name = re.sub(r'\s+', '', self.name.lower())
            self.hashtag = f"{cleaned_name}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Musician(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField()
    picture = models.ImageField(upload_to='musician_pics/', blank=True, null=True)
    picture_credit = models.CharField(max_length=255, blank=True, null=True)  # New field for picture credit
    slug = models.SlugField(blank=True)
    bands = models.ManyToManyField(Band, related_name='members', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Automatically create the slug from the name

        if self.picture:  # If a picture is uploaded
            img = Image.open(self.picture)
            img_format = img.format.lower()

            # Resize the image if it's larger than a certain width/height (optional)
            max_width = 800  # max width for images
            max_height = 800  # max height for images

            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)  # Use LANCZOS for high-quality resizing

            # Save image to an in-memory file
            image_io = io.BytesIO()
            img.save(image_io, format=img_format)
            image_io.seek(0)

            # Infer content type based on the file name (fallback to 'image/jpeg' if unsure)
            file_extension = self.picture.name.split('.')[-1].lower()
            content_type = f"image/{file_extension}" if file_extension in ['jpeg', 'png', 'gif'] else 'image/jpeg'

            # Save the compressed image back to the model field
            self.picture = InMemoryUploadedFile(
                image_io, None, self.picture.name, content_type, image_io.tell(), None
            )

        super().save(*args, **kwargs)  # Call the original save method

    def __str__(self):
        return self.name


class SocialLink(models.Model):
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE, related_name='social_links')
    description = models.CharField(max_length=200)  # Add a description field for the social link
    url = models.URLField()  # The URL of the social media or website link

    def __str__(self):
        return f"{self.musician.name} - {self.description}"

class Song(models.Model):
    musician = models.OneToOneField(Musician, on_delete=models.CASCADE)  # Link the Song to a Musician
    artist = models.CharField(max_length=200)  # Artist name of the song
    title = models.CharField(max_length=200)
    text = models.TextField()
    year = models.PositiveIntegerField(null=True, blank=True)
    album = models.CharField(max_length=200, blank=True, null=True)  # Not required
    image = models.ImageField(upload_to='song_images/', blank=True, null=True)  # Not required
    slug = models.SlugField(unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Create a combined slug for artist and title
        self.slug = slugify(f"{self.artist} {self.title}")
        super(Song, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('favourite_song', kwargs={'musician_slug': self.musician.slug, 'song_slug': self.slug})

    def __str__(self):
        return f'{self.title} by {self.artist} ({self.year})'
    
class StreamingLink(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='streaming_links')
    name = models.CharField(max_length=100)  # Name of the streaming platform or service
    url = models.URLField()  # URL of the streaming link

    def __str__(self):
        return f"{self.song.title} - {self.name}"
    

class SongSubmission(models.Model):
    musician = models.OneToOneField(Musician, on_delete=models.CASCADE)  # Ensure one submission per musician
    song_title = models.CharField(max_length=255, blank=True)
    song_artist = models.CharField(max_length=255, blank=True)
    reasoning = models.TextField(blank=True)
    unique_url = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  # New field to track approval status

    def get_full_url(self):
        return f"{BASE_URL}/send-inn-favoritt/{self.unique_url}/"
    
    def approve_submission(self):
        if not self.approved:
            print(f"Approving submission for {self.musician.name}, Song: {self.song_title}")  # Debug output
            
            # Create the Song instance
            song = Song.objects.create(
                musician=self.musician,
                artist=self.song_artist,
                title=self.song_title,
                text=self.reasoning
            )

            print(f"Song created: {song}")  # Debug output to check if song is created
            
            # Mark submission as approved and save
            self.approved = True
            self.save()
            
            print("Submission approved and saved.")  # Debug output for submission approval

    def unapprove_submission(self):
        """Unapprove and delete the associated Song."""
        if self.approved:
            # Delete the associated Song instance
            Song.objects.filter(musician=self.musician, title=self.song_title).delete()
            self.approved = False
            self.save()

    def __str__(self):
        return f"Submission by {self.musician.name}"
    
class SiteLink(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()  
    url = models.URLField()

    def __str__(self):
        return f"{self.name} - {self.description}"
    


