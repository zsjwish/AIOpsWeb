#!/usr/bin/env python
import os
import sys

from isolate_model.base_function import load_datas_from_disk_to_memory, load_lstm_class, load_xgboost_class
from models.models import data_set, xgboost_model_dict, lstm_model_dict

if __name__ == '__main__':
    # 从磁盘中加载数据集名列表
    load_datas_from_disk_to_memory()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AIOps_pro.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
