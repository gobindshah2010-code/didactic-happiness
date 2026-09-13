from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_article_role_groups(sender, **kwargs):
    if sender.name != 'articles':
        return

    Article = apps.get_model('articles', 'NewsArticle')
    content_type = ContentType.objects.get_for_model(Article)

    required_permissions = [
        'add_newsarticle',
        'change_newsarticle',
        'delete_newsarticle',
        'view_newsarticle',
        'can_publish',
    ]
    permissions = Permission.objects.filter(content_type=content_type, codename__in=required_permissions)
    permissions_by_codename = {permission.codename: permission for permission in permissions}

    all_perms = [permissions_by_codename[code] for code in required_permissions if code in permissions_by_codename]
    editor_perms = [permissions_by_codename[code] for code in ['add_newsarticle', 'change_newsarticle', 'view_newsarticle'] if code in permissions_by_codename]
    publisher_perms = [permissions_by_codename[code] for code in ['add_newsarticle', 'change_newsarticle', 'view_newsarticle', 'can_publish'] if code in permissions_by_codename]

    Group.objects.get_or_create(name='Admin')
    admin_group = Group.objects.get(name='Admin')
    admin_group.permissions.set(all_perms)

    Group.objects.get_or_create(name='Editor')
    editor_group = Group.objects.get(name='Editor')
    editor_group.permissions.set(editor_perms)

    Group.objects.get_or_create(name='Publisher')
    publisher_group = Group.objects.get(name='Publisher')
    publisher_group.permissions.set(publisher_perms)
