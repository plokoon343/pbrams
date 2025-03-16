from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from userauth.models import Profile, User, Level
from userauth.forms import UserRegisterForm, ProfileForm, MyPasswordChangeForm
from userauth.models import Hostel, Block
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from userauth.models import Hostel, Room, Allocation, Level, Block
from userauth.forms import OccupiedRoomForm  # Create this form
from userauth.models import Room, Request
from django.core.exceptions import ValidationError
# Register View

def RegisterView(request):
    if request.user.is_authenticated:
        username = request.user.username
        messages.warning(request, f"Hey {username}, you are already logged in.")
        return redirect("hostel:index")

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, your account has been created successfully!")

            # Initialize profile
            Profile.objects.get_or_create(user=user)

            # Automatically log the user in
            login(request, user)
            return redirect("hostel:index")
        else:
            messages.error(request, "There were errors in your form. Please correct them.")

    else:
        form = UserRegisterForm()

    context = {"form": form}
    return render(request, "userauth/signup.html", context)

# Login View
def LoginView(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("hostel:index")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate the user with username and password
        user_auth = authenticate(request, username=username, password=password)
        if user_auth:
            login(request, user_auth)
            messages.success(request, "You are logged in successfully!")
            next_url = request.GET.get("next", "hostel:index")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password")    

    return render(request, "userauth/login.html")

# Logout View
def LogoutView(request):
    logout(request)
    messages.success(request, "You are now logged out")
    return redirect("userauth:login")

@login_required
def home(request):
    return render(request, "userauth/home.html")

def about_us(request):
    return render(request, "userauth/about_us.html")

# Profile View
@login_required
def ProfileView(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            print("Form is valid")
            profile = form.save(commit=False)
            # Optional: Set defaults for missing file uploads
            if not profile.image and not request.FILES.get('image'):
                profile.image = "default.jpg"
            if not profile.proof_image and not request.FILES.get('proof_image'):
                profile.proof_image = "default.jpg"
            profile.save()  # Save the profile instance
            profile.save()
            form.save_m2m() 
            messages.success(request, "Your profile has been successfully updated!")
            return redirect("userauth:profile")
        else:
            # print(form.errors)  # Debugging: Log form errors
            print("Form errors:", form.errors)
            messages.error(request, "There were errors in your submission. Please check the form.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "userauth/profile.html", {"form": form})

# Change Password View
@login_required
def ChangePasswordView(request):
    if request.method == 'POST':
        form = MyPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('userauth:profile')  # Redirect to profile after password change
    else:
        form = MyPasswordChangeForm(user=request.user)

    return render(request, 'userauth/changepassword.html', {'form': form})

@login_required
def StudentDashboardView(request):
    # Get requests and update read status
    requests = Request.objects.filter(student=request.user)
    
    # Mark unread rejections as read
    unread = requests.filter(status='Rejected', read=False)
    unread.update(read=True)

    context = {
        'requests': requests,
        'allocation_data': Allocation.objects.filter(student=request.user).first()
    }
    return render(request, "userauth/student_dashboard.html", context)

@login_required
def OccupiedRoomsView(request):
    form = OccupiedRoomForm(request.POST or None, user=request.user)
    rooms = None
    hostel = None

    if form.is_valid():
        hostel = form.cleaned_data['hostel']
        rooms = Room.objects.filter(block__hostel=hostel)

    context = {
        "form": form,
        "rooms": rooms,
        "hostel": hostel,
    }
    return render(request, "userauth/occupied_rooms.html", context)

@login_required
def RequestRoomView(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        block_id = request.POST.get("block_id")
        hostel_id = request.POST.get("hostel_id")

        # Fetch the relevant models
        room = get_object_or_404(Room, id=room_id)
        block = get_object_or_404(Block, id=block_id)
        hostel = get_object_or_404(Hostel, id=hostel_id)

        # Check if the room has available space
        if room.occupied_beds >= room.capacity:
            messages.error(request, "Room is already full. Please choose another room.")
            return redirect("userauth:occupied_rooms")

        # Check if the user already has an active request for any room
        active_request = Request.objects.filter(
            student=request.user, status="Pending"
        ).first()
        if active_request:
            messages.error(request, "You already have an active room request.")
            return redirect("userauth:occupied_rooms")

        # Check if the room has reached its request limit
        room_request_count = Request.objects.filter(room=room, status="Pending").count()
        if room_request_count >= 10:
            messages.error(request, "This room has reached its request limit. Please choose another room.")
            return redirect("userauth:occupied_rooms")

        # Create a new room request
        Request.objects.create(
            student=request.user,
            room=room,
            block=block,
            hostel=hostel,
            priority="Other",  # Set default or calculate based on user conditions
            status="Pending",
        )
        messages.success(request, "Room request submitted successfully!")
        return redirect("userauth:occupied_rooms")

    messages.error(request, "Invalid request method.")
    return redirect("userauth:occupied_rooms")

# views.py
@login_required
def clear_rejection(request, pk):
    req = get_object_or_404(Request, pk=pk, student=request.user)
    req.read = True
    req.save()
    return redirect("userauth:student_dashboard")    