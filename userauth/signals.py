# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Allocation, Request

@receiver(post_save, sender=Allocation)
def update_request_status_on_allocation(sender, instance, created, **kwargs):
    if created:  # This ensures the signal only runs when a new Allocation is created
        try:
            # Get the corresponding request for this student and room
            request = Request.objects.get(student=instance.student, room=instance.room, status="Pending")
            request.status = 'Allocated'  # Change status to "Allocated"
            request.save()
        except Request.DoesNotExist:
            pass  # If no matching request is found, you can handle the exception or ignore it
