from django.urls import path
from . import views
from .feeds import LatestSongsFeed

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('send-inn-favoritt/<str:unique_url>/', views.submit_song, name='submit_song'),
    path('<str:musician_slug>/<slug:song_slug>/', views.favourite_song, name='favourite_song'),
    path('vilkaar/', views.terms, name='terms'),
    path('liste/', views.musician_list, name='musician_list'),
    path('kontakt/', views.contact, name='contact'),
    path('lenker/', views.links, name='links'),
    path('rss/', LatestSongsFeed(), name='rss_feed'),
]