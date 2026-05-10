"""
Public marketing landing (no tenant/staff privilege required).
"""
import logging

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from accounts.forms import LandingContactForm

from .helpers import get_available_rooms

logger = logging.getLogger(__name__)


@require_http_methods(['GET', 'HEAD', 'POST'])
def home_view(request):
    """
    Marketing home with featured available rooms (safe public fields only).

    POST here handles the landing contact inquiry (minimal backend + honeypot).
    """
    form = LandingContactForm()

    if request.method == 'POST':
        honeypot = (request.POST.get('company_site') or '').strip()
        if honeypot:
            messages.success(request, 'Thanks — your message has been received.')
            return redirect(reverse('home'))

        form = LandingContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            logger.info(
                'Landing contact inquiry | name=%r email=%r message=%s',
                data['name'],
                data['email'],
                (data['message'] or '')[:2000],
            )
            messages.success(
                request,
                'Thank you for contacting us. We will respond as soon as we can.',
            )
            return redirect(reverse('home'))

    rooms = list(get_available_rooms())

    return render(
        request,
        'home.html',
        {
            'landing_contact_form': form,
            'featured_rooms': rooms,
            'featured_room_count': len(rooms),
        },
    )
