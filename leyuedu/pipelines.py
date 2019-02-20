# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import logging


class MysqlPipeline(object):

    table_name = 'lread'
    logger = logging.getLogger(__name__)

    def __init__(self, host, user, password, port,database, charset, ):
        self._host = host
        self._user = user
        self._password = password
        self._port = port
        self._database = database
        self._charset = charset
        self._conn = pymysql.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            port=self._port,
            db=self._database,
            charset=self._charset
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host = crawler.settings.get('HOST'),
            user = crawler.settings.get('USER'),
            password = crawler.settings.get('PASSWORD'),
            port = crawler.settings.get('PORT'),
            database = crawler.settings.get('DATABASE',),
            charset = crawler.settings.get('CHARSET')
        )

    def process_item(self, item, spider):
        data = dict(item)
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))
        sql = "insert into {table}({keys})values({values}) on duplicate key update".format(table=self.table_name, keys=keys,
                                                                                           values=values)
        update = ','.join([' {key}=%s'.format(key=key) for key in data])
        sql += update
        try:
            with self._conn.cursor() as cursor:
                if cursor.execute(sql, tuple(data.values()) * 2):
                    self._conn.commit()
                    self.logger.info('保存成功')
        except Exception as e:
            self._conn.rollback()
            self.logger.info('保存失败，失败信息：', e.args)
        return item