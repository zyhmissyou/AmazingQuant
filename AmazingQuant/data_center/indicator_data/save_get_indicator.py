# -*- coding: utf-8 -*-

# ------------------------------
# @Time    : 2019/12/18
# @Author  : gao
# @File    : save_get_indicator.py
# @Project : AmazingQuant 
# ------------------------------

import pandas as pd
from mongoengine.context_managers import switch_collection

from AmazingQuant.data_center.mongo_connection import MongoConnect
from AmazingQuant.utils.performance_test import Timer
from AmazingQuant.data_center.database_field.field_indicator import Indicator
from AmazingQuant.constant import DatabaseName
from AmazingQuant.data_center.get_data.get_calendar import GetCalendar
from AmazingQuant.constant import Period


class SaveGetIndicator(object):
    def __init__(self, indicator_name):
        self.indicator_name = indicator_name

    def save_indicator(self, input_data):
        """

        :param input_data: dataframe,index是datetime,column是证券代码
        :return:
        """
        database = DatabaseName.INDICATOR.value
        with MongoConnect(database):
            with switch_collection(Indicator, self.indicator_name) as indicator:
                # 每次存之前都情况上一次的数据
                indicator.drop_collection()
                doc_list = []
                start_time = min(input_data.index)
                end_time = max(input_data.index)

                for i in input_data.columns:
                    doc = indicator(start_time=start_time, end_time=end_time, security_code=i, data=list(input_data[i]))
                    doc_list.append(doc)
                indicator.objects.insert(doc_list)

    def get_indicator(self):
        calendar_obj = GetCalendar()
        calendar_SZ = calendar_obj.get_calendar('SZ')
        database = DatabaseName.INDICATOR.value
        with MongoConnect(database):
            with switch_collection(Indicator, self.indicator_name) as indicator:
                obj_list = indicator.objects()
                result = []
                for i in obj_list:
                    result.append(pd.DataFrame({i.security_code: i.data},
                                               index=[date for date in calendar_SZ if
                                                      i.start_time <= date <= i.end_time]))
                result = pd.concat(result, axis=1)
        return result, i.start_time, i.end_time


if __name__ == '__main__':
    with Timer(True):
        indicator_data, start_time, end_time = SaveGetIndicator('close').get_indicator()

