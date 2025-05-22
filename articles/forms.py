
from django import forms
from .models import Article, ArticleImage, Tag, Category
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class ArticleForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Enter tags separated by commas",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Article
        fields = ['title', 'slug', 'content', 'content_en', 'format', 'published', 'state', 'category', 'fullscreen', 'multilang']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Article Title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'article-url-slug'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15, 'id': 'article-content'}),
            'content_en': forms.Textarea(attrs={'class': 'form-control', 'rows': 15, 'id': 'english-content'}),
            'format': forms.Select(attrs={'class': 'form-select'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fullscreen': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'multilang': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])
    
    def save(self, commit=True):
        article = super().save(commit=False)
        
        # Sync published field with state
        article.published = (article.state == 'published')
        
        if commit:
            article.save()
            
            # Handle tags
            tag_names = [name.strip() for name in self.cleaned_data['tags'].split(',') if name.strip()]
            article.tags.clear()
            
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    defaults={'slug': tag_name.lower().replace(' ', '-')}
                )
                article.tags.add(tag)
                
        return article


class ArticleImageForm(forms.ModelForm):
    class Meta:
        model = ArticleImage
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image Caption'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if not image.content_type.startswith('image/'):
                raise ValidationError("Only image files are allowed.")
        return image


class ArticleSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search articles...'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label="All Tags",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    state = forms.ChoiceField(
        choices=[('', 'All States')] + list(Article.STATE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class UserProfileForm(forms.ModelForm):
    """Form for user profile updates"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': _('Username'),
            'email': _('Email Address'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})



class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
