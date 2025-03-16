from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm, PasswordResetForm
from userauth.models import User, Profile, Condition, Level, GENDER, Hostel, Block, Room, Request, models


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'password1': 'Password',
            'password2': 'Password Confirmation',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter your username', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter your password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password', 'class': 'form-control'})


class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput(attrs={'autofocus': 'True', 'autocomplete': 'current-password', 'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'})
    )


class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))


class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'})
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "image",
            "fullname",
            "mobile",
            "level",
            "gender",
            "address",
            "conditions",
            "other_health_challenges",
            "matric_number",
            "proof_image",
            "next_of_kin",
            "next_of_kin_mobile",
        ]
        widgets = {
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "fullname": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter full name"}),
            "mobile": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter mobile number"}),
            "level": forms.Select(attrs={"class": "form-select"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter your address"}),
              "conditions": forms.CheckboxSelectMultiple(attrs={"class": "form-check"}),  # Change to CheckboxSelectMultiple
            "other_health_challenges": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Describe other health challenges (if any)"}
            ),
            "matric_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter matric number"}),
            "proof_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "next_of_kin": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter next of kin's name"}),
            "next_of_kin_mobile": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter next of kin's mobile number"}
            ),
        }
        help_texts = {
            "proof_image": "Submit doctor's reports, executive IDs, or any other form of proof.",
        }
    # def __init__(self, *args, **kwargs):
    #     super(ProfileForm, self).__init__(*args, **kwargs)
    #     # Ensure 'conditions' is rendered as radio buttons with additional styling
    #     self.fields['conditions'].widget = forms.RadioSelect(attrs={"class": "form-check"})
    #     self.fields['conditions'].label = "Select Condition"  # Customize the label text if needed
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile")
        if len(mobile) != 11 or not mobile.isdigit():
            raise forms.ValidationError("Enter a valid 11-digit mobile number.")
        return mobile
    
    def clean_conditions(self):
        conditions = self.cleaned_data.get('conditions')
        if not conditions:
            raise forms.ValidationError("Please select at least one health condition.")
        return conditions
        # Custom validation or handling if needed
    
    def clean_next_of_kin_mobile(self):
        next_of_kin_mobile = self.cleaned_data.get("next_of_kin_mobile")
        if len(next_of_kin_mobile) != 11 or not next_of_kin_mobile.isdigit():
            raise forms.ValidationError("Enter a valid 11-digit mobile number.")
        return next_of_kin_mobile

# class OccupiedRoomForm(forms.Form):
#     gender = forms.ChoiceField(choices=GENDER, label="Gender")
#     hostel = forms.ModelChoiceField(queryset=Hostel.objects.all(), label="Hostel")
#     level = forms.ModelChoiceField(queryset=Level.objects.all())
class OccupiedRoomForm(forms.Form):
    hostel = forms.ModelChoiceField(
        queryset=Hostel.objects.none(),
        label="Hostel",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(OccupiedRoomForm, self).__init__(*args, **kwargs)
        if user and hasattr(user, 'profile'):
            profile = user.profile
            self.fields['hostel'].queryset = Hostel.objects.filter(
                gender=profile.gender,
                assigned_levels__name=profile.level
            )    

class RequestRoomForm(forms.Form):
    gender = forms.ChoiceField(
        choices=GENDER,
        label="Gender",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    hostel = forms.ModelChoiceField(
        queryset=Hostel.objects.all(),
        label="Preferred Hostel",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    
    special_request = forms.CharField(
         label="Special Requests or Conditions (Optional)",
         required=False,
         widget=forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Specify any special requests or conditions"})
    )    
    block = forms.ModelChoiceField(
        queryset=Block.objects.none(),  # Initially empty
        label="Preferred Block",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.none(),  # Initially empty
        label="Preferred Room",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'hostel' in self.data:
            try:
                hostel_id = int(self.data.get('hostel'))
                self.fields['block'].queryset = Block.objects.filter(hostel_id=hostel_id)
            except (ValueError, TypeError):
                pass  # Invalid input, keep queryset empty
        if 'block' in self.data:
            try:
                block_id = int(self.data.get('block'))
                self.fields['room'].queryset = Room.objects.filter(block_id=block_id, occupied_beds__lt=models.F('capacity'))
            except (ValueError, TypeError):
                pass  # Invalid input, keep queryset empty
# class RequestRoomForm(forms.Form):
#     gender = forms.ChoiceField(
#         choices=GENDER,
#         label="Gender",
#         widget=forms.Select(attrs={"class": "form-select"})
#     )
#     hostel = forms.ModelChoiceField(
#         queryset=Hostel.objects.all(),
#         label="Preferred Hostel",
#         widget=forms.Select(attrs={"class": "form-select"})
#     )
#     block = forms.ModelChoiceField(
#         queryset=Block.objects.all(),
#         label="Preferred Block",
#         widget=forms.Select(attrs={"class": "form-select"})
#     )
#     room_number = forms.CharField(
#         label="Preferred Room Number",
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter preferred room number (e.g., 101, 202)"})
#     )
#     special_request = forms.CharField(
#         label="Special Requests or Conditions (Optional)",
#         required=False,
#         widget=forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Specify any special requests or conditions"})
#     )
#     priority = forms.ChoiceField(
#         choices=Request.PRIORITY_CHOICES,
#         label="Priority Level",
#         widget=forms.Select(attrs={"class": "form-select"}),
#         initial='Other',
#         help_text="Select the priority level for your room request"
#     )

#     def clean_block(self):
#         block = self.cleaned_data.get("block")
#         if block:
#             block_name = block.name.upper()  # Accessing the block's name field
#             if block_name not in ["A", "B", "C", "D"]:
#                 raise forms.ValidationError("Invalid block. Please enter A, B, C, or D.")
#             return block
#         return block

#     def clean_room_number(self):
#         room_number = self.cleaned_data.get("room_number")
#         if not room_number.isdigit():
#             raise forms.ValidationError("Room number must be numeric.")
#         return room_number

#     def clean(self):
#         cleaned_data = super().clean()
#         hostel = cleaned_data.get("hostel")
#         block = cleaned_data.get("block")
#         room_number = cleaned_data.get("room_number")

#         # Check room availability
#         room = Room.objects.filter(block__hostel=hostel, block__name=block, name=room_number).first()
#         if room and room.occupied_beds >= room.capacity:
#             raise forms.ValidationError(f"The selected room {room_number} in Block {block} is already full. Please choose another room.")

#         return cleaned_data
