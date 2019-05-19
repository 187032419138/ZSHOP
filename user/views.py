from django.shortcuts import render, HttpResponse, HttpResponseRedirect, reverse,render_to_response
from .models import users, car, user_address, order_info, orders, comment
from goods.models import GoodsInfro
import hashlib
import json
import random
import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.mail import send_mail
import time
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest


# 显示登录页
def login(request):
    return render(request, 'user/login.html')


# 显示注册页
def reg(request):
    return render(request, 'user/reg.html')


# 执行注册方法
def doreg(request):
    username = request.POST.get('username')
    password = request.POST.get('userpass')
    email=request.POST.get('email','')

    md = hashlib.md5()
    md.update(password.encode('utf-8'))
    md5_password = md.hexdigest()
    userObj=users()
    userObj.username=username
    userObj.password=md5_password
    userObj.email=email
    userObj.save()
    request.session['temp_id']=userObj.id
    return HttpResponseRedirect(reverse('user:send_msg_view'))
#跳转邮箱页
def send_msg_view(request):
    uid=request.session.get('temp_id',0)
    info = users.objects.filter(id=uid).first()
    return render(request,'user/send_message.html',{'info':info})

# 检查用户是否存在
def check_user(request):
    username = request.GET.get('username')
    # 检查数据库 验证用户名是否存在
    info = users.objects.filter(username=username).first()
    # 返回结果
    if info != None:
        return HttpResponse('1')
    else:
        return HttpResponse('0')


# 登录
def dologin(request):
    username = request.POST.get('username')
    password = request.POST.get('userpass')

    # 查询数据库 比对用户名和密码
    info = users.objects.filter(username=username).first()
    if info != None:
        md = hashlib.md5()
        md.update(password.encode('utf-8'))
        md5_password = md.hexdigest()
        if info.password == md5_password:
            request.session['U_userid'] = info.id
            request.session['U_username'] = info.username
            return HttpResponseRedirect('/goods/index')
        else:
            return HttpResponse('用户不存在或密码错误')
    else:
        return HttpResponse('用户不存在或密码错误')


# 登出
def logout(request):
    request.session.clear()
    return HttpResponseRedirect('/user/login')


# 加入购物车
def add_car(request):
    goods_id = request.POST.get('goods_id', 0)
    number = request.POST.get('count', 0)
    # 安全验证
    if goods_id == 0:
        return HttpResponse('你要买啥？')

    if number == 0:
        return HttpResponse('真的要买？ 数量不能是0')

    user_id = request.session.get('U_userid', 0)

    if user_id == 0:
        return HttpResponseRedirect('/user/login')

    # 判断商品是否已存于购物车
    exists = car.objects.filter(goods_id=goods_id, users_id=user_id).first()
    if exists == None:
        car.objects.create(goods_id=goods_id, users_id=user_id, number=number)
    else:
        exists.number = exists.number + int(number)
        exists.save()

    return HttpResponseRedirect('/user/car_list')


# 购物车列表 显示购物车内的商品
def car_list(request):
    user_id = request.session.get('U_userid', 0)
    if user_id == 0:
        return HttpResponseRedirect('/user/login')

    list = car.objects.filter(users_id=user_id)

    return render(request, 'user/cart_list.html', {'car_list': list})


# 修改购物车商品的数量
def edit_num(request):
    goods_id = request.POST.get('goods_id', 0)
    number = request.POST.get('number', 0)
    type = request.POST.get('type', 0)

    data = {}

    if goods_id == 0:
        data['status'] = 0
        data['msg'] = '商品ID不能为空'
        return HttpResponse(json.dumps(data))

    if number == 0:
        data['status'] = 0
        data['msg'] = '数量不能为空'
        return HttpResponse(json.dumps(data))

    user_id = request.session.get('U_userid', 0)

    if user_id == 0:
        data['status'] = 0
        data['msg'] = '请登录'
        return HttpResponse(json.dumps(data))
    # 操作数据库
    if type == 'reduce':
        number = int(number) - 1
    else:
        number = int(number) + 1

    good_info = GoodsInfro.objects.filter(id=goods_id).first()
    if good_info.goods_count < number:
        data['status'] = 0  # 0 失败  1成功
        data['msg'] = '库存不足'
        data['number'] = number
        return HttpResponse(json.dumps(data))
    bool = car.objects.filter(goods_id=goods_id, users_id=user_id).update(number=number)
    if bool:
        data['status'] = 1
        data['msg'] = '操作成功'
        data['number'] = number
        return HttpResponse(json.dumps(data))
    else:
        data['status'] = 0
        data['msg'] = '操作失败，请稍后再试'
        return HttpResponse(json.dumps(data))


