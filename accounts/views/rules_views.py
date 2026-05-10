from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.cache import cache
from ..models import Rule, TenantProfile, ActivityLog
from ..activity_utils import log_activity


@login_required(login_url='/admin/login/')
def rules_list(request):
    """Admin list of rules with search/filter. Tenant redirects."""
    if not request.user.is_staff:
        return redirect('tenant_rules')
    
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    rules = Rule.objects.all()
    
    if search:
        rules = rules.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    if status_filter:
        rules = rules.filter(is_active=(status_filter == 'active'))
    
    available_tenants = TenantProfile.objects.all()  # For create modal
    
    context = {
        'rules': rules,
        'search': search,
        'status_filter': status_filter,
        'available_tenants': available_tenants,  # Dummy for pattern
    }
    return render(request, 'admin/rules_list.html', context)


@login_required(login_url='/admin/login/')
def create_rule(request):
    """Admin create new rule."""
    if not request.user.is_staff:
        messages.error(request, 'Unauthorized.')
        return redirect('rules_list')
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if title and description:
            rule = Rule.objects.create(title=title, description=description)
            log_activity(
                user=request.user,
                action='rule_created',
                description=f'Created rule: {title}',
                content_type='Rule',
                object_id=rule.id
            )
            messages.success(request, f'Rule "{title}" created successfully.')
            
            # Clear cache for real-time updates
            cache.delete('rules_data')
            
            return redirect('rules_list')
        else:
            messages.error(request, 'Title and description are required.')
    
    return redirect('rules_list')


@login_required(login_url='/admin/login/')
def edit_rule(request, rule_id):
    """Admin edit existing rule."""
    if not request.user.is_staff:
        messages.error(request, 'Unauthorized.')
        return redirect('rules_list')
    
    rule = get_object_or_404(Rule, id=rule_id)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active', 'off') == 'on'
        
        if title and description:
            rule.title = title
            rule.description = description
            rule.is_active = is_active
            rule.save()
            
            log_activity(
                user=request.user,
                action='rule_updated',
                description=f'Updated rule: {title}',
                content_type='Rule',
                object_id=rule.id
            )
            
            messages.success(request, f'Rule "{title}" updated successfully.')
            
            # Clear cache for real-time updates
            cache.delete('rules_data')
            
            return redirect('rules_list')
        else:
            messages.error(request, 'Title and description are required.')
    
    context = {
        'rule': rule,
        'available_tenants': TenantProfile.objects.all(),
    }
    return render(request, 'admin/edit_rule.html', context)


@login_required(login_url='/admin/login/')
def delete_rule(request, rule_id):
    """Admin delete rule."""
    if not request.user.is_staff:
        messages.error(request, 'Unauthorized.')
        return redirect('rules_list')
    
    if request.method == 'POST':
        rule = get_object_or_404(Rule, id=rule_id)
        title = rule.title
        rule.delete()
        log_activity(
            user=request.user,
            action='rule_deleted',
            description=f'Deleted rule: {title}',
            content_type='Rule',
            object_id=rule_id
        )
        messages.success(request, f'Rule "{title}" deleted.')
        
        # Clear cache for real-time updates
        cache.delete('rules_data')
    
    return redirect('rules_list')


# Tenant view
@login_required(login_url='/login/')
def tenant_rules(request):
    """Tenant read-only rules list."""
    if request.user.is_staff:
        return redirect('rules_list')
    
    from django.core.paginator import Paginator
    rules = Rule.objects.filter(is_active=True)
    
    paginator = Paginator(rules, 10)
    page_number = request.GET.get('page')
    rules_page = paginator.get_page(page_number)
    
    context = {
        'rules': rules_page,
        'total_rules': rules.count(),
    }
    return render(request, 'tenant/tenant_rules.html', context)
