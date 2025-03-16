from django.http import HttpResponseRedirect
from django.utils import timezone  
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.shortcuts import render
from userauth.models import Profile, Condition, Hostel, Block, Room, Allocation, Level
from django.contrib import messages
from userauth.models import Request
from django.utils.html import format_html
from django.db import transaction
from django.db.models import F


class LevelAdmin(admin.ModelAdmin):
    """Admin for managing Levels."""
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """Admin interface for the Level model."""
    list_display = ('name',)  # Display level name in the admin interface
    search_fields = ('name',)  # Allow search by name



@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    """Admin interface for the Hostel model."""
    list_display = ('name', 'gender', 'created_at', 'total_space', 'occupied_space')
    search_fields = ('name', 'gender')
    list_filter = ('gender',)  # Filter by gender
    readonly_fields = ('total_space', 'occupied_space')  # Make total/occupied space read-only
    filter_horizontal = ('assigned_levels',)  # Add a filter interface for assigning levels

    def save_model(self, request, obj, form, change):
        """Ensure that at least one level is assigned to the hostel before saving."""
        # if not obj.assigned_levels.exists():
        #     raise ValidationError("Please assign at least one level to the hostel.")
        
        # First save the hostel object to ensure it has an ID
        obj.save()

        # At this point, the hostel object has an ID and we can safely assign levels
        if obj.assigned_levels.exists():
            # Re-save to make sure changes are persisted properly
            obj.save()

        # Call the parent class save method
        super().save_model(request, obj, form, change)

        
@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    """Admin interface for the Block model."""
    list_display = ('name', 'hostel', 'number_of_rooms')
    search_fields = ('name', 'hostel__name')
    list_filter = ('hostel',)  # Filter by hostel


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin interface for the Room model."""
    list_display = ('name', 'block', 'capacity', 'occupied_beds')
    search_fields = ('name', 'block__name')
    list_filter = ('block',)  # Filter by block

    def save_model(self, request, obj, form, change):
        """Ensure the block is assigned before saving."""
        if not obj.block:
            raise ValidationError("Please select a block for the room.")
        super().save_model(request, obj, form, change)


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ('student', 'room', 'condition', 'allocated_at')
    search_fields = ('student__username', 'room__name', 'condition__name')
    list_filter = ('room__block__hostel', 'condition')
    readonly_fields = ('allocated_at',)

    def save_model(self, request, obj, form, change):
        obj.clean()  # Ensure validation
        super().save_model(request, obj, form, change)
        
        # Update the related request's status to 'Allocated'
        try:
            request_obj = Request.objects.get(student=obj.student, room=obj.room, status="Pending")
            request_obj.status = 'Allocated'
            request_obj.save()
        except Request.DoesNotExist:
            pass  # Handle case where no matching request is found, if necessary

class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for the Profile model."""
    search_fields = ['fullname', 'user__username']
    list_display = ['id', 'user', 'fullname', 'level', 'gender', 'registration_date', 'get_conditions', 'image_preview', 'proof_image_preview']
    list_filter = ['conditions', 'gender', 'level']  # Allows filtering by medical conditions
    readonly_fields = ['image_preview', 'proof_image_preview']

    def get_conditions(self, obj):
        return ", ".join([condition.name for condition in obj.conditions.all()])
    get_conditions.short_description = "Conditions"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Profile Picture"

    def proof_image_preview(self, obj):
        if obj.proof_image:
            return format_html('<a href="{}" target="_blank">View Proof</a>', obj.proof_image.url)
        return "No Proof Uploaded"
    proof_image_preview.short_description = "Proof Image"

from django.contrib import admin
from django.db.models import Max
from .models import Request

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    actions = ['reject_requests', 'accept_requests']
    list_display = ['student', 'room', 'status', 'created_at', 'get_student_conditions', 'get_priority']
    search_fields = ('student__username', 'room__name')
    list_filter = ('room__block__hostel', 'student__profile__conditions')  
    # readonly_fields = ['status']

    def get_queryset(self, request):
        """Annotate each request with the highest priority condition."""
        queryset = super().get_queryset(request).annotate(
            max_priority=Max('student__profile__conditions__priority')
        )
        return queryset

    @admin.display(ordering='max_priority', description="Priority Level")
    def get_priority(self, obj):
        """Display priority number in admin panel."""
        return obj.max_priority if obj.max_priority is not None else 0

    @admin.display(description="Student Conditions")
    def get_student_conditions(self, obj):
        """Display student's conditions in admin panel."""
        if hasattr(obj.student, 'profile'):
            return ", ".join([condition.name for condition in obj.student.profile.conditions.all()])
        return "No Profile"
    def accept_requests(self, request, queryset):
        successful = 0
        errors = []
        
        for req in queryset:
            try:
                # Check if room is still available
                if req.room.occupied_beds >= req.room.capacity:
                    errors.append(f"Room {req.room.name} is full - {req.student}")
                    continue

                # Check if student already has allocation
                if Allocation.objects.filter(student=req.student).exists():
                    errors.append(f"Student {req.student} already has allocation")
                    continue

                # Create allocation with transaction
                with transaction.atomic():
                    # Create allocation record
                    Allocation.objects.create(
                        student=req.student,
                        room=req.room,
                        condition=req.student.profile.conditions.first(),
                        allocated_at=timezone.now()
                    )

                    # Update room occupancy
                    Room.objects.filter(id=req.room.id).update(
                        occupied_beds=F('occupied_beds') + 1
                    )

                    # Update request status
                    req.status = 'Allocated'
                    req.save()

                    # Reject other pending requests for this student
                    Request.objects.filter(
                        student=req.student,
                        status='Pending'
                    ).exclude(id=req.id).update(
                        status='Rejected',
                        rejection_reason='Another request was accepted',
                        rejected_at=timezone.now()
                    )

                    successful += 1

            except Exception as e:
                errors.append(f"Error processing {req}: {str(e)}")

        # Build result message
        msg = f"Successfully allocated {successful} requests"
        if errors:
            self.message_user(request, f"Errors: {', '.join(errors)}", level=messages.ERROR)
        self.message_user(request, msg)

    accept_requests.short_description = "Accept selected requests and allocate rooms"

    # def reject_requests(self, request, queryset):
    #     if 'apply' in request.POST:
    #         # Get selected IDs from POST data
    #         selected_ids = request.POST.getlist('_selected_action')
    #         # Get fresh queryset from POST-selected IDs
    #         queryset = Request.objects.filter(id__in=selected_ids)
            
    #         reason = request.POST.get('rejection_reason')
    #         updated = queryset.update(
    #             status='Rejected',
    #             rejection_reason=reason,
    #             rejected_at=timezone.now(),
    #             read=False
    #         )
    #         self.message_user(request, f"Rejected {updated} requests")
    #         return HttpResponseRedirect(request.get_full_path())

    #     # Show confirmation form
    #     return render(request, 'userauth/reject_reason.html', {
    #         'requests': queryset,
    #         'opts': self.model._meta  # Required for admin template tags
    #     })
    
    
    # def reject_requests(self, request, queryset):
    #     if 'apply' in request.POST:
    #         reason = request.POST.get('rejection_reason')
    #     # Corrected the missing closing parenthesis
    #         queryset.update(
    #             status='Rejected',
    #             rejection_reason=reason,
    #             rejected_at=timezone.now(),
    #             read=False
    #         )  # ✅ Closing parenthesis was missing
    #         self.message_user(request, f"Rejected {queryset.count()} requests")
    #         return

    #     return render(request, 'userauth/reject_reason.html', {'requests': queryset})

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Condition)
