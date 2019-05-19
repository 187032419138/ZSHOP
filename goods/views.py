from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from .models import GoodsInfro,GoodsType,Bijia
from manager.models import ManagerMessage
from user.models import comment
import uuid
from django.conf import settings
from ZSHOP.check_power import check_power
import requests
from lxml import etree

#显示添加商品页面
@check_power
def goods_add(request):
    goods_type_list = GoodsType.objects.all()
    return render(request,'goods/goods_add.html',{'goods_type_list':goods_type_list})

##显示添加商品页面提交操作
def dogoods_add(request):
    #获取表单信息
    # 商品编号
    goods_num = request.POST['goods_num']
    # 商品名称
    goods_name = request.POST['goods_name']
    # 商品原价
    goods_oprice = request.POST['goods_oprice']
    # 商品现价
    goods_xprice = request.POST['goods_xprice']
    # 库存
    goods_count = request.POST['goods_count']
    # 商品缩略图
    goods_pic = request.FILES.get('goods_pic')

    hix = ['image/png', 'image/jpg', 'image/gif','image/jpeg']
    if goods_pic.content_type not in hix:
        return HttpResponse('请上传正确格式的图片，只支持jpg,png,gif')

    # 给文件重命名
    file_suffix = goods_pic.name.split('.')[-1]
    new_file_name = str(uuid.uuid1()) + '.' + file_suffix

    # 上传图片 将图片移动到指定目录
    file_path = settings.MEDIA_ROOT + '/media/uploads/' + new_file_name
    save_path = 'media/uploads/' + new_file_name
    with open(file_path, 'wb+') as f:
        for file in goods_pic.chunks():
            f.write(file)

    # 配送地址
    goods_address = request.POST['goods_address']
    # 商品内容
    goods_content = request.POST['goods_content']
    #商品类别
    type_id = request.POST['type_id']
    user_id = request.session.get('user_id',0)

    #登录验证
    if user_id == 0:
        return HttpResponse('请先登录')

    #完成数据插入
    result = GoodsInfro.objects.create(goods_num=goods_num,
                              goods_name=goods_name,
                              goods_oprice=goods_oprice,
                              goods_xprice=goods_xprice,
                              goods_count=goods_count,
                              goods_pic=save_path,
                              goods_address=goods_address,
                              goods_content=goods_content,
                              manager_id=user_id,
                              type_id=type_id)
    if result:
        return HttpResponseRedirect('/goods/goods_list')
    else:
        return HttpResponse('失败')

#商品列表的显示
@check_power
def goods_list(request):
    #查找所有商品信息数据
    # list = GoodsInfro.objects.all()
    user_id = request.session.get('user_id',0)
    list = GoodsInfro.objects.filter(manager_id=user_id)
    return render(request,'goods/goods_list.html',{'list':list})

#删除商品信息
def goods_delete(request,g_id):
    try:
        user_id = request.session.get('user_id',0)

        goods = GoodsInfro.objects.get(id=g_id)
        if goods.manager_id != user_id:
            return HttpResponse('身份出错！')
        else:
            goods.delete()
            return HttpResponseRedirect('/goods/goods_list')
    except:
        return HttpResponse('删除失败，请联系管理员！')

#修改商品信息 ---显示修改页面
def goods_modify(request,g_id):
    user_id = request.session.get('user_id',0)
    goods = GoodsInfro.objects.get(id=g_id)
    if goods.manager_id != user_id:
        return HttpResponse('你在犯罪知道吗')

    goods_type_list = GoodsType.objects.all()
    return render(request,'goods/goods_modify.html',{'goods':goods,'goods_type_list':goods_type_list})

