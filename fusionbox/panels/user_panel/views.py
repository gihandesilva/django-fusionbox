from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.conf import settings
from django.contrib import auth
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

from fusionbox.panels.user_panel.forms import UserForm


def panel_enabled(request):
    return request.session.get('toolbar_user_panel_enabled', False)


def content(request):
    user_dict = {}
    template = 'content.html'
    env = {}

    if request.user.is_authenticated():
        for field in User._meta.fields:
            if field.name == 'password':
                continue
            user_dict[field.attname] = getattr(request.user, field.attname)

    if panel_enabled(request):
        env['display'] = True
        env['form'] = UserForm()
        env['next'] = request.GET.get('next')
        env['users'] = User.objects.all()[:10]
        env['user_dict'] = user_dict
    else:
        env['display'] = False

    return TemplateResponse(request, template, env)


@csrf_exempt
@require_POST
def login(request, **kwargs):
    enabled = panel_enabled(request)
    if not enabled:
        raise PermissionDenied

    if not kwargs:
        form = UserForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest()
        kwargs = form.get_lookup()

    user = get_object_or_404(User, **kwargs)

    user.backend = settings.AUTHENTICATION_BACKENDS[0]
    auth.login(request, user)

    if enabled:
        request.session['toolbar_user_panel_enabled'] = True

    return HttpResponseRedirect(request.POST.get('next', '/'))
