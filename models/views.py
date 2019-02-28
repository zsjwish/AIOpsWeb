import csv
import json
import os

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from isolate_model.base_function import save_datas_with_labels, use_XGBoost_predict, train_model, get_datas_for_tag, \
    update_datas_for_tag
from models.hello import Hello
from models.models import xgboost_model_dict, lstm_model_dict, data_set


def index(request):
    return render(request, 'models/index.html')


def menu(request):
    return render(request, 'models/menu.html')


def hello(request):
    h1 = Hello()
    string = h1.get_str("world!")
    context = {"string": string, "xgboost": xgboost_model_dict.keys(), "lstm": lstm_model_dict.keys()}
    return render(request, 'models/hello.html', context = context)


def success(request):
    return render(request, 'models/upload_success.html')


def submit(request):
    # 判断接收的值是否为POST
    print(request.body.decode())
    print(type(request.body.decode()))
    if request.method == "POST":
        body = json.loads(request.body.decode())
        # print(type(body))
        # print("host_id", body["host_id"])
        # print("time", body["time"])
        # print("kpi", body["CPU"])
        result = use_XGBoost_predict(body)
        print(result)
        return HttpResponse(result, content_type = "application/json")
    return render(request, 'models/upload_one_data.html')


def train(request):
    """
    用于训练数据
    :param request:
    :return:
    """
    # 判断接收的值是否为POST
    dataset = {"names": data_set}
    if request.method == "POST":
        kind = request.POST["kind"]
        data_name = request.POST["data_name"]
        info = {"kind": kind, "data_name": data_name}
        res = train_model(kind, data_name)
        if res == 0:
            return render(request, 'models/model_exists.html')
        return render(request, 'models/train_success.html', context = info)
    return render(request, 'models/train.html', context = dataset)


def tag(request):
    """
    对数据标注
    :param request:
    :return:
    """
    # 判断接收的值是否为POST
    info = {"data_names": data_set}
    if request.method == "POST":
        info["table_name"] = request.POST["data_name"]
        info["start_time"] = request.POST["start_time"]
        info["end_time"] = request.POST["end_time"]
        info["label"] = int(request.POST["label"])
        info["name"] = request.POST["data_name"]
        print(info)
        info["datas"] = get_datas_for_tag(table_name = info["table_name"],start_time = info["start_time"], end_time = info["end_time"], label = info["label"])
        print(info)
        return render(request, 'models/tag.html', context = info)
    return render(request, 'models/tag.html', context = info)



@csrf_exempt
def upload(request):
    """
    上传csv文件，注意文件要以host_id uuid形式命名，文件放到file文件夹下, 并且解析存储到数据库中
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
        # 获取上传的文件名
        f_name = f.name
        print(f_name)
        # 通过chunks分片上传存储在服务器内存中,以64k为一组，循环写入到服务器中
        for line in file_obj.chunks():
            f.write(line)
        f.close()
        if save_datas_with_labels(f_name):
            return render(request, 'models/upload_success.html', {'file_name': f_name.split("/")[-1]})
        return render(request, 'models/upload_failed.html')
    return render(request, 'models/upload_csv.html')  # 将处理好的结果通过render方式传给upload.html进行渲染
