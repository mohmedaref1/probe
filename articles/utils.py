import re
from django.utils.html import escape
from django.utils.safestring import mark_safe


def is_admin(user):
    """Check if the user is an admin"""
    return user.is_staff or user.is_superuser


def render_plaintext(content):
    """Render plain text content with line breaks"""
    escaped_content = escape(content)
    return mark_safe(escaped_content.replace('\n', '<br>'))


def render_bbcode(content):
    """
    Simple BBCode parser to convert BBCode to HTML
    
    Supported tags:
    [b]...[/b] - Bold
    [i]...[/i] - Italic
    [u]...[/u] - Underline
    [url=...]...[/url] - Link
    [img]...[/img] - Image
    [quote]...[/quote] - Quote
    [code]...[/code] - Code block
    [h1]...[/h1] - Heading 1
    [h2]...[/h2] - Heading 2
    [h3]...[/h3] - Heading 3
    [list][*]...[/list] - List
    """
    content = escape(content)
    
    # Basic formatting
    content = re.sub(r'\[b\](.*?)\[/b\]', r'<strong>\1</strong>', content)
    content = re.sub(r'\[i\](.*?)\[/i\]', r'<em>\1</em>', content)
    content = re.sub(r'\[u\](.*?)\[/u\]', r'<u>\1</u>', content)
    
    # Links
    content = re.sub(r'\[url=([^\]]+)\](.*?)\[/url\]', r'<a href="\1">\2</a>', content)
    content = re.sub(r'\[url\](.*?)\[/url\]', r'<a href="\1">\1</a>', content)
    
    # Images
    content = re.sub(r'\[img\](.*?)\[/img\]', r'<img src="\1" class="img-fluid" alt="">', content)
    
    # Quotes and code blocks
    content = re.sub(r'\[quote\](.*?)\[/quote\]', r'<blockquote class="blockquote">\1</blockquote>', content)
    content = re.sub(r'\[code\](.*?)\[/code\]', r'<pre><code>\1</code></pre>', content, flags=re.DOTALL)
    
    # Headings
    content = re.sub(r'\[h1\](.*?)\[/h1\]', r'<h1>\1</h1>', content)
    content = re.sub(r'\[h2\](.*?)\[/h2\]', r'<h2>\1</h2>', content)
    content = re.sub(r'\[h3\](.*?)\[/h3\]', r'<h3>\1</h3>', content)
    
    # Lists
    content = re.sub(r'\[list\](.*?)\[/list\]', r'<ul>\1</ul>', content, flags=re.DOTALL)
    content = re.sub(r'\[\*\](.*?)(?=\[\*\]|\[/list\])', r'<li>\1</li>', content)
    
    # Line breaks
    content = content.replace('\n', '<br>')
    
    return mark_safe(content)


def render_html(content):
    """Pass HTML content directly (already sanitized by Django admin)"""
    return mark_safe(content)


def render_content(content, format_type):
    """
    Render content based on its format type
    """
    if format_type == 'plaintext':
        return render_plaintext(content)
    elif format_type == 'bbcode':
        return render_bbcode(content)
    elif format_type == 'html':
        return render_html(content)
    else:
        # Default to plain text
        return render_plaintext(content)