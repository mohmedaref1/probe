from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404, JsonResponse, HttpResponseNotFound
from django.forms import modelformset_factory
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _
from django.utils.text import slugify
import random
import string
from .models import Article, Tag, Category, ArticleImage
from .forms import ArticleForm, ArticleImageForm, ArticleSearchForm, CustomAuthenticationForm, UserProfileForm
from .utils import render_content, is_admin


def set_language(request, language):
    """Set the language for the session"""
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    response.set_cookie('django_language', language)
    return response


@require_POST
def set_theme(request):
    """Set the theme preference"""
    dark_mode = request.POST.get('dark_mode', 'false') == 'true'
    response = JsonResponse({'status': 'success'})
    response.set_cookie(
        'dark_mode', 
        'true' if dark_mode else 'false',
        path='/',  # Add this line
        max_age=365*24*60*60,  # 1 year
        samesite='Lax'
    )
    return response


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'articles/login.html'


def index(request):
    """Simple landing page with website information"""
    dark_mode = request.COOKIES.get('dark_mode', 'false').lower() == 'true'
    return render(request, 'articles/index.html', {
        'dark_mode': dark_mode
    })

@login_required
@user_passes_test(is_admin)
def article_list(request):
    """Public list of all published articles"""
    dark_mode = request.COOKIES.get('dark_mode', 'false').lower() == 'true'
    articles = Article.objects.filter(state='published').order_by('-created_at')
    form = ArticleSearchForm(request.GET)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        tag = form.cleaned_data.get('tag')
        
        if query:
            articles = articles.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
        
        if category:
            articles = articles.filter(category=category)
            
        if tag:
            articles = articles.filter(tags=tag)
    
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    # Process each article to add truncated rendered content
    for article in articles:
        article.render_content = render_content(article.content, article.format)
        
    return render(request, 'articles/article_list.html', {
        'articles': articles,
        'form': form,
        'categories': categories,
        'tags': tags,
        'dark_mode': dark_mode
    })


def article_detail(request, slug):
    """Public view of a single article"""
    dark_mode = request.COOKIES.get('dark_mode', 'false').lower() == 'true'
    try:
        article = get_object_or_404(Article, slug=slug)
        
        # Check if article is published or user is staff
        if article.state != 'published' and not request.user.is_staff:
            return render(request, '404.html', {'dark_mode': dark_mode}, status=404)

        # Render content based on the selected format
        rendered_content = render_content(article.content, article.format)
        if article.content_en:
            rendered_content_en = render_content(article.content_en, article.format)
        context = {
            'article': article,
            'rendered_content': rendered_content,
            'rendered_content_en': rendered_content_en if article.content_en else '',
            'hide_navbar' : True,
            'fullscreen' : article.fullscreen,
            'multilang' : article.multilang,
            'dark_mode': dark_mode
        }
        if article.fullscreen:
            return render(request, 'articles/article_detail_full.html', context)
        else:
            return render(request, 'articles/article_detail.html', context)
    except Http404:
        return render(request, '404.html', {'dark_mode': dark_mode}, status=404)


@login_required
@user_passes_test(is_admin)
def user_profile(request):
    """View for users to update their profile information"""
    dark_mode = request.COOKIES.get('dark_mode', 'false').lower() == 'true'
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        
        # Check which form was submitted
        if 'submit_profile' in request.POST and form.is_valid():
            form.save()
            messages.success(request, _("Profile updated successfully!"))
            return redirect('user_profile')
            
        elif 'submit_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, _("Password changed successfully!"))
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    
    return render(request, 'articles/user_profile.html', {
        'form': form,
        'password_form': password_form,
        'dark_mode': dark_mode
    })


def generate_temp_data():
    """Generate random data for temporary article creation"""
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return {
        'title': f'Draft-{random_string}',
        'slug': f'draft-{random_string}',
        'content': 'Temporary draft content'
    }