# 删除购物车商品
def del_car(request):
    goods_id = request.POST.get('goods_id', 0)
    data = {}
    if goods_id == 0:
        data['status'] = 0
        data['msg'] = '商品ID不能为空'
        return HttpResponse(json.dumps(data))
    user_id = request.session.get('U_userid', 0)

    if user_id == 0:
        data['status'] = 2
        data['msg'] = '请登录'
        data['data'] = '/user/login'
        return HttpResponse(json.dumps(data))
    bool = car.objects.filter(goods_id=goods_id, users_id=user_id).delete()
    if bool:
        data['status'] = 1
        data['msg'] = '操作成功'
        return HttpResponse(json.dumps(data))
    else:
        data['status'] = 0
        data['msg'] = '操作失败，请稍后再试'
        return HttpResponse(json.dumps(data))


# 清空购物车
def clear_car(request):
    user_id = request.session.get('U_userid', 0)
    data = {}
    if user_id == 0:
        data['status'] = 2  # 0 失败  1成功
        data['msg'] = '请登录'
        data['data'] = '/user/login'
        return HttpResponse(json.dumps(data))

    bool = car.objects.filter(users_id=user_id).delete()
    if bool:
        data['status'] = 1  # 0 失败  1成功
        data['msg'] = '操作成功'
        return HttpResponse(json.dumps(data))
    else:
        data['status'] = 0  # 0 失败  1成功
        data['msg'] = '操作失败，请稍后再试！'
        return HttpResponse(json.dumps(data))


# 下单 确认页面
def place_order(request):
    # 查询数据 渲染页面

    # 所有的购物车信息
    user_id = request.session.get('U_userid', 0)
    if user_id == 0:
        return HttpResponseRedirect('/user/login')

    list = car.objects.filter(users_id=user_id)

    total = 0
    for cart in list:
        total += cart.number * int(cart.goods.goods_xprice)
    print(total)
    # 查询用户所有的收货地址
    address_list = user_address.objects.filter(users_id=user_id)

    return render(request, 'user/order.html', {'car_list': list, 'total_money': total, 'address_list': address_list})


