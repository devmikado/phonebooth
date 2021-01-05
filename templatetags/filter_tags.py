from django import template
import time
register = template.Library()
import datetime

def get_form_name_field_value(dictionary,key):
    # print(dictionary)
    # print(key)
    if key in dictionary: 
        return dictionary[key]['name']
    else:
        return ''

def get_form_description_field_value(dictionary,key):
    # print(dictionary)
    # print(key)
    if key in dictionary: 
        return dictionary[key]['description']
    else:
        return ''


def get_form_short_description_field_value(dictionary,key):
    if key in dictionary:
        return dictionary[key]['short_description']
    else:
        return ''

def get_form_comment_field_value(dictionary, key):
    if key in dictionary:
        return dictionary[key]['comment']
    else:
        return ''

def get_form_user_field_value(dictionary, key):
    if key in dictionary:
        return dictionary[key]['user']
    else:
        return ''



def duration_conversion(val):
    duration = 0
    if val:
        h = int(val)//(60*60)
        m = (int(val)-h*60*60)//60
        s = int(val)-(h*60*60)-(m*60)
        duration = "{0:.0f}:{1:.0f}:{2:.0f}".format(h, m, s)
        # duration = time.strftime('%H:%M:%S', time.gmtime(int(val)))
    return duration

register.filter('get_form_name_field_value', get_form_name_field_value)
register.filter('get_form_comment_field_value', get_form_comment_field_value)
register.filter('get_form_user_field_value', get_form_user_field_value)
register.filter('get_form_description_field_value', get_form_description_field_value)
register.filter('get_form_short_description_field_value', get_form_short_description_field_value)
register.filter('duration_conversion', duration_conversion)