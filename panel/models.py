from django.db import models
from django.utils import timezone
from panel.assist import generate_uid

# Create your models here.
class Games(models.Model):
    name = models.CharField(max_length=100)

class Profile(models.Model):
  enter_name = models.CharField(max_length=255, blank=True, null=True)
  enter_id = models.CharField(max_length=255, blank=True, null=True)
  full_name = models.CharField(max_length=255, blank=True, null=True)
  username = models.CharField(max_length=255, blank=True, null=True)
  picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
  user_id = models.IntegerField()
  friends = models.ManyToManyField('self', blank=True)  # Allows users to be friends with each other
  login_code = models.CharField(max_length=255, blank=True, null=True)  # Can be blank if not used
  referral_code = models.CharField(max_length=255, blank=True, null=True, default=generate_uid())  # Can be blank if not used

  def __str__(self):
      return f"{self.username} ({self.full_name})"  # Use f-strings for cleaner formatting


class Lottery(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='lottery_entries')  # User who participated
    register_date = models.DateTimeField(default=timezone.now().isoformat(), blank=True)  # Date and time of registration
    game = models.ForeignKey(Games, on_delete=models.CASCADE, related_name='lottery_game', blank=True, null=True)  # User who participated
    friends = models.ManyToManyField(Profile, blank=True, related_name='lottery_friends')  # Friend who participated (optional)
    ticket = models.CharField(max_length=255, blank=True, null=True, default=generate_uid())  # Can be blank if not used  # Ticket number for the lottery
    status = models.CharField(max_length=20, default="Unregistered", choices=(('Registered', 'Registered'), ('Registering', 'Registering'), ('Unregistered', 'Unregistered')))  # Payment status
    ticket_picture = models.ImageField(upload_to='img/uploads/', blank=True)
    payment_status = models.CharField(max_length=20, default="PENDING", choices=(('PENDING', 'Pending'), ('PAID', 'Paid'), ('FAILED', 'Failed')))  # Payment status
    payment_picture = models.ImageField(upload_to='img/uploads/', blank=True)
    winning = models.BooleanField(default=False)  # Whether the ticket is a winner

    def __str__(self):
        return f"Lottery for {self.game} by {self.profile.username} (Ticket: {self.ticket}) - {self.payment_status}"


class Messages(models.Model):
  sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_messages')
  message = models.TextField(blank=True, null=True)
  sender_picture = models.ImageField(upload_to='img/uploads/', blank=True)
  answer = models.TextField(blank=True, null=True)
  answer_picture = models.ImageField(upload_to='img/uploads/', blank=True)
  status = models.CharField(max_length=20, choices=(('OPEN', 'Open'), ('CLOSED', 'Closed')), default='OPEN')
  created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)

class Admins(models.Model):
    name = models.CharField(max_length=255, blank=True)
    user_id = models.IntegerField()
    login_code = models.CharField(max_length=255, blank=True, null=True, default=generate_uid())  # Can be blank if not used


class Setting(models.Model):
    # payment
    card_name = models.CharField(max_length=100)
    card_number = models.PositiveIntegerField()
    price = models.PositiveIntegerField(blank=True, null=True)
    # lottery date
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    lottery_time = models.DateTimeField(blank=True, null=True)

    channel = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)