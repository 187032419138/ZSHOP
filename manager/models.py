from django.db import models

# Create your models here.
class ManagerMessage(models.Model):
    #用户登录用户名
    username = models.CharField(max_length=30)
    #用户登录密码
    userpass = models.CharField(max_length=32)
    #角色id
    role = models.ForeignKey('roles', default=1)

# 权限表
class power(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    add_time = models.DateTimeField(auto_now=True)
    add_user = models.CharField(max_length=50)


# 角色表
class roles(models.Model):
    name = models.CharField(max_length=30)
    add_time = models.DateTimeField(auto_now=True)
    add_user = models.CharField(max_length=50)
    disabled = models.BooleanField(default=False)


# 权限和角色关系表
class power_roles(models.Model):
    power = models.ForeignKey('power', default=1)
    role = models.ForeignKey('roles', default=1)
