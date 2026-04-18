from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.templatetags.static import static

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image  = models.ImageField(upload_to='avatars', null=True, blank=True)
    displayname = models.CharField(max_length=20, blank=True, null=True)
    info = models.TextField(null=True, blank=True)


    def __str__(self):
        return str(self.user)

    @property
    def name(self):
        if self.displayname:
            name = self.displayname

        else: 
            name = self.user.username
        return name

    @property
    def avatar(self):
       # 1. Check if an image actually exists
        if self.image and hasattr(self.image, 'url'):
            # 2. Return the ImageKit URL by appending the file name to the endpoint
            # This points to https://ik.imagekit.io/your_id/avatars/filename.jpg
            return f"{settings.IMAGEKIT_URL_ENDPOINT}{self.image.name}"
        
        # 3. Fallback to your default static avatar
        return static('images/avatar.svg')
