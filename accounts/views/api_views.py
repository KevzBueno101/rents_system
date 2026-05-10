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
from ..models import Rule
from django.utils import timezone

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


@login_required(login_url='/login/')
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
@login_required(login_url='/login/')
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
    """API endpoint for real-time dashboard data."""
    
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        from tenant.services.dashboard_service import get_tenant_dashboard_data
        from django.utils import timezone
        
        data = get_tenant_dashboard_data(request.user)
        
        summary = data.get('summary', {})
        enhanced = data.get('enhanced_status', {})
        next_bill = summary.get('next_bill')
        latest_payment = data.get('latest_payment')
        
        # Serialize only safe primitive values — no model objects or Decimals
        safe_data = {
            'balance': float(data.get('balance') or 0),
            'payment_status': data.get('payment_status', 'no_bill'),
            'payment_status_label': data.get('payment_status_label', 'No bill'),
            'due_date': str(data['due_date']) if data.get('due_date') else None,
            'last_updated': timezone.now().isoformat(),
            'summary': {
                'total_billed': float(summary.get('total_billed') or 0),
                'total_paid': float(summary.get('total_paid') or 0),
                'has_overdue': bool(summary.get('has_overdue', False)),
                'is_overdue': bool(summary.get('is_overdue', False)),
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
                'has_overdue': bool(enhanced.get('overdue_bills', 0) > 0),
                'has_urgent_payment': bool(enhanced.get('has_urgent_payment', False)),
            },
            'latest_payment': {
                'payment_date': str(latest_payment.payment_date),
                'amount': float(latest_payment.amount),
            } if latest_payment else None,
            'unread_notifications': data.get('unread_notifications', 0),
            'room': {
                'room_code': data['room'].room_code,
                'monthly_rate': float(data['room'].monthly_rate),
            } if data.get('room') else None,
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


@csrf_exempt
@login_required(login_url='/login/')
@require_http_methods(["GET"])
def api_rules_data(request):
    """
    API endpoint to get rules data for real-time synchronization.
    
    GET /api/rules-data/
    
    Returns:
        {
            "rules": [
                {
                    "id": 1,
                    "title": "Rule Title",
                    "description": "Rule Description",
                    "is_active": true,
                    "created_at": "2023-05-05T10:30:00Z",
                    "updated_at": "2023-05-05T10:30:00Z"
                }
            ],
            "total_count": 5,
            "last_updated": "2023-05-05T10:30:00Z"
        }
    """
    try:
        # Get cache key for rules
        cache_key = 'rules_data'
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data)
        
        # Get rules from database
        if request.user.is_staff:
            # Admin gets all rules
            rules = Rule.objects.all()
        else:
            # Tenant gets only active rules
            rules = Rule.objects.filter(is_active=True)
        
        # Convert to list of dictionaries
        rules_data = []
        for rule in rules:
            rules_data.append({
                'id': rule.id,
                'title': rule.title,
                'description': rule.description,
                'is_active': rule.is_active,
                'created_at': rule.created_at.isoformat(),
                'updated_at': rule.updated_at.isoformat(),
            })
        
        # Get latest update timestamp
        latest_update = rules.order_by('-updated_at').first()
        last_updated = latest_update.updated_at.isoformat() if latest_update else timezone.now().isoformat()
        
        # Prepare response data
        response_data = {
            'rules': rules_data,
            'total_count': rules.count(),
            'last_updated': last_updated,
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, response_data, 300)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to fetch rules data',
            'message': str(e)
        }, status=500)
