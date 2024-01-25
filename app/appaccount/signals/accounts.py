from appaccount.models.accounts import Profile, User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profiles(sender, instance: User, created, **kwargs):
    """
    Create profiles for the user when a user is created.
    """
    if created:
        Profile.objects.create(user=instance)