# 确认订单操作
def do_place_order(request):
    address_id = request.POST.get('address', 0)
    if address_id == 0:
        return HttpResponse('请选择收货地址')

    user_id = request.session.get('U_userid', 0)
    if user_id == 0:
        return HttpResponseRedirect('/user/login')
    # 根据收货地址的ID 查询详细信息
    address_info = user_address.objects.filter(id=address_id, users_id=user_id).first()  #
    if address_info == None:
        return HttpResponse('请选择收货地址')

    # 查询购物车内所有的数据，计算金额
    car_list = car.objects.filter(users_id=user_id)

    if not car_list:  #
        return HttpResponse('请选择要结算的商品')

    total_money = 0  # 计算总金额
    manage_id = 0
    manage_name = ''
    goods_name_all = ''
    for cart in car_list:
        total_money += cart.number * int(cart.goods.goods_xprice)
        manage_id = cart.goods.manager_id  # 多个商品 最后一个覆盖前边的结果
        goods_name_all += cart.goods.goods_name
        goods_info = GoodsInfro.objects.filter(id=cart.goods_id).first()
        if goods_info.goods_count < cart.number:
            return message(goods_info.goods_name + "库存不足，请重新选择<a href='%s'>返回购物车</a>" % (reverse('user:car_list')))

    # 创建订单
    orderObj = orders()
    orderObj.order_code = '20181010' + str(random.randint(100000, 999999))
    orderObj.money = total_money
    orderObj.users_id = user_id
    # orderObj.add_time = user_id
    orderObj.address = address_info.address
    orderObj.phone = address_info.phone
    orderObj.contacts = address_info.name
    orderObj.manage_id = manage_id
    orderObj.save()
    # 订单详情表
    for cart in car_list:
        orderinfoObj = order_info()
        orderinfoObj.order_id = orderObj.id
        # orderObj.order=orderObj
        orderinfoObj.number = cart.number
        orderinfoObj.goods_id = cart.goods_id
        orderinfoObj.price = cart.goods.goods_xprice
        orderinfoObj.save()
    # 清空购物车
    car.objects.filter(users_id=user_id).delete()
    # 支付
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = 'https://openapi.alipaydev.com/gateway.do'  #
    alipay_client_config.app_id = '2016092100561606'
    alipay_client_config.app_private_key ='MIIEowIBAAKCAQEAvAQeli6bj2kPQBlZmqic8bbfPo29J9XIE/NQM1QhcFU/lAcZpleGm38Y+9XnpUN3k2cxIn49GZTTwsSJ0kX6SSBWLkGZOs3RpaLsrgOtkuT1DIXzvoTDe5Q88Hf/5XQJ3GStJnn1ZRnBqokzRUExbTUnuSW+nQftl6Bv/Xh4Ov5L6GPDfesbTG8SQsZYibXREmvoB7cpcQuz8Ci7MJanDASU3aUHTh2jOe27F3F4cPRDE8XNjoDPcW4CqViXwNZvBXH6phNEzFmDpPcPWSp7U5lFI+29BuBx9AJdhii+DNgKR3iongQf206qlhpzotqE1jv6Cztu4g4l/CsAtH7a8QIDAQABAoIBAEuBYAMx/njuWRiF1a09j6GmrirB4zfvK6WPbiLe43roUVsSKuPZfI5P0Wm5coi0+n1w0JOonML8OLqcETknrybU3KdA4tdxtoLNVj1f7sHyPtLjrIpTaOnlE0ADAPpVymv+5mZwTfNnD5Z7+OIUF1RjJ2u8U7teZrUg0ji5u5b8vlmitHVIgun7wCiIfli4zMXuYT1hp4i4ABtxdetfbETthi5Gcj0KHbymhpWfAEiU21bjA8XSpnEddsGALRQpwK1xS0gm538a+uM0hlIzSW5pcohLw+MxfzRLNwgtoRAweyNdXorv4CsV/rJHqeKZmSopu/0/mu1vtHylBeHXr80CgYEA6PO0DG2XpOVWZo3JXH+Fc+HSszh9/WRafY8GWE5r5zVKKYnfwRgOg7cir6iH9VTZrpAOK+JmTsLZO+VJ6IiugasBGu8V/1kMbLpaRlCWYnpyQAU6RQ2Lhn+1VsDzeeAYyyfP3GgPH9CnjUgkydC7ZVQncyLyxOaoFcstADZAdksCgYEAzp5DW4PfAtzhsYLZkgPz3j9wqcvR6bz+yRMtmQZHgVwsH+hP+T92Idj9VvhinyMEqpjNNXuGEaSXtxYpfGS50jkqb1slnxywXwT/TZVeQ0KVIMkVLrPIAOdp5HhDNlNY9Mr5CPsdj1jdUHv+PaV2CNFazT37I7tt03QpHaLPnjMCgYAJ7Jf3D5QuSjbsF45Eioo87Zn0WKvFZ8kTIEy85lpidzq5mk4WA9hadCreIOfp47uCXFC+Pd7t7A8lJheH+Iq2q3pYk2b0ge6tkyLVbAl8GItVfuOEnZccG8S19XJp9soXnZKVaTl7uX/p3PD0SBgzsOodVZfSG6F9jDJWl/kXEQKBgBu4vj7UFaLTsfBYJwrhPuINzvbpItPiiKi/yvliD0v66uypBbniWt41t9/oWYsSbrjY4YeQeC97zuNAtPY8qXXcN6ZTK1wKxFsrV3m4Vbpef5WzhQUMGASPB/UgcZwjWKcXaIxc7N1jxeXbjQQGZCzQsgchjsV/iz+4sR+JzaNjAoGBAJKfZidX3NcNpl8TQz7d1Z3M8BwSae25RYPW0ZaquJ5J3sEjgjxFIaX7HeveVdl+dT94q9Bd1K6dtHOPyQvuU0wJJ054zWWNOfAiyDylc2lsFE9grUsfxocaWGt5ADmU10De4crSu2JvmtOWaFBV5EjC56UnS2Bb3jE8rvUwfKTP'
    alipay_client_config.alipay_public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvAQeli6bj2kPQBlZmqic8bbfPo29J9XIE/NQM1QhcFU/lAcZpleGm38Y+9XnpUN3k2cxIn49GZTTwsSJ0kX6SSBWLkGZOs3RpaLsrgOtkuT1DIXzvoTDe5Q88Hf/5XQJ3GStJnn1ZRnBqokzRUExbTUnuSW+nQftl6Bv/Xh4Ov5L6GPDfesbTG8SQsZYibXREmvoB7cpcQuz8Ci7MJanDASU3aUHTh2jOe27F3F4cPRDE8XNjoDPcW4CqViXwNZvBXH6phNEzFmDpPcPWSp7U5lFI+29BuBx9AJdhii+DNgKR3iongQf206qlhpzotqE1jv6Cztu4g4l/CsAtH7a8QIDAQAB'
    """
    得到客户端对象。
    注意，一个alipay_client_config对象对应一个DefaultAlipayClient，定义DefaultAlipayClient对象后，alipay_client_config不得修改，如果想使用不同的配置，请定义不同的DefaultAlipayClient。
    logger参数用于打印日志，不传则不打印，建议传递。
    """
    client = DefaultAlipayClient(alipay_client_config=alipay_client_config)

    """
    页面接口示例：alipay.trade.page.pay
    """
    # 对照接口文档，构造请求对象
    model = AlipayTradePagePayModel()
    model.out_trade_no = orderObj.order_code
    model.total_amount = total_money
    #标题
    model.subject = "智能硬件购物商城"
    #订单描述
    model.body = goods_name_all
    model.product_code = "FAST_INSTANT_TRADE_PAY"
    request = AlipayTradePagePayRequest(biz_model=model)
    request.return_url = 'http://127.0.0.1:8000/user/return_url/'
    # 得到构造的请求，如果http_method是GET，则是一个带完成请求参数的url，如果http_method是POST，则是一段HTML表单片段
    response = client.page_execute(request, http_method="GET")
    print("alipay.trade.page.pay response:" + response)
    return HttpResponseRedirect(response)



