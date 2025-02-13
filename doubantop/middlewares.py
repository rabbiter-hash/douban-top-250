# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from faker import Faker
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

def get_douban_cookies():
    # 用于下载器中间件DoubantopDownloaderMiddleware

    # 使用pycharm的自动换行会加上（）,这样可以保证数据不是一整串一整长行

    cookie_str = ('ll="118204"; bid=aFwvXUAFIOE; '
                  '_pk_id.100001.4cf6=09c8117cff6346d6.1736154053.; '
                  '__yadk_uid=GKKsI3f35NWRuAXyCGJ3BedGXzNZzjo1; '
                  '__utmz=223695111.1736154054.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); '
                  '_vwo_uuid_v2=D3632799F3C92B9E02D72FFB2026CB307|615995ac9e41bfc69118af8490cb4eed; '
                  'dbcl2="246011477:KYqkwLUCro0"; push_noty_num=0; push_doumail_num=0; '
                  '__utmv=30149280.24601; douban-fav-remind=1; __utmz=30149280.1739156773.6.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; ck=98Zl; '
                  '_pk_ses.100001.4cf6=1; ap_v=0,6.0; __utma=30149280.1408190954.1736154054.1739156773.1739338759.7; __utmb=30149280.0.10.1739338759; '
                  '__utmc=30149280; __utma=223695111.328612136.1736154054.1738919557.1739338759.6; __utmb=223695111.0.10.1739338759; '
                  '__utmc=223695111; frodotk_db="a338b8b47e84170fe9aa2a1d7b8c452d"')
    cookie_dict = {i.split('=')[0]:i.split('=')[1] for i in cookie_str.split('; ')}
    return cookie_dict

COOKIE_DICT = get_douban_cookies()

# 随机user-agent的一个下载器中间件
class doubanRandomUserAgentMiddlewares():
    def __init__(self):
        self.faker = Faker()  # 看名字就知道是干啥的

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', self.faker.user_agent())  # 设置随机UA

class DoubantopSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class DoubantopDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        # 请求的时候追加cookie
        request.cookies = COOKIE_DICT
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


