import re

import scrapy
from ..items import DoubantopItem

class BdoubanSpider(scrapy.Spider):
    name = "bdouban"
    allowed_domains = ["douban.com"]
    start_urls = ["https://movie.douban.com/top250"]

    def parse(self, response, **kwargs):
        # 直接从起始页进行解析
        movie_lists = response.xpath('.//ol[@class="grid_view"]/li')

        # print(len(movie_lists)) # 打印长度，看是否符合预期
        for movie_list in movie_lists:
            item = DoubantopItem()

            rank = movie_list.xpath('.//div[@class="pic"]/em/text()').get()
            title = movie_list.xpath('.//div[@class="hd"]/a/span[1]/text()').get()
            movie_detail_page = movie_list.xpath('.//div[@class="hd"]/a/@href').get()
            rating = movie_list.css('span.rating_num::text').get()
            rating_count = movie_list.xpath('.//div[@class="star"]/span[last()]/text()').get()
            rating_count = re.sub(r"人评价", "", rating_count) # 这里可以用replace，为了学习，用re.sub
            try:
                subject = movie_list.css('span.inq::text').get() # 可能会没有
            except Exception as e:
                subject = None

            item['rank'] = rank
            item['title'] = title
            item['movie_detail_page'] = movie_detail_page
            item['rating'] = rating
            item['rating_count'] = rating_count
            item['subject'] = subject

            # print(rank, title, movie_detail_page, rating, rating_count, subject, sep=" | ")
            yield scrapy.Request(url=response.urljoin(movie_detail_page), callback=self.parse_detail_page, meta={'item': item})
         翻页规则
        try:
            next_page = response.xpath('.//span[@class="next"]/a/@href').get()
        except Exception as e:
            next_page = None
            return
        if next_page is not None:
            next_page_url = response.urljoin(next_page[0])
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_detail_page(self, response, **kwargs):
        # 接收item
        item = response.meta['item']

        # 解析内页
        duration = response.xpath('.//span[@property="v:runtime"]/@content').get()
        release_date = response.xpath('.//span[@property="v:initialReleaseDate"]/@content').get()  # 电影的上映时间
        movie_intro = response.xpath('normalize-space(.//span[@property="v:summary"]/text())').get() # 电影的简介
        movie_image_url = response.xpath('.//div[@id="mainpic"]/a/img/@src').get()  # 电影的海报，用于下载

        item['duration'] = duration
        item['release_date'] = release_date
        item['movie_intro'] = movie_intro
        item['movie_image_url'] = movie_image_url

        yield item