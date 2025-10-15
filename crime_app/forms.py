from django import forms
from .models import*
from django.contrib.auth import get_user_model
User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(
        
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-yellow-400 outline-none',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-yellow-400 outline-none',
            'placeholder': 'Enter your password'
        })
    )

class OfficerForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Officer
        fields = ['rank', 'badge_number', 'department', 'profile_picture']  # Keep only Officer-specific fields

    def save(self, commit=True):
        # Create a new User account automatically
        user = User.objects.create_user(
            username=self.cleaned_data['email'],  # use email as username
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password=self.cleaned_data['password'],
        )
        user.role = 'officer'  # optional: set role
        user.save()

        # Create the Officer record linked to that User
        officer = super().save(commit=False)
        officer.user = user
        if commit:
            officer.save()
        return officer

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
        exclude =['is_active']
        

class CrimeReportForm(forms.ModelForm):
    class Meta:
        model = CrimeReport
        fields = [
            'title', 'description', 'location',
            'incident_type', 'department',
            'evidence_image', 'evidence_video', 'evidence_audio'
        ]  # ✅ include only valid fields

    class Meta:
        model = CrimeReport
        fields = [
            'title',
            'description',
            'location',
            'incident_type',
            'department',
            'evidence_image',
            'evidence_video',
            'evidence_audio',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the incident...'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter report title'}),
            'location': forms.TextInput(attrs={'placeholder': 'Where did it happen?'}),
            
        }