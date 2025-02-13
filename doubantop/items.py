# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubantopItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 初始化列表页字段
    rank = scrapy.Field() # 电影的排名
    title = scrapy.Field()  # 电影的中文名
    rating = scrapy.Field()  # 电影的评分
    rating_count = scrapy.Field() # 电影的评分人数
    subject = scrapy.Field() # 电影的主题
    movie_detail_page = scrapy.Field() # 电影的详情页，这个页面是提取内页信息的关键

    # 初始化内页字段
    duration = scrapy.Field() # 电影的时长
    release_date = scrapy.Field() # 电影的上映时间
    movie_intro = scrapy.Field() # 电影的简介
    movie_image_url = scrapy.Field() # 电影的海报，用于下载