from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.utils import timezone
import re
from django.contrib import messages
from django.db.models import Max


class UniversityImage(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')  # Saves to media/images/

    def __str__(self):
        return self.title

# Constants
GENDER = (
    ("Female", "Female"),
    ("Male", "Male"),
)

CONDITION = (
    ('MEDICAL', 'MEDICAL'),
    ('EXECUTIVE', 'EXECUTIVE'),
    ('PREFERENCE', 'PREFERENCE'),
)

LEVEL = (
    ('100', '100'),
    ('200', '200'),
    ('300', '300'),
    ('400', '400'),
    ('500', '500'),
    ('600', '600'),
)

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.user.id}.{ext}"
    return f"user_{instance.user.id}/{filename}"

class Level(models.Model):
    """A model to define levels (e.g., 100, 200, etc.)."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Condition(models.Model):
    name = models.CharField(max_length=100, unique=True)
    priority = models.PositiveIntegerField(default=1)  # Optional: Assign a priority to each condition

    def __str__(self):
        return self.name

class Hostel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    gender = models.CharField(choices=GENDER, max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_levels = models.ManyToManyField(
        Level, 
        related_name="hostels", 
        blank=True,
        help_text="Levels to which this hostel is assigned"
    )

    @property
    def total_space(self):
        """Total capacity across all blocks."""
        return sum(block.total_space for block in self.blocks.all())

    @property
    def occupied_space(self):
        """Total occupied beds across all blocks."""
        return sum(block.occupied_space for block in self.blocks.all())

    @property
    def available_space(self):
        """Available beds across the hostel."""
        return self.total_space - self.occupied_space

    def __str__(self):
        return f"{self.name} ({self.gender})"

def clean(self):
    """Ensure no duplicate hostels are created."""
    if Hostel.objects.filter(name=self.name).exclude(pk=self.pk).exists():
        raise ValidationError(f"A hostel with the name '{self.name}' already exists.")


class Block(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="blocks")
    name = models.CharField(max_length=1)
    number_of_rooms = models.PositiveIntegerField(default=0)

    @property
    def total_space(self):
        """Calculate the total space for this block by summing the capacity of all rooms."""
        return sum(room.capacity for room in self.rooms.all())

    @property
    def occupied_rooms(self):
        """Calculate the number of rooms that are occupied in this block."""
        return sum(1 for room in self.rooms.all() if room.occupied_beds > 0)

    @property
    def available_space(self):
        """Calculate the available space (total space - occupied space) for this block."""
        return self.total_space - self.occupied_space

    @property
    def occupied_space(self):
        """Calculate the total number of occupied beds in this block."""
        return sum(room.occupied_beds for room in self.rooms.all())

    def __str__(self):
        return f"Block {self.name} - {self.hostel.name}"

    class Meta:
        unique_together = ('hostel', 'name')

class Profile(models.Model):
    pid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvwxyz123")
    image = models.FileField(upload_to=user_directory_path, default="default.jpg", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=200)
    mobile = models.CharField(default=0, max_length=11)
    level = models.CharField(choices=LEVEL, max_length=100)
    gender = models.CharField(choices=GENDER, max_length=100)
    address = models.CharField(max_length=1000, null=True, blank=True)
    registration_date = models.DateTimeField(default=timezone.now)
    conditions = models.ManyToManyField(
        Condition,
        related_name="profiles",
        blank=True,
        help_text="Select your condition(s) from the list"
    )
    other_health_challenges = models.TextField(
        blank=True,
        null=True,
        help_text="Describe other health challenges not listed above"
    )
    matric_number = models.CharField(max_length=1000, null=True, blank=True)
    proof_image = models.FileField(upload_to=user_directory_path, default="default.jpg", null=True, blank=True,
                                   help_text="Submit doctor's reports, executive IDs, or any other form of proof")
    next_of_kin = models.CharField(max_length=200)
    next_of_kin_mobile = models.CharField(default=0, max_length=11)

    class Meta:
        ordering = ['-registration_date']

    def __str__(self):
        return self.fullname or self.user.username

    def clean(self):
        """
        Ensure the selected hostel matches the student's gender
        and assigned levels include the student's level.
        """
        if self.gender and self.level:
            hostels = Hostel.objects.filter(gender=self.gender)
            if hostels.exists():
                hostels = hostels.filter(assigned_levels__name=self.level)
            if not hostels.exists():
                raise ValidationError(
                    f"No suitable hostel found for gender {self.gender} and level {self.level}."
                )
def clean(self):
    profile = self.student.profile
    if self.hostel.gender != profile.gender:
        raise ValidationError(f"{self.hostel.name} is not available for {profile.gender} students.")
    # Additional validation for level if needed
# Signal to create a profile after a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
class Room(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=10)  # e.g., A1, A2
    capacity = models.PositiveIntegerField()  # Maximum number of occupants
    occupied_beds = models.PositiveIntegerField(default=0)  # Current number of occupants

    class Meta:
        unique_together = ('block', 'name')  # Ensure no duplicate rooms in a block

    def __str__(self):
        return f"Room {self.name} - Block {self.block.name} ({self.block.hostel.name})"

    @property
    def request_count(self):
        """Return the number of requests made for this room"""
        return self.requests.filter(status="Pending").count()

class Allocation(models.Model):
    student = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="allocation",
        help_text="The student being allocated"
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="allocations")
    condition = models.ForeignKey(
        Condition, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="The priority condition for the allocation"
    )
    allocated_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
        Ensure that the student's level matches the hostel's assigned levels.
        """
        profile = self.student.profile
        hostel = self.room.block.hostel

        # Check if the student's level is in the list of assigned levels for the hostel
        level_instance = Level.objects.filter(name=profile.level).first()
        if level_instance and level_instance not in hostel.assigned_levels.all():
            raise ValidationError(
                f"Allocation failed: {profile.fullname}'s level ({profile.level}) is not allowed in {hostel.name}."
            )
class Request(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="requests",
        help_text="The student making the request"
    )
    hostel = models.ForeignKey(
        Hostel, on_delete=models.CASCADE, related_name="requests",
        help_text="The requested hostel"
    )
    block = models.ForeignKey(
        Block, on_delete=models.CASCADE, related_name="requests",
        help_text="The requested block"
    )
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="requests",
        help_text="The requested room"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.PositiveIntegerField(default=0, help_text="Priority level based on student's condition")  # ✅ Add this
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Allocated', 'Allocated'), 
        ('Rejected', 'Rejected')
    ]
    
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='Pending'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    read = models.BooleanField(default=False)
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.student.profile.fullname} - {self.room.name} ({self.status})"

    def clean(self):
        profile = self.student.profile
        if self.hostel.gender != profile.gender:
            raise ValidationError(f"{self.hostel.name} is not available for {profile.gender} students.")

        level_instance = Level.objects.filter(name=profile.level).first()
        if level_instance and level_instance not in self.hostel.assigned_levels.all():
            raise ValidationError(
                f"Level {profile.level} is not allowed in {self.hostel.name}."
            )

        if self.room.occupied_beds >= self.room.capacity:
            raise ValidationError(f"Room {self.room.name} is already full.")

    def save(self, *args, **kwargs):
        """Calculate and store the priority before saving."""
        self.priority = self.student.profile.conditions.aggregate(
            max_priority=Max('priority')
        )['max_priority'] or 0  # ✅ Assign priority before saving
        super().save(*args, **kwargs)
