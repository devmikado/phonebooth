from django.http import Http404, HttpResponseRedirect
from social_django.models import UserSocialAuth

def type_wise_user_redirect(function):
    """
    Decorator for views that checks and redirect user according to its tye
    to the log-in page if necessary.
    """
    def wrap(request, *args, **kwargs):
        
        
        if request.user.is_authenticated:
            if request.user.is_staff:
                return HttpResponseRedirect("/nationality/dashboard/")
            else:
                social_logins = UserSocialAuth.objects.filter(user=request.user)
                print(social_logins)
                if social_logins:
                    return HttpResponseRedirect("/customer/customer-dashboard/")
                else:
                    return HttpResponseRedirect("/customer/social-accounts/")
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