# 添加收货地址
def add_address(request):
    return render(request, 'user/add_address.html')


def do_add_address(request):
    name = request.POST.get('name', '')
    address = request.POST.get('address', '')
    phone = request.POST.get('phone', '')

    if name == '' or address == '' or phone == '':
        return HttpResponse('收货人、地址、电话不可为空')

    user_id = request.session.get('U_userid', 0)
    if user_id == 0:
        return HttpResponseRedirect('/user/login')

    addressObj = user_address()
    addressObj.users_id = user_id
    addressObj.address = address
    addressObj.name = name
    addressObj.phone = phone
    addressObj.save()

    return HttpResponseRedirect(reverse('user:place_order'))

def verify_login(func):
    def inner_fun(request):
        user_id = request.session.get('U_userid', 0)
        if user_id == 0:
            return HttpResponseRedirect(reverse('user:login'))
        else:
            return func(request)
    return inner_fun

# 用户中心的订单管理
@verify_login
def user_order_list(request):
    # 查询用户的所有订单
    user_id = request.session.get('U_userid', 0)
    # if user_id == 0:
    #     return HttpResponseRedirect('user:login')
    order_list = orders.objects.filter(users_id=user_id)
    return render(request,'user/user_order_list.html',{'order_list':order_list})
    # return render(request, 'user/user_order_list.html', {'order_list': order_list})


