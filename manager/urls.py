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
    #卖家后台登录页面显示
    url(r'^login/', views.login,name='login'),

    #卖家后台登录提交操作
    url(r'^dologin/',views.dologin,name='dologin'),

    #显示商品后台管理页面
    url(r'main/',views.main),

    #退出
    url(r'^loginout/',views.loginout,name='loginout'),

    #订单列表
    url(r'^order_list/',views.order_list,name='order_list'),

    #订单详情
    url(r'^order_info/',views.order_info,name='order_info'),

    # 修改发货状态 edit_send_status
    url(r'^edit_send_status/', views.edit_send_status, name='edit_send_status'),

    # 审核评价页面
    url(r'^comment_list/', views.comment_list, name='comment_list'),

    # 审核评价操作
    url(r'^comment_list_yes/', views.comment_list_yes, name='comment_list_yes'),
    #
    # 审核评价操作
    url(r'^check_comment/', views.check_comment, name='check_comment'),

    # 修改库存页面
    url(r'^edit_count/(?P<g_id>\d+)/', views.edit_count, name='edit_count'),

    #
    url(r'^do_edit_count/(?P<g_id>\d+)/', views.do_edit_count, name='do_edit_count'),
    # 用户列表
    url(r'^member_list/', views.member_list, name='member_list'),

    # 显示编辑用户页面 member_edit
    url(r'^member_edit/', views.member_edit, name='member_edit'),

    # 修改用户信息 操作do_member_edit
    url(r'^do_member_edit/', views.do_member_edit, name='do_member_edit'),

    #增加用户
    url(r'^member_add/', views.member_add, name='member_add'),

    #执行增加用户
    url(r'^do_member_add/', views.do_member_add, name='do_member_add'),

    # 删除用户
    url(r'^member_del/', views.member_del, name='member_del'),

]
