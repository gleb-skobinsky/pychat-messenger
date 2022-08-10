import email
from django.contrib.auth.models import (
    User,
    UserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core import validators
from django.db.models import (
    Model,
    TextField,
    CharField,
    BooleanField,
    DateTimeField,
    EmailField,
    ImageField,
    ForeignKey,
    CASCADE,
)

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class ChatUser(AbstractBaseUser, PermissionsMixin):
    avatar = ImageField(upload_to="uploads/", default="run/media_root/default_user.png")
    username = CharField(
        max_length=30,
        unique=True,
        help_text=(
            "Required. 30 characters or fewer. Letters, digits and " "@/./+/-/_ only."
        ),
        validators=[
            validators.RegexValidator(
                r"^[\w.@+-]+$",
                (
                    "Enter a valid username. "
                    "This value may contain only letters, numbers "
                    "and @/./+/-/_ characters."
                ),
                "invalid",
            ),
        ],
        error_messages={
            "unique": ("A user with that username already exists."),
        },
    )
    email = EmailField(blank=True)
    password = CharField(("password"), max_length=128, default="password")
    is_staff = BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin " "site."),
    )
    is_active = BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = DateTimeField(_("date joined"), default=timezone.now)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    objects = UserManager()


class MessageModel(Model):
    """
    This class represents a chat message. It has a owner (user), timestamp and
    the message body.

    """

    user = ForeignKey(
        ChatUser,
        on_delete=CASCADE,
        verbose_name="user",
        related_name="from_user",
        db_index=True,
    )
    recipient = ForeignKey(
        ChatUser,
        on_delete=CASCADE,
        verbose_name="recipient",
        related_name="to_user",
        db_index=True,
    )
    timestamp = DateTimeField(
        "timestamp", auto_now_add=True, editable=False, db_index=True
    )
    body = TextField("body")

    def __str__(self):
        return str(self.id)

    def characters(self):
        """
        Toy function to count body characters.
        :return: body's char number
        """
        return len(self.body)

    def notify_ws_clients(self):
        """
        Inform client there is a new message.
        """
        notification = {
            "type": "recieve_group_message",
            "message": "{}".format(self.id),
        }

        channel_layer = get_channel_layer()
        print("user.id {}".format(self.user.id))
        print("user.id {}".format(self.recipient.id))

        async_to_sync(channel_layer.group_send)("{}".format(self.user.id), notification)
        async_to_sync(channel_layer.group_send)(
            "{}".format(self.recipient.id), notification
        )

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.id
        self.body = self.body.strip()  # Trimming whitespaces from the body
        super(MessageModel, self).save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()

    # Meta
    class Meta:
        app_label = "core"
        verbose_name = "message"
        verbose_name_plural = "messages"
        ordering = ("-timestamp",)
