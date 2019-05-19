from django.shortcuts import render,reverse
from .models import ManagerMessage,roles
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from goods.models import GoodsInfro
from user.models import orders,comment,users
from django.core.paginator import Paginator
from django.db.models import Q
import datetime
import json
from ZSHOP.check_power import check_power
import urllib.request
import hashlib
# 卖家后台登录页面显示
def login(request):
    return render(request,'manager/login.html')

#卖家后台登录提交操作
def dologin(request):
    username = request.POST['username']
    password = request.POST['password']

    user = ManagerMessage.objects.filter(username=username,userpass=password)
    if user:
        request.session['username'] = username
        request.session['user_id'] = user[0].id
        user_power_list = []
        for filiation in user[0].role.power_roles_set.filter():
            user_power_list.append(filiation.power.url)
        # print(user_power_list)
        request.session['user_power_list'] = user_power_list

        return HttpResponseRedirect('/manager/main')
    else:
        return HttpResponse('用户名或密码错误')

#显示商品后台管理页面
def main(request):
    #查询所有商品 条件：商户Id是当前登录用户的Id
    data_count = GoodsInfro.objects.filter(manager_id=request.session.get('user_id')).count()
    #查询订单数
    order_count=orders.objects.filter().count()
    #查询会员数
    vip_count=users.objects.filter().count()
    return render(request,'manager/main.html',{'count':data_count,'order_count':order_count,'vip_count':vip_count})

#退出
def loginout(request):
    #清空session
    request.session.clear()
    #重定向到登录页面  不用render遵循业务逻辑，不能只看重实现效果
    return HttpResponseRedirect(reverse('manager:login'))

# 后台订单管理
def order_list(request):
    p = request.GET.get('p', 1)
    order_code = request.GET.get('order_code', '')
    pay_status = request.GET.get('pay_status', '99')
    send_status = request.GET.get('send_status', '99')

    manager_id = request.session.get('user_id', 0)
    if manager_id == 0:
        return HttpResponseRedirect('/manager/login')

    where = []
    view_where = {}
    q = Q()
    q.connector = 'and'
    q.children.append(('manage_id', manager_id))
    if order_code != '':
        q.children.append(('order_code', order_code))
        where.append('order_code=' + order_code)
        view_where['order_code'] = order_code

    if pay_status != '99':
        q.children.append(('pay_status', pay_status))
        where.append('pay_status=' + pay_status)
        view_where['pay_status'] = pay_status

    if send_status != '99':
        q.children.append(('send_status', send_status))
        where.append('send_status=' + send_status)
        view_where['send_status'] = send_status

    url_where = '&'.join(where)  # 拼接分页连接的参数

    orderList = orders.objects.filter(q).order_by('id')  # 查询

    pageObj = Paginator(orderList, 2)  # 第一个数据  第二参数每页多少条数据
    data = pageObj.page(p)  # p是页码

    return render(request, 'manager/order_list.html',
                  {'orderList': data, 'url_where': url_where, 'view_where': view_where})

# 订单详情
def order_info(request):
    #订单ID
    order_id=request.GET.get('order_id',0)
    if order_id==0:
        return HttpResponse('请选择要查看的订单')

    manager_id = request.session.get('user_id',0)
    if manager_id==0:
        return HttpResponseRedirect('/manager/login')

    info  = orders.objects.filter(id=order_id,manage_id=manager_id).first()
    if info==None:
        return HttpResponse('订单不存在')

    return render(request,'manager/order_info.html',{'info':info})

# 修改发货状态 发短信
def edit_send_status(request):
    order_id = request.POST.get('order_id', 0)
    tel=request.POST.get('tel',0)
    receiver=request.POST.get('receiver')
    num=request.POST.get('order_code')
    if order_id == 0:
        return HttpResponse('请选择要发货的订单')

    manager_id = request.session.get('user_id', 0)
    if manager_id == 0:
        return HttpResponseRedirect(reverse('manager:login'))
    bool = orders.objects.filter(id=order_id).update(send_status=1, send_time=datetime.datetime.now())
    if bool:
        def md5(str):
            m = hashlib.md5()
            m.update(str.encode("utf8"))
            return m.hexdigest()

        statusStr = {
            '0': '短信发送成功',
            '-1': '参数不全',
            '-2': '服务器空间不支持,请确认支持curl或者fsocket,联系您的空间商解决或者更换空间',
            '30': '密码错误',
            '40': '账号不存在',
            '41': '余额不足',
            '42': '账户已过期',
            '43': 'IP地址限制',
            '50': '内容含有敏感词'
        }

        smsapi = "http://api.smsbao.com/"
        # 短信平台账号
        user = '18703249138'
        # 短信平台密码
        password = md5('zxc123')
        # 要发送的短信内容
        # num = 123123123
        content = '    亲爱的 '+receiver+' ,您的订单 : ' + str(num) + '已发货,请您注意及时查收！'
        # 要发送短信的手机号码
        phone = tel

        data = urllib.parse.urlencode({'u': user, 'p': password, 'm': phone, 'c': content})
        send_url = smsapi + 'sms?' + data
        response = urllib.request.urlopen(send_url)
        the_page = response.read().decode('utf-8')
        print(statusStr[the_page])
        return HttpResponseRedirect(reverse('manager:order_list'))
    else:
        return HttpResponse('修改失败')

