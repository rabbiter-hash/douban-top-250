# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import csv
import json
import sqlite3
import pymysql

import openpyxl
import scrapy
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline

# 将数据保存到json
class doubanDataToJsonPipeline():
    def __init__(self):
        # 初始化就新建文档
        self.file = codecs.open('douban.json', 'w', encoding='utf-8-sig')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line)
        return item # 将item传递给下一个管道使用

    def close_spider(self, spider):
        self.file.close()

# 将数据保存到csv
class doubanDataToCsvPipeline():
    def __init__(self):
        # 管道开启就创建文档
        self.headers = (('排名', '标题', '评分', '评论人数', '电影主题', '链接', '片长', '上映日期', '电影简介', '电影海报'))
        self.filename = 'douban.csv'

    def open_spider(self, spider):
        # 蜘蛛一运行就需要打开文件
        self.file = open(self.filename, mode='a', encoding='utf-8-sig', newline='') # utf-8-sig专门解决中文乱码问题
        self.csvWriter = csv.writer(self.file)
        # 写入头部
        self.csvWriter.writerow(self.headers)

    def process_item(self, item, spider):
        # 从item处提取数据
        item = dict(item) # 其实item在这里的结构化数据还是挺明显的，为了保险还是用dict进行解析
        rank = item.get('rank', '')
        title = item.get('title') or ''
        rating = item.get('rating') or ''
        rating_count = item.get('rating_num', '')
        subject = item.get('subject') or ''
        movie_detail_page = item.get('movie_detail_page') or ''
        duration = item.get('duration') or ''
        release_date = item.get('release_date') or ''
        movie_intro = item.get('movie_intro') or ''
        movie_image_url = item.get('movie_image_url') or ''

        # 组织数据
        datas = []
        datas.append([
            rank, title, rating, rating_count, subject, movie_detail_page, duration, release_date,
            movie_intro, movie_image_url
        ])
        # 开始写入
        for data in datas:
            self.csvWriter.writerow(data)

        return item # 别忘记return

    def close_spider(self, spider):
        # 关闭蜘蛛的同时也关闭文件
        self.file.close()

class doubanDataToExcelPipeline():
    def __init__(self):
        self.wb = openpyxl.Workbook() # 创建工作簿
        self.ws = self.wb.active # 获取工作簿里的表
        self.headers = (('排名', '标题', '评分', '评论人数', '电影主题', '链接', '片长', '上映日期', '电影简介', '电影海报'))
        self.filename = 'douban.xlsx'

    def open_spider(self, spider):
        # 爬虫开始就填充表头
        self.ws.append(self.headers)

    def process_item(self, item, spider):
        # 从item处提取数据
        item = dict(item)  # 其实item在这里的结构化数据还是挺明显的，为了保险还是用dict进行解析
        rank = item.get('rank', '')
        title = item.get('title') or ''
        rating = item.get('rating') or ''
        rating_count = item.get('rating_count', '')
        subject = item.get('subject') or ''
        movie_detail_page = item.get('movie_detail_page') or ''
        duration = item.get('duration') or ''
        release_date = item.get('release_date') or ''
        movie_intro = item.get('movie_intro') or ''
        movie_image_url = item.get('movie_image_url') or ''

        # 组织数据
        self.ws.append([
            rank, title, rating, rating_count, subject, movie_detail_page, duration, release_date,
                        movie_intro, movie_image_url
                        ])

        self.wb.save(self.filename) # 每追加一条保存一次
        return item

    def close_spider(self, spider):
        self.wb.save(self.filename)
        self.wb.close()

class doubanDataToSqlitePipeline():
    def __init__(self):
        self.dbname = 'douban.sqlite'
        # self.dbname = 'douban.db' # 也可以是这样
        self.dbtable = 'db250'

    def open_spider(self, spider):
        # 当爬虫启动时，就开始连接并创建数据库
        self._create_database() # 如果存在就是连接，如果不存在就是创建

    def _create_database(self):
        # 开始连接
        self.conn = sqlite3.connect(self.dbname) # 如果不存在就是创建
        # 获取游标
        self.cur = self.conn.cursor()

        # 建表sql
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS {} 
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT not null,
                    rank int not null,
                    title varchar(255) not null,
                    rating decimal(3,1) not null,
                    rating_count char(100) not null,
                    subject char(100),
                    movie_detail_page varchar(255) not null,
                    duration decimal(3,1) not null,
                    release_date varchar(255) not null,
                    movie_intro varchar(20000) not null,
                    movie_image_url varchar(255) not null
                )
        """.format(self.dbtable)
        # 运行sql
        self.cur.execute(create_table_sql)
        # 提交更改
        self.conn.commit()

    def process_item(self, item, spider):
        # 先提取数据
        # item在scrapy中是一个item对象，类似字典，但又不是字典，所以将数据转换一下
        dict_item = dict(item)
        # 从字典取值
        rank = dict_item.get('rank', '')  # 取值，没有取到就为空
        title = dict_item.get('title') or ''  # 也可以这样取，如果没取到就为空
        rating = dict_item.get('rating', '')
        rating_count = dict_item.get('rating_count', '')
        subject = dict_item.get('subject', '')
        movie_detail_page = dict_item.get('movie_detail_page', '')
        duration = dict_item.get('duration', '')
        release_date = dict_item.get('release_date', '')
        movie_intro = dict_item.get('movie_intro', '')
        movie_image_url = dict_item.get('movie_image_url', '')

        # 老版本插入方法
        # insert_into_db = """
        #     insert into {}
        #         (
        #             rank, title, rating, rating_count, subject,
        #             movie_detail_page, duration, release_date,  movie_intro,
        #             movie_image_url
        #         ) values (
        #             {}, "{}", {}, "{}", "{}", "{}", {}, "{}", "{}", "{}");
        # """.format(self.dbtable, rank, title,
        #            rating, rating_count, subject, movie_detail_page,
        #            duration, release_date,movie_intro, movie_image_url
        #            )
        # print("我来看看sql是怎么样的：" + insert_into_db)
        # 执行sql
        # self.cur.execute(insert_into_db)

        # 更简单的插入sql
        insert_into_db = """
                    insert into {} 
                        (
                            rank, title, rating, rating_count, subject, 
                            movie_detail_page, duration, release_date,  movie_intro, 
                            movie_image_url
                        ) values (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """.format(self.dbtable)

        print("我来看看sql是怎么样的：" + insert_into_db)
        self.cur.execute(insert_into_db,
                         (rank, title, rating, rating_count, subject, movie_detail_page, duration, release_date, movie_intro, movie_image_url))


        self.conn.commit()

        return item

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()