# 修改收货状态
def edit_receive_status(request):
    order_id = request.POST.get('order_id', 0)
    data = {}
    if order_id == 0:
        data['msg'] = '请选择订单'
        data['status'] = 0
        return HttpResponse(json.dumps(data))

    user_id = request.session.get('U_userid', 0)
    if user_id == 0:
        data['msg'] = '请登录'
        data['status'] = 0
        return HttpResponse(json.dumps(data))

    bool = orders.objects.filter(id=order_id, users_id=user_id).update(receive_status=1, receive_time=datetime.datetime.now())
    if bool:
        data['msg'] = '收货成功'
        data['status'] = 1
        return HttpResponse(json.dumps(data))
    else:
        data['msg'] = '出了点小意外，请您稍后再试'
        data['status'] = 0
        return HttpResponse(json.dumps(data))


def user_order_info(request):
    order_id = request.GET.get('order_id', 0)
    if order_id == 0:
        return HttpResponse('请选择要查看的订单')

    user_id = request.session.get('U_userid', 0)
    if user_id == 0:
        return HttpResponse('请登录')

    info = orders.objects.filter(id=order_id, users_id=user_id).first()
    print(info)

    if info == None:
        return HttpResponse('未找到订单信息')

    return render(request, 'user/user_order_info.html', {'info': info})


# 渲染评价页面
def comment_view(request):
    order_id = request.GET.get('order_id', 0)

    order_info_list = order_info.objects.filter(order_id=order_id)
    return render(request, 'user/comment.html', {'order_info_list': order_info_list})


# 保存评价
def docomment(request):
    print(request.POST)
    goods_id_list = request.POST.getlist('goods_id')
    order_id = request.POST.get('order_id', 0)

    user_id = request.session.get('U_userid', 0)
    if user_id == 0:
        return HttpResponse('请登录')

    for goods_id in goods_id_list:
        score = request.POST.get('score' + goods_id)
        content = request.POST.get('comment_content' + goods_id)
        commentObj = comment()
        commentObj.goods_id = goods_id

        good_info = GoodsInfro.objects.filter(id=goods_id).first()
        commentObj.manager_id = good_info.manager_id

        commentObj.users_id = user_id
        commentObj.score = score
        commentObj.content = content
        commentObj.save()

    # 修改订单评价状态
    bool = orders.objects.filter(id=order_id).update(comment_status=1)
    if bool:
        return HttpResponseRedirect(reverse('user:user_order_list'))
    else:
        return HttpResponse('评价状态修改失败')


# 显示--修改密码页面
def edit_password(request):
    user_id = request.session.get('U_userid', 0)
    if user_id == 0:
        return HttpResponseRedirect('/user/login')
    return render(request, 'user/updatepass.html')


# 检查密码是否正确
def check_pwd(request):
    password = request.POST.get('password', 0)
    data = {}
    if password == '':
        data['msg'] = '请输入原始密码'
        data['status'] = 0
        return HttpResponse(json.dumps(data))

    user_id = request.session.get('U_userid', 0)
    if user_id == 0:
        data['msg'] = '登录状态失效，请重新登录'
        data['status'] = 0
        return HttpResponse(json.dumps(data))
    userinfo = users.objects.filter(id=user_id).first()
    if userinfo == None:
        data['msg'] = '用户不存在'
        data['status'] = 0
        return HttpResponse(json.dumps(data))

    md = hashlib.md5()
    md.update(password.encode('utf-8'))
    md5_password = md.hexdigest()
    if userinfo.password == md5_password:
        data['msg'] = '密码正确'
        data['status'] = 1
        return HttpResponse(json.dumps(data))
    else:
        data['msg'] = '原始密码错误'
        data['status'] = 0
        return HttpResponse(json.dumps(data))


