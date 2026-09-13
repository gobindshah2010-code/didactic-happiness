from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


class NewsArticle(models.Model):
    DRAFT = 'draft'
    PENDING = 'pending'
    PUBLISHED = 'published'

    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PENDING, 'Pending Review'),
        (PUBLISHED, 'Published'),
    ]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='articles')
    content = models.TextField()
    image = models.ImageField(upload_to='articles/%Y/%m/%d/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('can_publish', 'Can publish articles'),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[self.slug])
