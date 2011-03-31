from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """ User profile model """
    user = models.ForeignKey(User, unique=True)
    families = models.TextField()

    def has_family(self, family):
        if family in self.families.split(","):
            return True
        else:
            return False

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