#
def do_edit_password(request):
    user_id = request.session.get('U_userid', 0)
    if user_id==0:
        return HttpResponseRedirect('/user/login')

    new_pass=request.POST.get('usernewpass')
    md = hashlib.md5()
    md.update(new_pass.encode('utf-8'))
    md5_password = md.hexdigest()

    bool=users.objects.filter(id=user_id).update(password=md5_password)
    if bool:
        return HttpResponseRedirect('/user/login')
    else:
        return HttpResponse('密码修改失败')


# 生成验证码
def verify_code(request):
    # 创建画板
    img_color = (random.randint(0, 255), random.randint(0, 150), random.randint(0, 255))
    img = Image.new('RGB', (100, 30), img_color)
    # 创建画笔
    draw = ImageDraw.Draw(img)

    str = 'AaBx1CibD3wEFv2G4jhHc5I6JkKyu7L8dtMNsO9ePmQlRS0ToUnfVrWzXgYpqZ'

    font = ImageFont.truetype('simhei.ttf', 25)
    x, y = 0, 0
    font_str = ''
    # 生成验证码
    for i in range(0, 5):
        # 字体颜色
        one_str = str[random.randint(0, len(str) - 1)]
        font_str += one_str
        color = (random.randint(0, 255), random.randint(150, 255), random.randint(0, 255),)
        draw.text((x, y), one_str, fill=color, font=font)
        x += 20
    for z in range(0, 100):
        point_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.point((random.randint(0, 100), random.randint(0, 25)), fill=point_color)

    draw.line(((20, 15), (90, 18)), fill=(0, 0, 0))



    io = BytesIO()
    img.save(io, 'png')
    request.session['verify_code'] = font_str.lower()
    return HttpResponse(io.getvalue(), 'image/png')


# 检查验证码是否正确
def check_code(request):
    verify_code = request.POST.get('verify_code', '').lower()
    local_code = request.session['verify_code']
    data = {}
    if len(verify_code) != 5:
        data['status'] = 0
        data['msg'] = '验证码输入错误'
        return HttpResponse(json.dumps(data))
    if verify_code != local_code:
        data['status'] = 0
        data['msg'] = '验证码输入错误'
        return HttpResponse(json.dumps(data))
    else:
        data['status'] = 1
        data['msg'] = '验证码输入正确'
        return HttpResponse(json.dumps(data))

#发送消息
def send_message(request):
    uid=request.session.get('temp_id',0)
    user_info=users.objects.filter(id=uid).first()
    host='http://127.0.0.1:8000'
    address=reverse('user:activate_email')
    parameter={}
    parameter['Uid']=uid
    parameter['t']=int(time.time())

    url_list=[]
    for key,val in parameter.items():
        url_list.append(str(key)+'='+str(val))

    url_param='&'.join(url_list)

    url=host+address+'?'+url_param

    md = hashlib.md5()
    md.update(url_param.encode('utf-8'))
    token = md.hexdigest()
    url+='&token='+token

    send_mail('账户激活','邮件内容','智能硬件购物商城<18703249138@163.com>',
              [user_info.email],html_message="<a href=%s>点击这里进行验证</a>"%(url))

    return HttpResponse('发送成功')


#激活账户
def activate_email(request):
    id = request.GET.get('Uid','0')
    t=request.GET.get('t')
    token=request.GET.get('token')
    now_time=time.time()
    url_param= 'Uid='+id+'&t='+t
    md = hashlib.md5()
    md.update(url_param.encode('utf-8'))
    new_token = md.hexdigest()
    if token!=new_token:
        return HttpResponse('链接无效')
    if now_time-int(t)>(60*30):
        return HttpResponse('链接已失效')

    bool=users.objects.filter(id=id).update(activate=1)
    if bool:
        return message("激活成功,请返回<a href='%s'>登录</a>" % (reverse('user:login')))
    else:
        return HttpResponse('激活失败')

def message(msg):
    return render_to_response('user/message.html',{'msg':msg})

# 支付宝回调页面
def return_url(request):
    order_code = request.GET.get('out_trade_no')
    bool = orders.objects.filter(order_code=order_code).update(pay_status=1, pay_time=datetime.datetime.now())
    return message("支付成功！<a href='%s'>继续购物</a>" % (reverse('goods:index')))