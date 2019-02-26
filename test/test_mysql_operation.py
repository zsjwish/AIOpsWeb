import unittest

from db.mysql_operation import connectdb, query_table, create_table, drop_table, query_datas, insert_train_datas, closedb, \
    delete_datas, update_datas
from isolate_model.base_function import load_csv
from isolate_model.isolate_class import Isolate


class MysqlTestCases(unittest.TestCase):

    def setUp(self):
        # 加载测试文件
        cases = load_csv("../file/mysql_test_case.csv")
        # 使用孤立森立判断label
        isolate1 = Isolate('mysql_test_case', cases)
        # 孤立森林判断后的结果
        self.np_array = isolate1.merge_arrays()
        # 连接数据库
        self.db = connectdb()
        # 设置表名
        self.table_name = self.np_array[1, 0]

    def test_create_table(self):
        """
        测试创建表
        :return:
        """
        # 创建表之前确定表不存在
        self.assertEqual(False, query_table(self.db, self.table_name))
        # 创建表操作
        create_table(self.db, self.np_array[0], self.np_array[1, 0])
        # 创建表之后确定表已经存在
        self.assertEqual(True, query_table(self.db, self.table_name))

    def test_insert_datas(self):
        """
        测试插入数据
        :return:
        """
        # 创建表操作
        create_table(self.db, self.np_array[0], self.np_array[1, 0])
        # 测试查询数据
        query_result = query_datas(self.db, self.table_name)
        # 没插入数据之前为0条
        self.assertEqual(0, len(query_result))
        # 插入数据
        insert_train_datas(self.db, self.table_name, self.np_array[1:])
        # 测试查询数据
        query_result = query_datas(self.db, self.table_name)
        self.assertEqual(3, len(query_result))

    def test_delete_datas(self):
        """
        测试删除数据
        :return:
        """
        # 创建表操作
        create_table(self.db, self.np_array[0], self.np_array[1, 0])
        # 插入数据
        insert_train_datas(self.db, self.table_name, self.np_array[1:])
        # 删除数据
        delete_datas(self.db, self.table_name, end_time = '2019/01/07 10:15')
        # 查询删除数据后的数据
        query_result = query_datas(self.db, self.table_name)
        self.assertEqual(2, len(query_result))
        # 删除数据
        delete_datas(self.db, self.table_name, start_time = '2019/01/07 10:17')
        # 查询删除数据后的数据
        query_result = query_datas(self.db, self.table_name)
        self.assertEqual(1, len(query_result))

    def test_drop_table(self):
        """
        测试删除表
        :return:
        """
        # 创建表操作
        create_table(self.db, self.np_array[0], self.np_array[1, 0])
        # 创建表后能查到表的存在
        self.assertEqual(True, query_table(self.db, self.table_name))
        # 删除表
        drop_table(self.db, self.table_name)
        # 删除表后查不到表
        self.assertEqual(False, query_table(self.db, self.table_name))

    def test_update_datas(self):
        """
        测试更新数据
        :return:
        """
        # 创建表操作
        create_table(self.db, self.np_array[0], self.np_array[1, 0])
        # 插入数据
        insert_train_datas(self.db, self.table_name, self.np_array[1:])
        # 获取数据
        query_result = query_datas(self.db, self.table_name)
        print(query_result)
        # 更新数据，将'2019/01/07 10:17'之后的数据label全置为1
        update_datas(self.db, self.table_name, start_time = '2019/01/07 10:17', label = 1)
        query_with_label = query_datas(self.db, self.table_name, start_time = '2019/01/07 10:17', label = 1)
        query_without_label = query_datas(self.db, self.table_name, start_time = '2019/01/07 10:17')
        self.assertEqual(len(query_with_label), len(query_without_label))
        # 更新数据，将'2019/01/07 10:17'之后的数据label全置为0
        update_datas(self.db, self.table_name, start_time = '2019/01/07 10:17', label = 0)
        query_with_label = query_datas(self.db, self.table_name, start_time = '2019/01/07 10:17', label = 0)
        query_without_label = query_datas(self.db, self.table_name, start_time = '2019/01/07 10:17')
        self.assertEqual(len(query_with_label), len(query_without_label))

    def tearDown(self):
        # 删除表
        drop_table(self.db, self.table_name)
        # 关闭数据库连接
        closedb(self.db)


if __name__ == '__main__':
    unittest.main()
