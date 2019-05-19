from django.http import HttpResponse
from manager.models import power


def check_power(func):
    def inner_fun(request):
        visit_url = request.resolver_match.url_name
        # print(visit_url)
        power_info = power.objects.filter(url=visit_url).first()
        if power_info != None:
            user_power_list = request.session.get('user_power_list')
            # print(user_power_list)
            if visit_url not in user_power_list:
                return HttpResponse('您没有访问该方法的权限')

        result = func(request)
        return result

    return inner_fun
