from .models import AdminProfile

def admin_profile(request):
    if request.user.is_authenticated and request.user.is_staff:
        try:
            profile = request.user.adminprofile
        except AdminProfile.DoesNotExist:
            profile = None
    else:
        profile = None

    return {'admin_profile': profile}