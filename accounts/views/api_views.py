"""
API Views for user-related operations.
Provides RESTful endpoints for username validation and user management.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.services.user_service import UserService
from django.core.cache import cache

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
        }, status=500)



@login_required
def api_tenant_dashboard_data(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        from tenant.services.dashboard_service import get_tenant_dashboard_data
        from django.utils import timezone
        from decimal import Decimal
        
        data = get_tenant_dashboard_data(request.user)
        
        # Serialize only safe, primitive values
        summary = data.get('summary', {})
        enhanced = data.get('enhanced_status', {})
        next_bill = summary.get('next_bill')
        latest_payment = data.get('latest_payment')
        
        safe_data = {
            'balance': float(data.get('balance') or 0),
            'payment_status': data.get('payment_status', 'no_bill'),
            'payment_status_label': data.get('payment_status_label', 'No bill'),
            'due_date': str(data['due_date']) if data.get('due_date') else None,
            'last_updated': timezone.now().isoformat(),
            'summary': {
                'total_billed': float(summary.get('total_billed') or 0),
                'total_paid': float(summary.get('total_paid') or 0),
                'has_overdue': summary.get('has_overdue', False),
                'is_overdue': summary.get('is_overdue', False),
                'days_until_due': summary.get('days_until_due'),
                'next_bill': {
                    'due_date': str(next_bill.due_date),
                    'bill_number': next_bill.bill_number,
                } if next_bill else None,
            },
            'enhanced_status': {
                'total_bills': enhanced.get('total_bills', 0),
                'paid_bills': enhanced.get('paid_bills', 0),
                'pending_bills': enhanced.get('pending_bills', 0),
                'has_urgent_payment': enhanced.get('has_urgent_payment', False),
            },
            'latest_payment': {
                'payment_date': str(latest_payment.payment_date),
                'amount': float(latest_payment.amount),
            } if latest_payment else None,
            'unread_notifications': data.get('unread_notifications', 0),
        }
        
        return JsonResponse({'success': True, **safe_data})
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'detail': traceback.format_exc()
        }, status=500)
@login_required
@require_POST
def api_force_dashboard_refresh(request):
    """Force dashboard refresh for all connected clients."""
    
    try:
        # Clear cache for this user
        cache_key = f'tenant_dashboard_{request.user.id}'
        cache.delete(cache_key)
        
        return JsonResponse({
            'success': True,
            'message': 'Dashboard cache cleared'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
