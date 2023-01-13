import pytz
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def validate_timezone(value):
    '''
    Validator for the time zone
    '''
    if value not in pytz.all_timezones:
        raise ValidationError(
            "%(value)s the time zone is specified incorrectly",
            params={"value": value},
        )


class Client(models.Model):
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    PHONE_NUMBER_REGEX = RegexValidator(
        regex=r"^7\d{10}$",
        message="Phone numbers are not matched to the pattern 7XXXXXXXXXX (X is a digit from 0 to 9)",
    )

    phone_number = models.CharField(
        verbose_name="Phone number",
        max_length=11,
        unique=True,
        validators=[PHONE_NUMBER_REGEX],
    )
    timezone = models.CharField(
        verbose_name="Time zone",
        max_length=32,
        choices=TIMEZONES,
        default="GMT",
        validators=[validate_timezone],
    )
    operator_code = models.CharField(
        verbose_name="Mobile operator code", max_length=3, editable=False
    )
    tag = models.CharField(verbose_name="Search by tag", max_length=30)

    def save(self, *args, **kwargs):
        self.operator_code = str(self.phone_number)[1:4]
        return super(Client, self).save(*args, **kwargs)

    def __str__(self):
        return f"Client: {self.id} \n phone_number: {self.phone_number} \n timezone: {self.timezone} \n operator_code: {self.operator_code} \n tag: {self.tag}"

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"


class Message(models.Model):
    class ChoicesStatuses(models.TextChoices):
        SENT = "SENT", "SENT"
        NO_SENT = "NO_SENT", "NO_SENT"

    sent_at = models.DateTimeField(verbose_name="Time of sending", auto_now=True)
    status = models.CharField(
        verbose_name="Status of sending",
        max_length=10,
        choices=ChoicesStatuses.choices,
        default=ChoicesStatuses.NO_SENT,
    )
    client = models.ForeignKey("Client", on_delete=models.SET_NULL, null=True)
    mailing = models.ForeignKey("Mailing", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Message: {self.id} \n sent_at: {self.sent_at} \n status: {self.status} \n client: {self.client} \n mailing: {self.mailing}"

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"


class Mailing(models.Model):
    CODE_OPERATOR_REGEX = RegexValidator(
        regex=r"^\d{3}$",
        message="The mobile operator's code must consist of 3 digits",
    )

    mailling_start_at = models.DateTimeField(verbose_name="Mailing start")
    mailling_end_at = models.DateTimeField(verbose_name="End of mailing")
    text = models.TextField(verbose_name="Text mailling", max_length=500)
    tag = models.CharField(verbose_name="Search by tag", max_length=30, blank=True)
    operator_code = models.CharField(
        verbose_name="Mobile operator code",
        max_length=3,
        validators=[CODE_OPERATOR_REGEX],
        blank=True,
    )


    @property
    def to_send(self):
        now = timezone.now()
        if self.mailling_start_at <= now <= self.mailling_end_at:
            return True
        else:
            return False

    def __str__(self):
        return f"Mailing: {self.id} \n start: {self.mailling_start_at} \n end: {self.mailling_end_at} \n text: {self.text} \n tag: {self.tag} \n operator_code: {self.operator_code}"

    class Meta:
        verbose_name = "Mailing"
        verbose_name_plural = "Mailings"
