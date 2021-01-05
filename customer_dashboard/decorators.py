from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect

def login_required(function):
    """
    Decorator for views that checks and redirect user according to its tye
    to the log-in page if necessary.
    """
    def wrap(request, *args, **kwargs):
        
        
        if request.user.is_anonymous:
            print("--------------------if--------------------->")
            return redirect("/")
        else:
            print("----------------------else------------------->")
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap