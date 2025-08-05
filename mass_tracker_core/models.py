
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class Priest(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username

class IntentionType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, null=False, blank=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class IntentionSource(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, null=False, blank=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class MassIntention(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    priest = models.ForeignKey(Priest, on_delete=models.CASCADE, null=False, blank=False)
    intention_type = models.ForeignKey(IntentionType, on_delete=models.CASCADE, null=False, blank=False)
    intention_source = models.ForeignKey(IntentionSource, on_delete=models.CASCADE, null=False, blank=False)
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class PersonalMassIntention(models.Model):
    mass_intention = models.OneToOneField(MassIntention, on_delete=models.CASCADE, primary_key=True)
    month = models.IntegerField(null=False, blank=False)
    year = models.IntegerField(null=False, blank=False)
    celebrated_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Personal Mass for {self.mass_intention.priest.username} - {self.month}/{self.year}"

class FixedDateMassIntention(models.Model):
    mass_intention = models.OneToOneField(MassIntention, on_delete=models.CASCADE, primary_key=True)
    original_date = models.DateField(null=False, blank=False)
    rescheduled_date = models.DateField(null=True, blank=True)
    reschedule_reason = models.TextField(blank=True, null=True)
    is_celebrated = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return f"Fixed Date Mass for {self.mass_intention.priest.username} on {self.original_date}"

class BulkMassIntention(models.Model):
    mass_intention = models.OneToOneField(MassIntention, on_delete=models.CASCADE, primary_key=True)
    total_masses = models.IntegerField(null=False, blank=False)
    remaining_masses = models.IntegerField(null=False, blank=False)
    start_date = models.DateField(null=False, blank=False)
    is_paused = models.BooleanField(default=False, null=False, blank=False)
    last_celebrated_date = models.DateField(null=True, blank=True)
    estimated_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Bulk Mass for {self.mass_intention.priest.username} - {self.remaining_masses}/{self.total_masses}"

class MassCelebration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    priest = models.ForeignKey(Priest, on_delete=models.CASCADE, null=False, blank=False)
    mass_intention = models.ForeignKey(MassIntention, on_delete=models.CASCADE, null=False, blank=False)
    celebration_date = models.DateField(null=False, blank=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mass by {self.priest.username} for {self.mass_intention.title} on {self.celebration_date}"

class DailyStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    priest = models.ForeignKey(Priest, on_delete=models.CASCADE, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    celebrated_mass = models.BooleanField(default=False, null=False, blank=False)
    reason_not_celebrated = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('priest', 'date')

    def __str__(self):
        return f"Daily Status for {self.priest.username} on {self.date}: {self.celebrated_mass}"


