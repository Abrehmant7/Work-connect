from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


ACTIVE_STATUSES = ['applied', 'reviewing', 'shortlisted', 'interviewing']
ACTIVE_PROPOSAL_STATUSES = ['submitted', 'reviewing']


def is_representative(user):
    return user.user_type == 'representative'


def is_applicant(user):
    return user.user_type == 'applicant'


def has_applicant_profile(user):
    return hasattr(user, 'applicant_profile')


def has_representative_profile(user):
    return hasattr(user, 'representative_profile')


def representative_required(view_func=None, redirect_url="/", message="Access denied"):
    if view_func is None:
        return lambda actual_view: representative_required(
            actual_view, redirect_url, message
        )

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_representative(request.user):
            error_msg = message or "You are not allowed to access this page!"
            messages.error(request, error_msg)
            return redirect(redirect_url)
        return view_func(request, *args, **kwargs)

    return wrapper


def representative_profile_required(view_func=None, redirect_url="/", message="Access denied"):
    if view_func is None:
        return lambda actual_view: representative_profile_required(
            actual_view, redirect_url, message
        )

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'representative_profile', None)

        if not profile:
            error_msg = message or "You have to create profile first!"
            messages.error(request, error_msg)
            return redirect("representative_profile")
        return view_func(request, *args, **kwargs)

    return wrapper


def applicant_required(view_func=None, redirect_url="/", message="Access denied"):
    if view_func is None:
        return lambda actual_view: applicant_required(
            actual_view, redirect_url, message
        )

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_applicant(request.user):
            error_msg = message or "You are not allowed to access this page!"
            messages.error(request, error_msg)
            return redirect(redirect_url)
        return view_func(request, *args, **kwargs)

    return wrapper


def applicant_profile_required(view_func=None, redirect_url="/", message="Access denied"):
    if view_func is None:
        return lambda actual_view: applicant_profile_required(
            actual_view, redirect_url, message
        )

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'applicant_profile', None)

        if not profile:
            error_msg = message or "You have to create profile first!"
            messages.error(request, error_msg)
            return redirect("applicant_profile")
        return view_func(request, *args, **kwargs)

    return wrapper
