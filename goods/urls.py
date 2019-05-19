from django.conf.urls import url
from . import views

urlpatterns = [
    #显示添加商品页面
    url(r'^goods_add/',views.goods_add,name='goods_add'),

    #显示添加商品页面提交操作
    url('^dogoods_add/',views.dogoods_add,name='dogoods_add'),

    #显示商品列表
    url(r'^goods_list/',views.goods_list,name='goods_list'),

    #删除商品信息
    url(r'^goods_delete/(?P<g_id>\d+)',views.goods_delete,name='goods_delete'),

    #修改商品信息 ---显示
    url(r'^goods_modify/(?P<g_id>\d+)',views.goods_modify,name='goods_modify'),

    #修改商品信息 ---提交
    url(r'^dogoods_modify/',views.dogoods_modify,name='dogoods_modify'),

    #商城首页
    url(r'^index/',views.index,name='index'),

    # 商城列表页
    url(r'^goods_types/', views.goods_type, name='type'),

    # 商城 商品详情页
    url(r'^details/', views.goods_details, name='details'),

    # 比价
    url(r'^bijia/', views.bijia, name='bijia')

]