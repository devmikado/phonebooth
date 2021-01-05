from django.conf import settings
import requests
import json
from django.core.paginator import InvalidPage, Paginator

def get_instagram_access_token(code):
    code = "AQB7_fBw5hkaxqzBW4GgKZGPz8umwsuYIB38iaqFUPTpzBv8f5Qm83OHoRsDBefHSwO4L1AfXHTvp25w3hOMEOSM6LdZhVgK0jzhmhtW2gMijMPB22Z-UDKKEyLdJXrQdE2Ih3OrebkkMiqJJIYwe26BBB3UqTdScQcX2JEWpLMP2jEi15k-iyGP5PPiF0-rXYEylRdXksiEnaJQ7c0rA35c_t0kMenUgOWBEFMURCtv4w"
    url = "https://api.instagram.com/oauth/access_token"
    data = {
        'client_id': settings.SOCIAL_AUTH_INSTAGRAM_KEY,
        'client_secret': settings.SOCIAL_AUTH_INSTAGRAM_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.SOCIAL_AUTH_INSTAGRAM_REDIRECT_URL,
        'code': code
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    req = requests.post(url, data=data, headers=headers)
    print(req.json)
    return req.json


def get_paginator_items(items, paginate_by, page_number):
    if not page_number:
        page_number = 1
    paginator = Paginator(items, paginate_by)
    try:
        page_number = int(page_number)
    except Exception as e:
        print(e)

    try:
        items = paginator.page(page_number)
    except InvalidPage as err:
        print(err)
        # raise Http404('Invalid page (%(page_number)s): %(message)s' % {
        #     'page_number': page_number, 'message': str(err)})
    return items