@login_required
@user_passes_test(is_admin)
def article_create(request):
    """Admin view to create a new article"""
    dark_mode = request.COOKIES.get('dark_mode', 'false').lower() == 'true'
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        image_form = ArticleImageForm(request.POST, request.FILES)
        
        # Check if we're adding a new category
        new_category_name = request.POST.get('new_category_name')
        if new_category_name:
            category, created = Category.objects.get_or_create(
                name=new_category_name,
                defaults={'slug': slugify(new_category_name)}
            )
            if created:
                messages.success(request, _("New category created!"))
                
            # Update the form's category selection
            if request.POST.get('category') == 'new':
                request.POST = request.POST.copy()
                request.POST['category'] = category.id
        
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            
            # Save tags
            form.save_m2m()
            
            # Save uploaded image if provided
            if 'image' in request.FILES and image_form.is_valid():
                image = image_form.save(commit=False)
                image.article = article
                image.save()
            
            messages.success(request, _("Article created successfully!"))
            return redirect('article_edit', slug=article.slug)
    else:
        form = ArticleForm()
        image_form = ArticleImageForm()
    
    categories = Category.objects.all()
    
    context = {
        'form': form,
        'image_form': image_form,
        'categories': categories,
        'action': _('Create'),
        'dark_mode': dark_mode
    }
    
    return render(request, 'articles/article_form.html', context)


@login_required
@user_passes_test(is_admin)
def article_edit(request, slug):
    """Admin view to edit an existing article"""
    dark_mode = request.COOKIES.get('dark_mode', 'false').lower() == 'true'
    isediting = True
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        
        # Check if we're adding a new category
        new_category_name = request.POST.get('new_category_name')
        if new_category_name:
            category_slug = None
            category, created = Category.objects.get_or_create(
                name=new_category_name,
                defaults={'slug': slugify(new_category_name)}
            )
            if created:
                messages.success(request, _("New category created!"))
                
            # Update the form's category selection
            if request.POST.get('category') == 'new':
                request.POST = request.POST.copy()
                request.POST['category'] = category.id
        
        # Create a formset for image uploads
        ImageFormSet = modelformset_factory(ArticleImage, form=ArticleImageForm, extra=1)
        formset = ImageFormSet(
            request.POST, 
            request.FILES,
            queryset=ArticleImage.objects.filter(article=article)
        )
        
        if form.is_valid() and formset.is_valid():
            article = form.save()
            
            # Save images
            instances = formset.save(commit=False)
            for instance in instances:
                instance.article = article
                instance.save()
            
            messages.success(request, _("Article updated successfully!"))
            return redirect('article_edit', slug=article.slug)
    else:
        form = ArticleForm(instance=article)
        
        # Create a formset for image uploads
        ImageFormSet = modelformset_factory(ArticleImage, form=ArticleImageForm, extra=1)
        formset = ImageFormSet(queryset=ArticleImage.objects.filter(article=article))
    
    # Get a preview of the content
    rendered_content = render_content(article.content, article.format)
    if article.content_en:
        rendered_content_en = render_content(article.content_en, article.format)

    categories = Category.objects.all()
    
    context = {
        'form': form,
        'formset': formset,
        'article': article,
        'rendered_content': rendered_content,
        'rendered_content_en': rendered_content_en if article.content_en else '',
        'categories': categories,
        'action': _('Edit'),
        'isediting':isediting,
        'dark_mode': dark_mode
    }
    
    return render(request, 'articles/article_form.html', context)


@login_required
@user_passes_test(is_admin)
def article_delete(request, slug):
    """Admin view to delete an article"""
    dark_mode = request.COOKIES.get('dark_mode', 'false').lower() == 'true'
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, _("Article deleted successfully!"))
        return redirect('article_admin_list')
    
    return render(request, 'articles/article_confirm_delete.html', {
        'article': article,
        'dark_mode': dark_mode
    })


@login_required
@user_passes_test(is_admin)
def article_admin_list(request):
    """Admin view to list all articles for management"""
    dark_mode = request.COOKIES.get('dark_mode', 'false').lower() == 'true'
    articles = Article.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    archived_articles = Article.objects.filter(state='archived').count()
    
    # Apply filters if provided in query params
    query = request.GET.get('query')
    category_id = request.GET.get('category')
    state = request.GET.get('state')
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    
    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            articles = articles.filter(category=category)
        except (Category.DoesNotExist, ValueError):
            pass
        
    if state:
        articles = articles.filter(state=state)
    
    active_articles = [article for article in articles if article.state != 'archived']
    archived_articles_list = [article for article in articles if article.state == 'archived']
    
    return render(request, 'articles/article_admin_list.html', {
        'articles': articles,
        'active_articles': active_articles,
        'archived_articles_list': archived_articles_list,
        'categories': categories,
        'dark_mode': dark_mode,
        'archived_articles_count': archived_articles
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def update_article_state(request):
    """AJAX endpoint to update article state"""
    article_id = request.POST.get('article_id')
    state = request.POST.get('state')
    
    if not article_id or not state or state not in dict(Article.STATE_CHOICES):
        return JsonResponse({'status': 'error', 'message': _('Invalid parameters')})
    
    try:
        article = Article.objects.get(id=article_id)
        article.state = state
        article.published = (state == 'published')
        article.save()
        
        messages.success(request, _("Article state updated successfully."))
        return redirect('article_admin_list')
    except Article.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': _('Article not found')})


@login_required
@user_passes_test(is_admin)
@require_POST
def upload_image(request):
    """AJAX endpoint to upload images immediately"""
    if 'image' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No image provided'})
        
    image = request.FILES['image']
    image_type = request.POST.get('type', 'additional')
    article_id = request.POST.get('article_id')
    image_id = request.POST.get('image_id')
    
    try:
        # If no article_id is provided or article doesn't exist, create a temporary article
        article = None
        if article_id:
            try:
                article = Article.objects.get(id=article_id)
            except Article.DoesNotExist:
                pass
        
        if not article:
            temp_data = generate_temp_data()
            article = Article(
                title=temp_data['title'],
                slug=temp_data['slug'],
                content=temp_data['content'],
                author=request.user,
                state='draft'
            )
            article.save()
            article_id = article.id
        
        # Handle additional image
        if image_type == 'additional':
            if image_id:
                try:
                    article_image = ArticleImage.objects.get(id=image_id)
                    article_image.image = image
                    article_image.save()
                    image_url = request.build_absolute_uri(article_image.image.url)
                    return JsonResponse({
                        'success': True, 
                        'image_url': image_url,
                        'image_id': article_image.id,
                        'article_id': article.id,
                        'full_url': request.build_absolute_uri(article_image.image.url)
                    })
                except ArticleImage.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Image not found'})
            else:
                article_image = ArticleImage(article=article, image=image)
                article_image.save()
                image_url = request.build_absolute_uri(article_image.image.url)
                return JsonResponse({
                    'success': True, 
                    'image_url': image_url,
                    'image_id': article_image.id,
                    'article_id': article.id,
                    'full_url': request.build_absolute_uri(article_image.image.url)
                })
        
        return JsonResponse({'success': False, 'error': 'Invalid parameters'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_image(request):
    """AJAX endpoint to delete images"""
    image_id = request.POST.get('image_id')
    image_type = request.POST.get('type', 'featured')
    
    if not image_id:
        return JsonResponse({'success': False, 'error': 'No image ID provided'})
    
    try:
        if image_type == 'featured':
            article = Article.objects.get(id=image_id)
            if article.featured_image:
                article.featured_image.delete(save=False)  # delete file from media folder
                article.featured_image = None  # clear the field
                article.save()
            return JsonResponse({'success': True})
        elif image_type == 'additional':
            article_image = ArticleImage.objects.get(id=image_id)
            article_image.image.delete(save=False)  # delete file from media folder
            article_image.delete()  # delete the record
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Invalid image type'})
    except (Article.DoesNotExist, ArticleImage.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Image not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def handler404(request, exception=None):
    dark_mode = request.COOKIES.get('dark_mode', 'false').lower() == 'true'
    return render(request, '404.html', {'dark_mode': dark_mode}, status=404)