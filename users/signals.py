from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Profile


# add to apps.py file inorder to work
@receiver(post_save, sender=User)
def user_postsave(sender, instance, created, **kwargs):
    user = instance

    # add profile if user created
    if created: 
        Profile.objects.create(
            user = user,
        )