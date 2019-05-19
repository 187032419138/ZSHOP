from django.db import models
#用户
class users(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=32)
    email=models.EmailField(max_length=50,default='')
    activate=models.BooleanField(default=0)


# 购物车
class car(models.Model):
    goods = models.ForeignKey('goods.GoodsInfro', default=1)  # 商品ID
    users = models.ForeignKey('users', default=1)
    number = models.IntegerField()


#订单表
    #单号，总价，下单人，下单时间，收货地址，支付状态，，支付时间发货状态，商家ID
class orders(models.Model):
    order_code = models.CharField(max_length=14, unique=True)
    money = models.DecimalField(max_digits=10, decimal_places=2)  # float(10,2)
    users = models.ForeignKey('users', default=1)
    add_time = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=150)
    contacts = models.CharField(max_length=30, default='')
    phone = models.CharField(max_length=20, default='')
    pay_status = models.BooleanField(default=False)
    pay_time = models.DateTimeField(null=True)
    send_status = models.BooleanField(default=False)
    send_time = models.DateTimeField(null=True)
    receive_status = models.BooleanField(default=False)
    receive_time = models.DateTimeField(null=True)
    comment_status=models.BooleanField(default=False)
    manage = models.ForeignKey('manager.ManagerMessage', default=1)


# 订单详情表
# 订单ID 、 商品ID 、价格、数量 、小计
class order_info(models.Model):
    order = models.ForeignKey('orders', default=1)
    goods = models.ForeignKey('goods.GoodsInfro', default=1)
    number = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # float(10,2)


# 收货地址
class user_address(models.Model):
    address = models.CharField(max_length=150)
    users = models.ForeignKey('users', default=1)
    name = models.CharField(max_length=30, default='')
    phone = models.CharField(max_length=20, default='')

#评论
class comment(models.Model):
    goods=models.ForeignKey('goods.GoodsInfro',default=1)
    manager=models.ForeignKey('manager.ManagerMessage',default=1)
    users=models.ForeignKey('users',default=1)
    score=models.IntegerField(default=0)
    content=models.CharField(max_length=100,default='')
    add_time=models.DateTimeField(auto_now_add=True)
    status=models.BooleanField(default=False)

