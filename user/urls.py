"""QSHOP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    #显示登录页面
    url(r'^login/',views.login,name='login'),

    #显示注册页面
    url(r'^reg/',views.reg,name='reg'),

    #检查用户名
    url(r'^check_user/',views.check_user,name='check_user'),

    #注册
    url(r'^doreg/',views.doreg,name='doreg'),
    #登录
    url(r'^dologin/',views.dologin,name='dologin'),
    #登出
    url(r'^logout/',views.logout,name='logout'),
    # 添加购物车
    url(r'^add_car/', views.add_car, name='add_car'),

    # 购物车列表
    url(r'^car_list/', views.car_list, name='car_list'),

    # 修改购物车商品数量
    url(r'^edit_num/', views.edit_num, name='edit_num'),

    #删除购物车商品
    url(r'^del_car/', views.del_car, name='del_car'),

    #清空购物车
    url(r'^clear_car/', views.clear_car, name='clear_car'),

    # 下单
    url(r'^place_order/', views.place_order, name='place_order'),

    # 确认下单 do_place_order
    url(r'^do_place_order/', views.do_place_order, name='do_place_order'),

    # 添加收货地址 add_address
    url(r'^add_address/', views.add_address, name='add_address'),

    # 添加地址 操作 do_add_address
    url(r'^do_add_address/', views.do_add_address, name='do_add_address'),

    # 用户中心---订单管理
    url(r'^user_order_list/', views.user_order_list, name='user_order_list'),

    #用户中心---修改收货状态
    url(r'^edit_receive_status/', views.edit_receive_status, name='edit_receive_status'),

    url(r'^user_order_info/', views.user_order_info, name='user_order_info'),

    #用户中心-评价页面
    url(r'^comment_view/', views.comment_view, name='comment'),
    #用户中心-保存评价数据
    url(r'^do_comment/', views.docomment, name='do_comment'),
    #修改密码
    url(r'^edit_password/', views.edit_password, name='edit_password'),
    #检查用户密码是否正确
    url(r'^check_pwd/', views.check_pwd, name='check_pwd'),

    url(r'^do_edit_password/', views.do_edit_password, name='do_edit_password'),
    #生成验证码
    url(r'^verify_code/', views.verify_code, name='verify_code'),
    #检查验证码是否正确
    url(r'^check_code/', views.check_code, name='check_code'),
    #发送邮件
    url(r'^send_message/', views.send_message, name='send_message'),
    #注册跳转页
    url(r'^send_msg_view/', views.send_msg_view, name='send_msg_view'),
    #激活邮件
    url(r'^activate_email/', views.activate_email, name='activate_email'),
    #回调地址
    url(r'^return_url/',views.return_url)

]