class doubanDataToMySqlPipeline():
    def __init__(self):
        # 定义服务器信息
        self.host = '127.0.0.1'
        self.user = 'root'
        self.passwd = ''
        self.port = 3306
        self.database_name = 'douban'
        self.database_table = 'douban250'
        self.charset = 'utf8'

    def open_spider(self, spider):
        # 打开爬虫的时候就连接并创建数据库
        self._connect_server_to_create_database()
        self._create_table()

    def _connect_server_to_create_database(self):
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.passwd,
                                    port=self.port, charset=self.charset)
        self.cur = self.conn.cursor()

        # 创建数据库名
        create_database_sql = """
            create database if not exists {} character set {}
        """.format(self.database_name, self.charset)

        self.cur.execute(create_database_sql)
        # 提交
        self.conn.commit()
        # 关闭数据库连接
        self.conn.close()

    def _create_table(self):
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.passwd, database=self.database_name,
                                    port=self.port, charset=self.charset)
        # 获取游标
        self.cur = self.conn.cursor()

        # 创建语句rank是mysql保留字，需要用`rank`进行转义。
        create_table_sql = """
                    create table if not exists `{}`
                        (
                            `id` int AUTO_INCREMENT not null,
                            `rank` int not null,
                            `title` varchar(255),
                            `rating` decimal(3, 1),
                            `rating_count` char(100),
                            `subject` varchar(255) default '' ,
                            `movie_detail_page` varchar(255) not null,
                            `duration` int not null,
                            `release_date` varchar(255) not null,
                            `movie_intro` varchar(255) default '',
                            `movie_image_url` varchar(255) not null,
                            primary key (`id`)
                        )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='豆瓣top250'
                """.format(self.database_table)
        # 执行sql
        self.cur.execute(create_table_sql)
        # 提交更改
        self.conn.commit()

    def process_item(self, item, spider):
        # 获取item
        dict_item = dict(item)
        # 从字典取值
        rank = dict_item.get('rank', '')  # 取值，没有取到就为空
        title = dict_item.get('title') or ''  # 也可以这样取，如果没取到就为空
        rating = dict_item.get('rating', '')
        rating_count = dict_item.get('rating_count', '')
        subject = dict_item.get('subject', '')
        movie_detail_page = dict_item.get('movie_detail_page', '')
        duration = dict_item.get('duration', '')
        release_date = dict_item.get('release_date', '')
        movie_intro = dict_item.get('movie_intro', '')
        movie_image_url = dict_item.get('movie_image_url', '')

        # 插入语句，rank是mysql的保留字，需要用`rank`进行转义。
        insert_into_db_sql = """
                    insert into {}
                        (`rank`, title, rating, rating_count, subject, movie_detail_page, duration, release_date, movie_intro, movie_image_url)
                            values ({}, "{}", {}, "{}", "{}", "{}", {}, "{}", "{}", "{}");
                """.format(self.database_table, rank, title, rating, rating_count, subject,
                           movie_detail_page, duration, release_date, movie_intro, movie_image_url)
        # 提交数据
        print('我想看看SQL语句呀：----------------------------------------------', insert_into_db_sql)
        self.cur.execute(insert_into_db_sql)
        # 提交更改
        self.conn.commit()

        return item

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

class overWriteDoubanImagePipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        # 获取url
        image_url = item['movie_image_url']
        if image_url:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            print(image_url + "===" * 100)
            # 请求
            yield scrapy.Request(
                    url=image_url,
                    headers=headers,
                    meta={'item': item},
                    dont_filter=True
            )
            # 也可以单个拿
            # yield scrapy.Request(url=image_url, meta={'item': item['title']})

    def file_path(self, request, response=None, info=None, *, item=None):
        # 将item直接拿过来
        item = request.meta['item']
        # 获取图片名称
        file_title = item['title']
        print("文件名为：" + "*"*50 + file_title)
        # 获取图片后置
        file_suffix = item['movie_image_url'].split('.')[-1]
        print("文件后缀为：" + "*"*50 + file_suffix)
        # 组合filename
        filename = file_title + '.' + file_suffix

        # 保存文件
        return u"images/{}".format(filename) # 记得去settings.py中设置一下文件保存路径

    def item_completed(self, results, item, info):
        # 添加下载结果处理
        file_paths = [x['path'] for ok, x in results if ok]
        if not file_paths:
            print(f"Failed to download image for item: {item.get('title', 'unknown')}")
        return item

class DoubantopPipeline:
    def process_item(self, item, spider):
        return item
