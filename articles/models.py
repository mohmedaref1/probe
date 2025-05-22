
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse

def article_image_path(instance, filename):
    """Generate file path for article images"""
    return f'article_images/{instance.article.slug}/{filename}'

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    FORMAT_CHOICES = (
        ('plaintext', 'Plain Text'),
        ('bbcode', 'BBCode'),
        ('html', 'HTML'),
    )
    
    STATE_CHOICES = (
        ('published', 'Published'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    content_en = models.TextField(default='')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='plaintext')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    fullscreen = models.BooleanField(default=False)
    multilang = models.BooleanField(default=False)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='published')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Update state based on published field for backward compatibility
        if self.published and self.state == 'draft':
            self.state = 'published'
        elif not self.published and self.state == 'published':
            self.state = 'draft'
            
        # Update published field based on state
        self.published = (self.state == 'published')
            
        super().save(*args, **kwargs)


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=article_image_path)
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.article.title}"
