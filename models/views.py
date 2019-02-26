import csv
import json
import os


# Create your views here.
from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import csrf_exempt

from models.hello import Hello
from models.models import xgboost_list, lstm_list




def index(request):
    return render(request, 'models/index.html')


def menu(request):
    return render(request, 'models/menu.html')


def hello(request):
    h1 = Hello()
    string = h1.get_str("world!")
    context = {"string": string, "xgboost": xgboost_list, "lstm": lstm_list}
    return render(request, 'models/hello.html', context = context)


def success(request):
    return render(request, 'models/upload_success.html')



def submit(request):
    # 判断接收的值是否为POST
    print(request.body.decode())
    print(type(request.body.decode()))
    if request.method == "POST":
        body = json.loads(request.body.decode())
        print("time", body["time"])
        print("kpi", body["CPU"])
    return render(request, 'models/upload_one_data.html')


@csrf_exempt
def upload(request):
    """
    上传csv文件，注意文件要以host_id uuid形式命名，文件放到file文件夹下
    :param request:
    :return:
    """
    # 判断接收的值是否为POST
    if request.method == "POST":
        # 上传文件的接收方式应该是request.FILES
        inp_files = request.FILES
        # 通过get方法获取upload.html页面提交过来的文件
        file_obj = inp_files.get('f1')
        if file_obj is None:
            return render(request, 'models/upload_csv.html', context = {"error_message": "请选择文件后再上传！"})
        # 文件存储路径
        file_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/file/' + file_obj.name
        print(file_path)
        # 将客户端上传的文件保存在服务器上，一定要用wb二进制方式写入，否则文件会乱码
        f = open(file_path, 'wb+')
        # 通过chunks分片上传存储在服务器内存中,以64k为一组，循环写入到服务器中
        for line in file_obj.chunks():
            f.write(line)
        f.close()
        return render(request, 'models/upload_success.html')
    return render(request, 'models/upload_csv.html')  # 将处理好的结果通过render方式传给upload.html进行渲染


