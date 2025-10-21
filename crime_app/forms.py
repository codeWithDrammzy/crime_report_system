from django import forms
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your address',
            'rows': 3
        })
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'password1', 'password2'
        ]  # Removed username and role fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field since we're using email
        self.fields.pop('username', None)
        
        # Add styling to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use email as username and set role as citizen
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        user.role = 'citizen'  # Default role for self-registration
        
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Authenticate using email instead of username
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
                if user is None:
                    raise forms.ValidationError("Invalid email or password.")
                cleaned_data['user'] = user
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")
        
        return cleaned_data


# ... rest of your existing forms (OfficerForm, DepartmentForm, etc.) remain the same
class OfficerForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Officer
        fields = ['rank', 'badge_number', 'department', 'profile_picture']

    def save(self, commit=True):
        # Create a new User account automatically
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password=self.cleaned_data['password'],
        )
        user.role = 'officer'
        user.save()

        officer = super().save(commit=False)
        officer.user = user
        if commit:
            officer.save()
        return officer


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
        exclude = ['is_active']


class CrimeSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by report ID, department, location, status, or type',
            'class': 'bg-blue-800 text-sm px-4 py-2 rounded-full focus:outline-none focus:ring-2 focus:ring-yellow-400 placeholder-gray-300 text-gray-100 w-full pr-10'
        })
    )


class CrimeReportForm(forms.ModelForm):
    class Meta:
        model = CrimeReport
        fields = [
            'title', 'description', 'location',
            'incident_type', 'department',
            'evidence_image', 'evidence_video', 'evidence_audio'
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Describe the incident...',
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter report title',
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Where did it happen?',
                'class': 'form-control'
            }),
            'incident_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'department': forms.Select(attrs={
                'class': 'form-control'
            }),
            'evidence_image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'evidence_video': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'evidence_audio': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }