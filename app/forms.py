from django import forms
from .models import SongSubmission

class SongSubmissionForm(forms.ModelForm):
    class Meta:
        model = SongSubmission
        fields = ['musician', 'song_title', 'song_artist', 'reasoning']
        widgets = {
            'musician': forms.HiddenInput(),
        }

    name = forms.CharField(max_length=255, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        musician = kwargs.pop('musician', None)
        super().__init__(*args, **kwargs)

        if musician:
            # Store original musician details
            self._original_name = musician.name
            self._original_bio = musician.bio

            # Set initial data for both bound and unbound forms
            if self.is_bound:
                # For POST requests, use submitted data or fall back to original
                self.data = self.data.copy()
                if 'name' not in self.data:
                    self.data['name'] = musician.name
                if 'bio' not in self.data:
                    self.data['bio'] = musician.bio
            else:
                # For GET requests, set initial values
                self.fields['name'].initial = musician.name
                self.fields['bio'].initial = musician.bio

    def clean(self):
        cleaned_data = super().clean()
        
        # Preserve original values if fields are empty
        if hasattr(self, '_original_name'):
            if not cleaned_data.get('name'):
                cleaned_data['name'] = self._original_name
        
        if hasattr(self, '_original_bio'):
            if not cleaned_data.get('bio'):
                cleaned_data['bio'] = self._original_bio
        
        return cleaned_data

    def save(self, commit=True):
        song_submission = super().save(commit=False)
        musician = song_submission.musician

        # Update musician details
        musician.name = self.cleaned_data.get('name', self._original_name)
        musician.bio = self.cleaned_data.get('bio', self._original_bio)
        musician.save()

        if commit:
            song_submission.save()

        return song_submission
    
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Name')
    email = forms.EmailField(label='Email')
    message = forms.CharField(widget=forms.Textarea, label='Message')

    
    

