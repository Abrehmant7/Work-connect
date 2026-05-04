from django.utils.text import slugify
import uuid

def generate_slug(title:str) -> str:
    from .models import Post

    title = slugify(title)
    while(Post.objects.filter(slug = title)):
        title = f'{slugify(title)}-{str(uuid.uuid4())[:4]}'

    return title