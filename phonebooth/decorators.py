
from django.shortcuts import render, redirect

def is_superuser(function):
    def wrap(request, *args, **kwargs):
        if  request.user.is_superuser == True:
            return function(request, *args, **kwargs)
        else:
            # raise PermissionDenied
            return redirect('/')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def is_customer(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser == False:
            return function(request, *args, **kwargs)
        else:
            # raise PermissionDenied
            return redirect('/')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap