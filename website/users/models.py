from django.db import models


class UserInformation(models.Model):
    """User information object."""

    firstname = models.CharField(max_length=256)
    lastname = models.CharField(max_length=256, blank=True)
    email_address = models.EmailField(max_length=256)
    address = models.CharField(max_length=256, blank=True)
    postal_code = models.CharField(max_length=6, blank=True)
    residence = models.CharField(max_length=256, blank=True)

    def __str__(self):
        """
        Casts this object to a string format.

        :return: the firstname and lastname of this object seperated by a space
        """
        return "{} {}".format(self.firstname, self.lastname)
