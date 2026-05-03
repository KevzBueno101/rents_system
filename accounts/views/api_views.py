"""
API Views for user-related operations.
Provides RESTful endpoints for username validation and user management.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.services.user_service import UserService


@csrf_exempt
@require_http_methods(["GET"])
def check_username_availability(request):
    """
    API endpoint to check if a username is available.
    
    GET /api/check-username/?username=testuser
    
    Returns:
        {
            "available": true/false,
            "message": "Username is available" or "Username is already taken"
        }
    """
    username = request.GET.get('username', '').strip()
    
    if not username:
        return JsonResponse({
            'available': False,
            'message': 'Username is required'
        }, status=400)
    
    # Check if user is logged in (exclude current user)
    exclude_user_id = None
    if request.user.is_authenticated:
        exclude_user_id = request.user.id
    
    try:
        # Validate username
        validated_username = UserService.validate_username(username, exclude_user_id)
        
        # If validation passes, username is available
        return JsonResponse({
            'available': True,
            'message': 'Username is available'
        })
        
    except Exception as e:
        # Username is not available or invalid
        return JsonResponse({
            'available': False,
            'message': str(e)
        })


@login_required
@require_http_methods(["GET"])
def get_current_user_info(request):
    """
    API endpoint to get current user information.
    
    GET /api/user-info/
    
    Returns:
        {
            "username": "current_username",
            "email": "user@example.com",
            "full_name": "John Doe"
        }
    """
    user = request.user
    
    # Get user profile information
    profile_data = {}
    if hasattr(user, 'tenantprofile'):
        profile = user.tenantprofile
        profile_data = {
            'full_name': profile.full_name,
            'phone': profile.phone,
            'room': profile.get_room_display(),
            'photo_url': profile.photo.url if profile.photo else None
        }
    elif hasattr(user, 'adminprofile'):
        profile = user.adminprofile
        profile_data = {
            'full_name': profile.full_name,
            'phone': profile.phone,
            'photo_url': profile.photo.url if profile.photo else None
        }
    
    return JsonResponse({
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
        **profile_data
    })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_username(request):
    """
    API endpoint to update username.
    
    POST /api/update-username/
    {
        "username": "new_username"
    }
    
    Returns:
        {
            "success": true/false,
            "message": "Username updated successfully" or error message
        }
    """
    import json
    data = json.loads(request.body)
    new_username = data.get('username', '').strip()
    
    if not new_username:
        return JsonResponse({
            'success': False,
            'message': 'Username is required'
        }, status=400)
    
    try:
        # Update username using service layer
        updated_user = UserService.update_username(
            user=request.user,
            new_username=new_username,
            request=request
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Username updated successfully',
            'username': updated_user.username
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
