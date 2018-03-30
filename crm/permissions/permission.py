
from django.urls import resolve
from crm.permissions import permission_list
from django.shortcuts import HttpResponse, render, redirect

def perm_check(*args, **kwargs):
    request = args[0]
    if request.user.is_authenticated:
        for permission_name, v in permission_list.perm_dic.items():
            # print(k, v)
            url_matched = False
            if v['url_type'] == 1:
                if v['url'] == request.path:
                    url_matched = True
            else:
                resolve_url_obj = resolve(request.path)
                if resolve_url_obj.url_name == v['url']:
                    url_matched = True

            if url_matched:
                if v['method'] == request.method:
                    arg_matched = True
                    for request_arg in v['args']:
                        request_method_func = getattr(request, v['method'])
                        if not request_method_func.get(request_arg):
                            arg_matched = False

                    if arg_matched:
                        if request.user.has_perm(permission_name):

                            return True

    else:
        return redirect('/account/login/')

def check_permission(func):

    def inner(*args, **kwargs):
        print("--permissions", *args, **kwargs)

        if perm_check(*args, **kwargs):
            return func(*args, **kwargs)
        else:
            return HttpResponse('Have no permissions!')

    return inner