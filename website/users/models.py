from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import secrets
import pytz
import datetime
from django.conf import settings


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
            admin=is_admin,
            staff=is_staff,
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


class User(AbstractBaseUser):
    """User object."""

    username = models.CharField(max_length=256, unique=True)
    email = models.EmailField(max_length=256, unique=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

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
        return self.username

    def get_short_name(self):
        """
        Get the short name of a User object.

        :return: username
        """
        return self.username

    @property
    def is_staff(self):
        """
        Check if a user is a staff user.

        :return: True if the user has staff access, False otherwise
        """
        return self.staff

    @property
    def is_admin(self):
        """
        Check if a user is an administrator.

        :return: True if the user has administrative access, False otherwise
        """
        return self.admin

    def has_perm(self, perm_list, obj=None):
        """
        Check if a user has all permissions in perm_list.

        :param perm_list: permission list
        :param obj: the object over which the permissions must hold
        :return: True
        """
        return True

    def has_module_perms(self, package_name):
        """
        Check if a user has all permissions over a package.

        :param package_name: the package name
        :return: True
        """
        return True


class PasswordReset(models.Model):
    """Queued password resets object."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, null=False, blank=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)

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

    def __str__(self):
        """
        Convert this object to string.

        :return: a string format of the username and the creation timestamp
        """
        return "{}, created: {}".format(self.user.username, self.created)

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
