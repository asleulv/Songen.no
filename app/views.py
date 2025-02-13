from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import ContactForm
from django.core.paginator import Paginator
from django.conf import settings
from django.core.mail import send_mail
from .models import Musician, Song, StreamingLink, SocialLink, SongSubmission, SiteLink
from .forms import SongSubmissionForm

def frontpage(request):
    latest_songs = Song.objects.select_related('musician').order_by('-id')
    paginator = Paginator(latest_songs, 6)  # Show 6 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'frontpage.html', {'page_obj': page_obj})

def musician_list(request):
    musicians = Musician.objects.filter(song__isnull=False).order_by('name')

    search_query = request.GET.get('search', '')
    if search_query:
        musicians = musicians.filter(
            Q(name__icontains=search_query) | 
            Q(bands__name__icontains=search_query)
        ).distinct()

    total_musicians = musicians.count()

    return render(request, 'musician_list.html', {'musicians': musicians, 'total_musicians': total_musicians})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            send_mail(
                f'Contact form message from {name}',
                message,
                email,
                [settings.CONTACT_EMAIL],  
            )
            return render(request, 'contact_success.html')  
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})

def links(request):
    sitelinks = SiteLink.objects.all()
    return render(request, 'links.html',{'sitelinks': sitelinks})

def terms(request):
    return render(request, 'terms.html')

def favourite_song(request, musician_slug, song_slug):
    # Fetch the musician by slug
    musician = get_object_or_404(Musician, slug=musician_slug)
    
    # Fetch the song by slug and ensure it belongs to the correct musician
    favorite_song = get_object_or_404(Song, slug=song_slug, musician=musician)

    # Use IDs for any further processing if needed
    musician_id = musician.id
    song_id = favorite_song.id

    # Fetch related streaming and social links
    streaming_links = StreamingLink.objects.filter(song_id=song_id)
    social_links = SocialLink.objects.filter(musician_id=musician_id)

    bands = musician.bands.all()
    
    return render(request, 'favourite_song.html', {
        'musician': musician,
        'favorite_song': favorite_song,
        'streaming_links': streaming_links,
        'social_links': social_links,
        'bands': bands, 
    })


def submit_song(request, unique_url):
    submission = get_object_or_404(SongSubmission, unique_url=unique_url)
    
    # Explicitly get the musician
    musician = submission.musician

    if submission.approved:
        return render(request, 'submission_success.html', {'submission': submission})

    if request.method == 'POST':
        form = SongSubmissionForm(
            request.POST, 
            instance=submission, 
            musician=musician  # Explicitly pass musician
        )
        
        print("VIEW - POST Data:", request.POST)

        if form.is_valid():
            print("VIEW - Form is valid")
            form.save()

            # Refresh to verify
            musician.refresh_from_db()
            print("VIEW - After save - Musician name:", musician.name)
            print("VIEW - After save - Musician bio:", musician.bio)

            return render(request, 'submission_success.html')
        else:
            print("VIEW - Form errors:", form.errors)
    else:
        form = SongSubmissionForm(
            instance=submission, 
            musician=musician  # Explicitly pass musician
        )

    return render(request, 'submit_song.html', {
        'form': form, 
        'submission': submission, 
        'musician': musician
    })