# 查询待审核数据
def comment_list(request):
    score = request.GET.get('score', '0')
    p = request.GET.get('p', 1)
    manager_id = request.session.get('user_id', 0)

    if manager_id == 0:
        return HttpResponseRedirect('/manager/login')

    where = []
    view_where = {}
    q = Q()
    q.connector = 'and'
    q.children.append(('manager_id', manager_id))

    if score != '0':
        q.children.append(('score', score))
        where.append('score=' + score)  # 分页连接 上保留检索条件
        view_where['score'] = score

    q.children.append(('status', 0))

    url_where = '&'.join(where)  # 拼接分页连接的参数

    comment_list = comment.objects.filter(q)
    print(comment_list.query)
    pageObj = Paginator(comment_list, 1)
    data = pageObj.page(p)

    return render(request, 'manager/comment_list.html',
                  {'comment_list': data, 'url_where': url_where, "view_where": view_where})


# 查询待审核数据
def comment_list_yes(request):
    score = request.GET.get('score', '0')
    p = request.GET.get('p', 1)
    manager_id = request.session.get('user_id', 0)

    if manager_id == 0:
        return HttpResponseRedirect('/manager/login')

    where = []
    view_where = {}
    q = Q()
    q.connector = 'and'
    q.children.append(('manager_id', manager_id))

    if score != '0':
        q.children.append(('score', score))
        where.append('score=' + score)  # 分页连接 上保留检索条件
        view_where['score'] = score

    q.children.append(('status', 1))

    url_where = '&'.join(where)  # 拼接分页连接的参数

    comment_list = comment.objects.filter(q)
    print('123123123123')
    pageObj = Paginator(comment_list, 1)
    data = pageObj.page(p)

    return render(request, 'manager/comment_list_yes.html',
                  {'comment_list': data, 'url_where': url_where, "view_where": view_where})


def check_comment(request):
    comment_id = request.POST.get('comment_id', 0)
    data = {}
    if comment_id == 0:
        data['status'] = 1
        data['msg'] = '请选择要审核的评价'
        return HttpResponse(json.dumps(data))

    # 修改状态
    bool = comment.objects.filter(id=comment_id).update(status=1)

    if bool:
        data['status'] = 1
        data['msg'] = '修改成功'
        return HttpResponse(json.dumps(data))
    else:
        data['status'] = 0
        data['msg'] = '修改失败'
        return HttpResponse(json.dumps(data))

def edit_count(request, g_id):
    goods_info = GoodsInfro.objects.filter(id=g_id).first()
    return render(request, 'manager/edit_count.html', {'goods_info': goods_info})

def do_edit_count(request, g_id):
    count = request.POST.get('count', 0)
    bool = GoodsInfro.objects.filter(id=g_id).update(goods_count=count)
    data = {}
    if bool:
        data['status'] = 1
        data['msg'] = '修改成功'
        return JsonResponse(data)
    else:
        data['status'] = 0
        data['msg'] = '修改失败'
        return JsonResponse(data)

# 用户列表
@check_power
def member_list(request):
    # 查询所有用户信息

    user_name = request.GET.get('user_name', '')
    role = request.GET.get('role', '99')
    p = request.GET.get('p', 1)
    # print(p)
    q = Q()
    q.connector = 'and'

    where = []
    view_where = {}

    if user_name != '':
        q.children.append(('username', user_name))
        where.append('username=' + user_name)  # 分页连接 上保留检索条件
        view_where['username'] = user_name

    if role != '99':
        q.children.append(('role', role))
        where.append('role=' + role)  # 分页连接 上保留检索条件
        view_where['role'] = role

    print(view_where)
    url_where = '&'.join(where)  # 拼接分页连接的参数

    data = ManagerMessage.objects.filter(q).order_by('id')
    # print(data.query)

    pageObj = Paginator(data, 5)
    list = pageObj.page(p)

    # 查询角色列表
    role_list = roles.objects.filter(disabled=0)

    return render(request, 'manager/member_list.html',
                  {'list': list, 'url_where': url_where, 'view_where': view_where, 'role_list': role_list})


# 显示修改用户页面
def member_edit(request):
    member_id = request.GET.get('member_id', 0)
    member_info = ManagerMessage.objects.filter(id=member_id).first()

    # 查询角色列表
    role_list = roles.objects.filter(disabled=0)

    return render(request, 'manager/member_edit.html', {'member_info': member_info, 'role_list': role_list})


# 执行修改操作
def do_member_edit(request):
    id = request.POST.get('id')
    username = request.POST.get('username')
    userpass=request.POST.get('userpass')
    role = request.POST.get('role')

    memberObj = ManagerMessage()
    memberObj.id = id
    memberObj.username = username
    memberObj.userpass = userpass
    memberObj.role_id = role
    memberObj.save()

    data = {}
    data['status'] = 1
    data['msg'] = '修改成功'
    return JsonResponse(data)

#删除用户
def member_del(request):
    id = request.GET.get('id')
    bool = ManagerMessage.objects.filter(id=id).delete()

    data = {}
    if bool:
        data['status'] = 1
        data['msg'] = '删除成功'
    else:
        data['status'] = 0
        data['msg'] = '删除失败'

    return JsonResponse(data)

def member_add(request):
    role_list = roles.objects.filter(disabled=0)
    return render(request,'manager/member_add.html',{'role_list': role_list})

def do_member_add(request):
    username = request.POST.get('username')
    userpass = request.POST.get('userpass')
    role = request.POST.get('role')
    ManagerMessage.objects.create(username=username,userpass=userpass,role_id=role)

    data = {}
    data['status'] = 1
    data['msg'] = '添加成功'
    return JsonResponse(data)
