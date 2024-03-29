from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import secrets
import pytz
import datetime
from django.conf import settings


class UserManager(BaseUserManager):
    """User manager object."""

    def create_user(
        self, username, email, password=None, is_staff=False, is_admin=False
    ):
        """
        Create a new user.

        :param username: the username of the new user, must be unique
        :param email: the email of the new user, must be unique
        :param password: the password for the new user
        :param is_staff: whether or not to create a staff user
        :param is_admin: whether or not to create an administrative user
        :return: the new user
        """
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have a password")
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            is_superuser=is_admin,
            is_staff=is_staff,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, username, email, password):
        """
        Create a new staff user.

        :param username: the username of the new user, must be unique
        :param email: the email of the new user, must be unique
        :param password: the password for the new user
        :return: the new user
        """
        return self.create_user(username, email, password, is_staff=True)

    def create_superuser(self, username, email, password):
        """
        Create a new super user.

        :param username: the username of the new user, must be unique
        :param email: the email of the new user, must be unique
        :param password: the password for the new user
        :return: the new user
        """
        return self.create_user(
            username, email, password=password, is_staff=True, is_admin=True
        )


class User(AbstractUser):
    """User object."""

    username = models.CharField(max_length=256, unique=True)
    email = models.EmailField(max_length=256, unique=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        """
        Convert user to string.

        :return: the email of the user
        """
        return self.email

    def get_full_name(self):
        """
        Get the full name of a User object.

        :return: username
        """
        if self.first_name and self.last_name:
            return "{} {}".format(self.first_name, self.last_name)
        elif self.first_name:
            return self.first_name
        else:
            return self.username

    def get_short_name(self):
        """
        Get the short name of a User object.

        :return: username
        """
        if self.first_name:
            return self.first_name
        else:
            return self.username

    def get_profile(self):
        """
        Get the profile corresponding to this user object.

        :return: a Profile object corresponding to this user, if it does not exist create it first
        """
        try:
            return Profile.objects.get(user=self)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=self)
            profile.save()
            return profile


class PasswordReset(models.Model):
    """Queued password resets object."""

    user = models.ForeignKey(
        User, related_name="password_resets", on_delete=models.CASCADE
    )
    token = models.CharField(max_length=64, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Convert this object to string.

        :return: a string format of the username and the creation timestamp
        """
        return "{}, created: {}".format(self.user.username, self.created)

    @staticmethod
    def generate(user):
        """
        Generate a PasswordReset object with random token.

        :param user: the User object for which to generate the password reset
        :return: a PasswordReset object connected to the User object and with a random token
        """
        random_token = secrets.token_hex(32)
        reset = PasswordReset.objects.create(token=random_token, user=user)
        return reset

    @staticmethod
    def remove_expired():
        """
        Remove all expired PasswordReset objects.

        :return: None
        """
        password_resets = PasswordReset.objects.all()
        timezone = pytz.timezone(settings.TIME_ZONE)
        remove_after = timezone.localize(
            datetime.datetime.now() - datetime.timedelta(minutes=15)
        )
        for password_reset in password_resets:
            if password_reset.created <= remove_after:
                password_reset.delete()


class EmailUpdate(models.Model):
    """Queued email update model."""

    user = models.ForeignKey(
        User, related_name="email_updates", on_delete=models.CASCADE
    )
    token = models.CharField(max_length=64, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    email_address = models.EmailField(max_length=512)

    def __str__(self):
        """
        Convert this object to string.

        :return: a string format of the username and the creation timestamp
        """
        return "{}, created: {}".format(self.user.username, self.created)

    @staticmethod
    def generate(user, email_address):
        """
        Generate a EmailUpdate object with random token.

        :param user: the User object for which to generate the email update
        :param email_address: the new email address to register for the email update
        :return: a EmailUpdate object connected to the User object and with a random token
        """
        random_token = secrets.token_hex(32)
        reset = EmailUpdate.objects.create(
            token=random_token, user=user, email_address=email_address
        )
        return reset

    def update_user(self):
        """
        Update the corresponding user with the new email address.

        :return: None
        """
        self.user.email = self.email_address
        self.user.save()

    @staticmethod
    def remove_expired():
        """
        Remove all expired EmailUpdate objects.

        :return: None
        """
        email_updates = EmailUpdate.objects.all()
        timezone = pytz.timezone(settings.TIME_ZONE)
        remove_after = timezone.localize(
            datetime.datetime.now() - datetime.timedelta(minutes=60)
        )
        for email_update in email_updates:
            if email_update.created <= remove_after:
                email_update.delete()


class Profile(models.Model):
    """Profile of a user."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=512, blank=True)
    postal_code = models.CharField(max_length=256, blank=True)
    residence = models.CharField(max_length=512, blank=True)

    def __str__(self):
        """
        Convert this object to string.

        :return: the username of the user object
        """
        return self.user.__str__()
