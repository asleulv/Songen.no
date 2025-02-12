import os
import uuid
from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django import forms
from dotenv import load_dotenv
from .models import Musician, SocialLink, Song, StreamingLink, Band, SongSubmission, SiteLink

load_dotenv() 
BASE_URL = os.getenv('PROD_URL') if os.getenv('DJANGO_ENV') == 'production' else os.getenv('DEV_URL')


# Inline configuration for SocialLink
class SocialLinkInline(admin.TabularInline):  
    model = SocialLink
    extra = 1  # Number of empty forms to display
    fields = ('description', 'url')  # Display only relevant fields
    show_change_link = True  # Adds a link to edit the related object


# Inline configuration for StreamingLink
class StreamingLinkInline(admin.TabularInline):
    model = StreamingLink
    extra = 1  # Number of empty forms to display
    fields = ('name', 'url')  # Display platform and URL
    show_change_link = True  # Adds a link to edit the related object

# Inline configuration for Musicians in Band Admin
class MusicianInline(admin.TabularInline):
    model = Musician.bands.through  # Use the through table for ManyToManyField
    extra = 1  # Number of empty forms to display
    verbose_name = "Band Member"
    verbose_name_plural = "Band Members"

# Musician Admin with SocialLink Inline
@admin.register(Musician)
class MusicianAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')  
    search_fields = ('name',)  
    inlines = [SocialLinkInline]  # Add MusicianInline

@admin.register(SiteLink)
class SiteLinksAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'url')  
    search_fields = ('name', 'description')  
    list_filter = ('name',)  
    

# Band Admin
@admin.register(Band)
class BandAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display only the band name
    search_fields = ('name',)  # Allow searching by band name

class SongSubmissionAdminForm(forms.ModelForm):
    class Meta:
        model = SongSubmission
        fields = ['musician']  # Only include musician for initial submission

    # Make song fields optional (you can leave them blank during initial creation)
    song_title = forms.CharField(required=False)
    song_artist = forms.CharField(required=False)
    reasoning = forms.CharField(widget=forms.Textarea, required=False)

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure musician is selected
        if not cleaned_data.get('musician'):
            raise forms.ValidationError("Musician is required")
        
        return cleaned_data

@admin.register(SongSubmission)
class SongSubmissionAdmin(admin.ModelAdmin):
    list_display = ('musician', 'copy_submission_url', 'approved', 'submitted_at')
    list_filter = ('approved',)
    actions = ['approve_selected', 'generate_unique_url']  # Custom actions for approval and URL regeneration
    
    # Exclude 'approved' field from the detail view (form view)
    exclude = ('approved',)  # Exclude 'approved' field from the admin form view.

    def copy_submission_url(self, obj):
        full_url = obj.get_full_url()
        return format_html(
            '<input type="text" value="{}" id="url_{}" readonly style="width:150px;">'
            '<button onclick="navigator.clipboard.writeText(document.getElementById(\'url_{}\').value)">📋 Copy</button>',
            full_url, obj.id, obj.id
        )
    
    copy_submission_url.short_description = 'Submission URL'

    def approve_selected(self, request, queryset):
        """Approve the selected submissions and create Songs."""
        for submission in queryset:
            if not submission.approved:
                submission.approve_submission()  # Calls the approve_submission method from the model
                self.message_user(request, f"Submission by {submission.musician} has been approved.")
            else:
                # Unapprove and delete the song if it's approved
                submission.unapprove_submission()
                self.message_user(request, f"Submission by {submission.musician} has been unapproved.")
        return redirect(request.META.get('HTTP_REFERER', 'admin:song_submission_changelist'))

    approve_selected.short_description = 'Approve/Unapprove Selected Submissions'

    def generate_unique_url(self, request, queryset):
        """Regenerates unique URLs for selected submissions."""
        for submission in queryset:
            submission.unique_url = uuid.uuid4()  # Generate a new unique URL if needed
            submission.save()
        self.message_user(request, "Unique URLs have been regenerated.")

    generate_unique_url.short_description = "Regenerate Unique URL for selected submissions"

    def save_model(self, request, obj, form, change):
        """Ensures unique_url is always generated when saving."""
        if not obj.unique_url:
            obj.unique_url = uuid.uuid4()  # Generate unique URL if not already set
        obj.save()

# Song Admin with StreamingLink Inline
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'year', 'get_musician', 'slug') 
    list_filter = ('year',)  
    search_fields = ('title', 'artist', 'album')  
    inlines = [StreamingLinkInline]  
    readonly_fields = ('slug',) 

    def get_musician(self, obj):
        return format_html('<a href="/admin/app/musician/{}/change/">{}</a>', 
                           obj.musician.id, obj.musician.name)  
    get_musician.short_description = 'Favourite of'


