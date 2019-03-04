from django.db import models

# Create your models here.

# 用于存储已经训练好的XGBoost和LSTM模型名称，还有数据集名称


data_set = []
xgboost_name = []
lstm_name = []
xgboost_model_dict = {}
lstm_model_dict = {}
from db.train_model_thread import TrainModelThreadPool
executor = TrainModelThreadPool()
print(executor)
