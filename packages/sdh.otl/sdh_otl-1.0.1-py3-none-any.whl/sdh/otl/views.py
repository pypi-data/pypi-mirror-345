from django.shortcuts import Http404
from django.http import HttpResponseRedirect

from .generator import OneTimeLink


def otl_view(request, otp_key):
    try:
        otl = OneTimeLink.get(otp_key)
    except KeyError:
        raise Http404

    if otl.cb_function:
        rc = otl.cb_function(request, **otl.context)
        if rc:
            return rc

    return HttpResponseRedirect(otl.redirect_url)