#修改商品信息 ---提交
def dogoods_modify(request):
    # 获取表单信息
    # 商品编号
    goods_num = request.POST['goods_num']
    # 商品名称
    goods_name = request.POST['goods_name']
    # 商品原价
    goods_oprice = request.POST['goods_oprice']
    # 商品现价
    goods_xprice = request.POST['goods_xprice']
    # 库存
    goods_count = request.POST['goods_count']
    # 商品缩略图
    goods_pic = request.FILES.get('goods_pic')

    #判断图片的类型（另外一种方式：判断后缀）
    hix = ['image/png','image/jpg','image/gif','image/jpeg']
    if goods_pic.content_type not in hix:
        return HttpResponse('请上传正确格式的图片，只支持jpg,png,gif')

    #给文件重命名
    file_suffix = goods_pic.name.split('.')[-1]
    new_file_name = str(uuid.uuid1()) + '.' + file_suffix

    # 上传图片 将图片移动到指定目录
    file_path = settings.MEDIA_ROOT + '/media/uploads/' + new_file_name
    save_path = 'media/uploads/' + new_file_name
    with open(file_path,'wb+') as f:
        for file in goods_pic.chunks():
            f.write(file)


    # 配送地址
    goods_address = request.POST['goods_address']
    # 商品内容
    goods_content = request.POST['goods_content']

    #商品id
    g_id = request.POST['id']

    #数据库操作
    goods = GoodsInfro.objects.filter(id=g_id)
    result = goods.update(goods_num=goods_num,
                  goods_name=goods_name,
                  goods_oprice=goods_oprice,
                  goods_xprice=goods_xprice,
                  goods_count=goods_count,
                  goods_pic=save_path,
                  goods_address=goods_address,
                  goods_content=goods_content)
    if result:
        return HttpResponseRedirect('/goods/goods_list')
    else:
        return HttpResponse('删除失败，请联系管理员')



#开店页面----提交
def doopenstore(request):
    #获取数据
    username = request.POST['username']
    shop_name = request.POST['shop_name']
    nicheng = request.POST['nicheng']
    shop_address = request.POST['shop_address']
    shop_logo = request.FILES['shop_logo']

    #默认初始密码000000

    #数据库操作
    result = ManagerMessage.objects.create(username=username,
                                  shop_name=shop_name,
                                  nicheng=nicheng,
                                  shop_address=shop_address,
                                  userpass = '000000',
                                  shop_logo = shop_logo
                                  )
    if result:
        return HttpResponseRedirect('/goods/welcome')
    else:
        return HttpResponse('注册失败，请稍后重试')


#前台首页
def index(request):
    data = GoodsInfro.objects.filter()#查询所有商品
    return render(request,'goods/index.html',{'list':data})

#前台列表页
def goods_type(request):
    tid = request.GET.get('tid',0)

    if tid == 0:
        data = GoodsInfro.objects.filter()
    else:
        data = GoodsInfro.objects.filter(type_id=tid)

    type_list = GoodsType.objects.filter()

    return render(request,'goods/goods_type.html',{'list':data,'type_list':type_list})

#显示商品详情 评论
def goods_details(request):
    id = request.GET.get('gid',0)
    if id == 0:
        return HttpResponse('你要看啥？')
    goods = GoodsInfro.objects.filter(id=id).first()
    #获取评论
    comments=comment.objects.filter(goods_id=id,status=1)
    #获取其他商品
    other_goods = GoodsInfro.objects.filter(type_id=goods.type_id)
    return render(request,'goods/goods_details.html',{'goods':goods,'other_goods_list':other_goods,'comments':comments})
#比价
def bijia(request):
    key=request.GET.get('key')
    id = request.GET.get('gid', 0)
    Bijia.objects.all().delete()
    kw = key
    base_url = 'http://www.b1bj.com/s.aspx?key=' + kw
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'
    }
    response = requests.get(url=base_url, headers=header)
    sel = etree.HTML(response.text)
    try:
        for i in range(1, 8, 2):
            price = sel.xpath('//*[@id="listpro"]/div[' + str(i) + ']/div[3]/div/font/text()')[0]
            title = sel.xpath('//*[@id="listpro"]/div[' + str(i) + ']/div[2]/div[1]/a/text()')[0]
            img = sel.xpath('//*[@id="listpro"]/div[' + str(i) + ']/div[1]/div/a/img/@src')[0]
            link = sel.xpath('//*[@id="listpro"]/div[' + str(i) + ']/div[2]/div[1]/a/@href')[0]
            saler = sel.xpath('//*[@id="listpro"]/div[' + str(i) + ']/div[2]/div[2]/text()')[0]
            comments = sel.xpath('//*[@id="listpro"]/div[' + str(i) + ']/div[5]/a/b/text()')[0]
            result = Bijia.objects.create(price=price,
                                          title=title,
                                          img=img,
                                          link=link,
                                          saler=saler,
                                          comment=comments,
                                          goods_id=id)
            print( title, img, link, saler,comments)
    except:
        return HttpResponse('服务器繁忙，请稍后重试')
    print(key,id)
    other_goods_list=Bijia.objects.filter(goods_id=id)
    this_goods = GoodsInfro.objects.filter(id=id).first()
    comment_num=comment.objects.filter(goods_id=id).count()

    return render(request,'goods/bijia.html',{'other_goods_list':other_goods_list,'this_goods':this_goods,'comment_num':comment_num})

