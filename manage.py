#!/usr/bin/env python
import os
import sys

from AIOps_pro.static_value import StaticValue
from isolate_model.base_function import load_datas_from_disk_to_memory

if __name__ == '__main__':
    print("manage 33333333333333333333")
    # 从磁盘中加载数据集名列表
    os.environ.update({"DJANGO_SETTINGS_MODULE": "AIOps_pro.settings"})
    load_datas_from_disk_to_memory()

    # 加载设置项
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

