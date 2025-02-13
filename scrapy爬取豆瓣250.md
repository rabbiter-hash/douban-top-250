# Scrapy爬取豆瓣电影TOP250并保存数据、下载海报图片

利用scrapy爬取数据并保存到Excel，Sqlite，Mysql，Json，Csv。其中Json和csv文档，scrapy是集成了的，这里主要解决一下中文乱码的问题。目标网站——https://movie.douban.com/top250。需要爬取的字段为**排名**，**中文标题**，**评分**，**评价人数**，**电影的主题**，内页的**片长**，上**映日期**还有**电影简介**。

![img](https://article.biliimg.com/bfs/article/4aa545dccf7de8d4a93c2b2b8e3265ac0a26d216.png)

环境：

  ---windows 11

  ---python 3.8.9

  ---Pycharm

  ---scrapy 2.7.1

![img](https://article.biliimg.com/bfs/article/4aa545dccf7de8d4a93c2b2b8e3265ac0a26d216.png)

首先打开windows命令终端，切换到想保存项目的文件夹，如：D:\Python Porjects：

```javascript
cd D:\Python Projects
```

新建scrapy项目：

```python
scrapy startproject douban # douban是项目名
```

切换到douban文件夹：

```python
cd douban
```

在该文件夹下创建两个爬虫模板：

```python
scrapy genspider db douban.com # scrapy的基础爬虫模板，db是爬虫名，douban.com是允许爬取的域名
scrapy genspider dbcrawler douban.com # scrapy的crawl模板，针对有规则的域名很好爬，dbcrawler是爬虫名，douban.com是允许爬取的域名。
```

创建好后，在windows资源管理器中打开项目所在目录，右键**Open Folder as PyCharm Project**。也可以先打开PyCharm，在PyCharm的欢迎界面将项目文件夹拖入。

打开之后，为项目创建一个虚拟环境，懒的话可以直接用略过。虚拟环境的用处一般是项目需要给别人用，需要打包当前环境下所有的依赖项的时候。

虚拟环境创建方法：在PyCharm中，File——settings——Project:（项目名）——单击Python Interpreter，找到Python Interpreter最右边的**齿轮**，单击它，Add，在弹出的选项中（Virtualenv Environment）选择Location（路径），Base interpreter为默认当前默认解释器就好。其他的不用填，直接点ok。

创建好虚拟环境后，所有的依赖项都从虚拟环境安装。在当前项目下的PyCharm中，选择底部的Terminal，打开Pycharm内置的终端，查看当前虚拟环境下的依赖项：

```python
pip list # 一般查看
pip freeze # 类似拿到别人的项目的时候，有个requirements.txt的文件一样的内容，也就是 包名==版本号
pip install -r requirements.txt # 如果是拿到别人的项目，且人已配置好依赖项到requirements.txt里可以这样安装；
pip install <packagename> # 单独安装
pip install <packagename> -i https://pypi.tuna.tsinghua.edu.cn/simple # 单独从清华源安装
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple # 永久将pip源设置为清华源，该设置只需要设置一次，永久使用。
```

当自己的项目需要给别人用时，依赖项打包：

```python
pip freeze > requirements.txt # 将虚拟环境下的所有依赖项打包至txt文件
```

<hr >
**正文开始**

<hr >
## 1，设置爬虫字段

安装好依赖项后，切换到项目下的**items.py**文件，先来设置预爬取的字段，代码如下：

```python
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    rank = scrapy.Field() # 电影排名
    title = scrapy.Field() # 电影中文名
    rating = scrapy.Field() # 电影评分
    rating_count = scrapy.Field() # 电影评分总人数
    subject = scrapy.Field() # 电影主题，中心思想，一句话电影描述
    movie_url = scrapy.Field()  # 电影详情页链接，电影内页

    # 以下是详情页的四个个字段
    duration = scrapy.Field() # 电影的时长
    release_date = scrapy.Field() # 电影的上映日期
    movie_intro = scrapy.Field() # 电影的简介
    movie_image_url = scrapy.Field() # 图片地址，下载使用
```




## 2，编写爬虫文件：

接着切换到项目文件夹下的爬虫文件**db.py**，开始解析响应。代码如下：

```python
import scrapy
from scrapy import Selector
from ..items import DoubanItem

class DbSpider(scrapy.Spider):
    name = 'db'
    allowed_domains = ['douban.com']
    start_urls = ['https://movie.douban.com/top250']

    def parse(self, response, **kwargs):

        # print(response.url) # 打印一下响应链接
        sel = Selector(response) # 页面选择器

        movie_lists = sel.xpath('.//ol[@class="grid_view"]/li') # 获取当前页面下的所有电影列表
        # print(len(movie_lists)) # 应该是25
        # 从movie_lists解析所需数据
        for movie_list in movie_lists:
            movie_item = DoubanItem() # 实例化一个scrapy的item对象，这个对象类似字典，但它实际上是一个对象，取数据的时候可以强制转换成字典
            # movie_list也是一个选择器，也可以用xpath,css,re等语法进行提取数据，字段要与items.py里设置的字段一直
            movie_item['rank'] = movie_list.xpath('.//div[@class="pic"]/em/text()').extract_first() # 排名，取出第一个，后续的用生成器生成
            movie_item['title'] = movie_list.css('span.title::text').extract_first() # 中文标题
            movie_item['rating'] = movie_list.css('span.rating_num::text').extract_first() #
            movie_item['rating_count'] = movie_list.xpath('.//div[@class="star"]/span[last()]/text()').extract_first() # 评价人数，这里span不好取，但是它是最后一个，所以用span[last()]来取
            movie_item['subject'] = movie_list.css('span.inq::text').extract_first() # 电影主题

            # 详情页的三个参数需要跳转，需要另外一个函数来处理，先提取详情页（内页）的链接
            movie_item['movie_url'] = movie_list.xpath('.//div[@class="hd"]/a/@href').extract_first()
            detail_page_url = movie_list.xpath('.//div[@class="hd"]/a/@href').extract_first() # 本质上是movie_item['movie_url']，为了区别再定义一个字段
            # print(movie_item['rank'], movie_item['title'], movie_item['rating'], movie_item['rating_count'],
            #       movie_item['subject'], movie_item['movie_url']) # 打印是否符合语气，减少不必要的错误

            # 请求详情页去请求其他的三个字段
            yield scrapy.Request(url=detail_page_url, callback=self.parse_details, meta={'item': movie_item}) # 将movie_item对象传出
            # yield scrapy.Request(url=detail_page_url, callback=self.parse_details, cb_kwargs={'item': movie_item}) # 官方推荐用cb_kwargs字段，将movie_item对象传出

    def parse_details(self, response, **kwargs):
        movie_item = response.meta['item'] # 接收传过来的movie_item对象
        # movie_item = kwargs['item'] # 如果用的是官方推荐的cb_kwargs

        # 到内页（详情页）后也可以将其包装成一个Selector对象，scrapy语法里也可以直接从response中提取数据，如下
        movie_item['duration'] = response.xpath('.//span[@property="v:runtime"]/@content').extract_first() # 提取片长
        movie_item['release_date'] = response.xpath('.//span[@property="v:initialReleaseDate"]/@content').extract()
        # 判断一下上映日期的长度，并将其转换成字符串
        if len(movie_item['release_date']) != 0:
            movie_item['release_date'] = ','.join(movie_item['release_date']) # 将列表拆分成字符串
        else:
            movie_item['release_date'] = '' # 空字符串

        movie_item['movie_intro'] = response.xpath('normalize-space(.//span[@property="v:summary"]/text())').extract_first() # 电影简介
        movie_item['movie_image_url'] = response.xpath('.//div[@id="mainpic"]/a/img/@src').extract_first() # 电影海报
        yield movie_item # 最终生成movie_item对象
```

在终端运行**scrapy crawl db**，字段都采集到了，并且数据格式都正确。但是，这仅仅是第一页的数据，接下来修改一下爬虫代码：

```python
import scrapy
from scrapy import Selector
from ..items import DoubanItem

class DbSpider(scrapy.Spider):
    name = 'db'
    allowed_domains = ['douban.com']
    start_urls = ['https://movie.douban.com/top250']

    def parse(self, response, **kwargs):

        # print(response.url) # 打印一下响应链接
        sel = Selector(response) # 页面选择器

        movie_lists = sel.xpath('.//ol[@class="grid_view"]/li') # 获取当前页面下的所有电影列表
        # print(len(movie_lists)) # 应该是25
        # 从movie_lists解析所需数据
        for movie_list in movie_lists:
            movie_item = DoubanItem() # 实例化一个scrapy的item对象，这个对象类似字典，但它实际上是一个对象，取数据的时候可以强制转换成字典
            # movie_list也是一个选择器，也可以用xpath,css,re等语法进行提取数据，字段要与items.py里设置的字段一直
            movie_item['rank'] = movie_list.xpath('.//div[@class="pic"]/em/text()').extract_first() # 排名，取出第一个，后续的用生成器生成
            movie_item['title'] = movie_list.css('span.title::text').extract_first() # 中文标题
            movie_item['rating'] = movie_list.css('span.rating_num::text').extract_first() #
            movie_item['rating_count'] = movie_list.xpath('.//div[@class="star"]/span[last()]/text()').extract_first() # 评价人数，这里span不好取，但是它是最后一个，所以用span[last()]来取
            movie_item['subject'] = movie_list.css('span.inq::text').extract_first() # 电影主题

            # 详情页的三个参数需要跳转，需要另外一个函数来处理，先提取详情页（内页）的链接
            movie_item['movie_url'] = movie_list.xpath('.//div[@class="hd"]/a/@href').extract_first()
            detail_page_url = movie_list.xpath('.//div[@class="hd"]/a/@href').extract_first() # 本质上是movie_item['movie_url']，为了区别再定义一个字段
            # print(movie_item['rank'], movie_item['title'], movie_item['rating'], movie_item['rating_count'],
            #       movie_item['subject'], movie_item['movie_url']) # 打印是否符合语气，减少不必要的错误

            # 请求详情页去请求其他的三个字段
            yield scrapy.Request(url=detail_page_url, callback=self.parse_details, meta={'item': movie_item}) # 将movie_item对象传出
            # yield scrapy.Request(url=detail_page_url, callback=self.parse_details, cb_kwargs={'item': movie_item}) # 官方推荐用cb_kwargs字段，将movie_item对象传出

        # 获取下一页链接，因为起始页是https://movie.douban.com/top250，所以不需要担心漏采的问题。
        next_page_urls = response.xpath('.//div[@class="paginator"]/span/a/@href').extract() # “后页的链接”
        # 判定是否有“后页”链接
        if len(next_page_urls) > 0:
            # 说明有后页链接
            next_page_url = response.urljoin(next_page_urls[0]) # 将响应的根链接与抓取到的后页进行拼接，相当于下面的注释行代码
            print('下一页的链接地址为：---------------------------------------{}'.format(next_page_url))
            # next_page_url = self.start_urls[0] + next_page_urls[0] # 将起始页链接与抓取到的后页链接进行拼接
            # 提取到了下一页链接，还是得交给爬虫进行处理
            yield scrapy.Request(url=next_page_url, callback=self.parse) # 回调是函数本身
            # 这样就完成了分页爬取

    def parse_details(self, response, **kwargs):
        movie_item = response.meta['item'] # 接收传过来的movie_item对象
        # movie_item = kwargs['item'] # 如果用的是官方推荐的cb_kwargs

        # 到内页（详情页）后也可以将其包装成一个Selector对象，scrapy语法里也可以直接从response中提取数据，如下
        movie_item['duration'] = response.xpath('.//span[@property="v:runtime"]/@content').extract_first() # 提取片长
        movie_item['release_date'] = response.xpath('.//span[@property="v:initialReleaseDate"]/@content').extract()
        # 判断一下上映日期的长度，并将其转换成字符串
        if len(movie_item['release_date']) != 0:
            movie_item['release_date'] = ','.join(movie_item['release_date']) # 将列表拆分成字符串
        else:
            movie_item['release_date'] = '' # 空字符串

        movie_item['movie_intro'] = response.xpath('normalize-space(.//span[@property="v:summary"]/text())').extract_first() # 电影简介
        movie_item['movie_image_url'] = response.xpath('.//div[@id="mainpic"]/a/img/@src').extract_first() # 电影海报
        # yield movie_item # 最终生成movie_item对象
```

### 2.1 翻页逻辑问题（重要）

修改的部分在第一个回调函数parse()的最后，next_page_urls部分的代码就是翻页的逻辑。

有一些逻辑（比如scrapy的crawl模板），再比如从开始请求的时候就构造好十个页面的链接，代码如下：

```python
class DbSpider(scrapy.Spider):
    name = 'db'
    allowed_domains = ['douban.com']
    start_urls = ['https://movie.douban.com/top250']

    def start_requests(self):
        for page in range(0, 10):
            url = f'https://movie.douban.com/top250?start={page*25}&filter='
            yield scrapy.Request(url=url)
            
    def parse(self, response, **kwargs):
		pass
```

上面的两种情况可能会导致多爬25条，那是因为第一页的链接有两个：

```python
https://movie.douban.com/top250
https://movie.douban.com/top250?start=0&filter=
```

上面这两个链接，在scrapy调度器里是两个不同的url，它会给两个链接进行排队，然后交给引擎，引擎再交给下载器下载，下载后引擎交给爬虫处理，爬虫处理出来的数据是一样的，但是链接不一样，所以会多出25条。要解决这个问题，最简单的办法就是将start_urls改为：https://movie.douban.com/top250?start=0&filter=，釜底抽薪。





## 3，下载器中间件设置COOKIES：

### a, 为请求设置cookies

实现好了翻页之后，最重要要做的事就是模拟登录，豆瓣电影，请求过多，Ip就会被封了，登录后就可以无限访问。设置cookies是一种很好的办法。先从网页登录一下豆瓣账号，打开浏览器的开发者调试工具，将请求头中的cookies复制下来。然后切换到项目文件下的middlewares.py——下载器中间件，为请求设置cookies，代码如下：

```python
# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

def get_douban_cookies():
    cookie_str = 'yourcookies'
    cookie_dict = {i.split('=')[0]:i.split('=')[1] for i in cookie_str.split('; ')}
    return cookie_dict

COOKIE_DICT = get_douban_cookies() # 获取cookie，为了不每次调用函数，先将其转换成值

class DoubanSpiderMiddleware:
    pass

class DoubanDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        pass

    def process_request(self, request, spider):
        request.cookies = COOKIE_DICT # 将获取到的cookie写入请求
        return None

    def process_response(self, request, response, spider):
        pass

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        pass
```

为了简化代码，将原来的爬虫中间件全部pass掉了，下载器中间件的里的类方法也pass掉了。只在类方法process_request()中设置了cookies。运行的时候还是得加上。

### b，随机的User-Agent

如果要切换随机的User-Agent，也是在中间件里定义，代码如下：

```python
from faker import Faker

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

def get_douban_cookies():
    cookie_str = ''
    cookie_dict = {i.split('=')[0]:i.split('=')[1] for i in cookie_str.split('; ')}
    return cookie_dict

COOKIE_DICT = get_douban_cookies() # 获取cookie，为了不每次调用函数，先将其转换成值

class doubanRandomUserAgentMiddlewares():
    def __init__(self):
        self.faker = Faker() # 看名字就知道是干啥的
    
    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', self.faker.user_agent()) # 设置随机UA
```

### c，为请求设置代理或者代理池（略）

写好后，在项目文件夹下的**settings.py**文件中开启中间件，代码如下：

```python
DOWNLOADER_MIDDLEWARES = {
   'douban.middlewares.DoubanDownloaderMiddleware': 543, # 下载中间件设置cookies
   'douban.middlewares.doubanRandomUserAgentMiddlewares': 544, # 随机切换UA
}
```



![img](https://article.biliimg.com/bfs/article/4aa545dccf7de8d4a93c2b2b8e3265ac0a26d216.png)

## 4，Scrapy数据管道保存数据

scrapy处理数据用到的是管道文件pipelines.py，我打算保存数据到csv（内置），json（这个其实scrapy内置了，但是中文会乱码，通过管道来处理，Excel，Sqlite，Mysql。

首先csv和json保存方法很简单，打开终端：

```python
scrapy crawl db -o douban.csv # 这样数据就会保存到csv，中文在windows系统下用excel打开会乱码，需用到数据管道
scrapy crawl db -o douban.json # 保存json文件，遇到中文会乱码，需用管道处理
```

**管道文件编写都在项目文件夹下的pipelines.py中。**

### a，保存Json文件数据的管道：

```python
import json
import codecs

class doubanDataToJson():
    def __init__(self):
        self.file = codecs.open('douban.json', mode='w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line) # 写入

        return item
    
    def close_spider(self, spider):
        self.file.close()
```

写好之后在项目文件夹下的settings.py文件中配置管道：

```python
ITEM_PIPELINES = {
   'douban.pipelines.doubanDataToJson': 300, # 保存json文件
}
```

### b，保存数据到csv文件的管道：

```python
import csv
class doubanDataToCsv():

    def __init__(self):
        self.headers = (('排名', '标题', '评分', '评论人数', '电影主题', '链接', '片长', '上映日期', '电影简介', '电影海报'))
        self.filename = 'douban.csv'

    def open_spider(self, spider):
        self.file = open(self.filename, mode='a', newline='', encoding='utf-8-sig')
        self.csvWriter = csv.writer(self.file)
        self.csvWriter.writerow(self.headers)

    def process_item(self, item, spider):
        dict_item = dict(item)
        # 从字典取值
        rank = dict_item.get('rank', '')  # 取值，没有取到就为空
        title = dict_item.get('title') or ''  # 也可以这样取，如果没取到就为空
        rating = dict_item.get('rating', '')
        rating_count = dict_item.get('rating_count', '')
        subject = dict_item.get('subject', '')
        movie_url = dict_item.get('movie_url', '')
        duration = dict_item.get('duration', '')
        release_date = dict_item.get('release_date', '')
        movie_intro = dict_item.get('movie_intro', '')
        movie_image_url = dict_item.get('movie_image_url', '')

        datas = []
        datas.append([rank, title, rating, rating_count, subject, movie_url, duration,
                      release_date, movie_intro, movie_image_url])

        for data in datas:
            self.csvWriter.writerow(data)

        return item

    def close_spider(self, spider):
        self.file.close()
```

只要将encoding的值写成utf-8-sig，用excel打开的时候就不会出现乱码的情况。写好之后在settings.py中配置管道。

```python
ITEM_PIPELINES = {
   'douban.pipelines.doubanDataToJson': 300, # 保存数据到json
   'douban.pipelines.doubanDataToCsv': 301, # 保存数据到csv
}
```

### c，保存数据到Excel文档的管道：

```python
import openpyxl

class doubanDataToExcel():
    def __init__(self):
        self.wb = openpyxl.Workbook() # 创建工作簿
        self.ws = self.wb.active # 获取表
        # self.ws = self.wb.create_sheet('top250') # 也可以创建表
        self.headers = (('排名', '标题', '评分', '评论人数', '电影主题', '链接', '片长', '上映日期', '电影简介', '电影海报'))
        self.filename = 'doubantop250.xlsx'

    def open_spider(self, spider):
        # 当爬虫启动时要处理的事情，可以将上面构造函数的内容全部移至此处，它在scrapy的管道中功能就类似于构造函数
        self.ws.append(self.headers)


    def process_item(self, item, spider):
        # item在scrapy中是一个item对象，类似字典，但又不是字典，所以将数据转换一下
        dict_item = dict(item)
        # 从字典取值
        rank = dict_item.get('rank', '') # 取值，没有取到就为空
        title = dict_item.get('title') or '' # 也可以这样取，如果没取到就为空
        rating = dict_item.get('rating', '')
        rating_count = dict_item.get('rating_count', '')
        subject = dict_item.get('subject', '')
        movie_url = dict_item.get('movie_url', '')
        duration = dict_item.get('duration', '')
        release_date = dict_item.get('release_date', '')
        movie_intro = dict_item.get('movie_intro', '')
        movie_image_url = dict_item.get('movie_image_url', '')

        # 将item数据逐一加入到excel表格
        self.ws.append((rank, title, rating, rating_count, subject, movie_url,
                        duration, release_date, movie_intro, movie_image_url))

        self.wb.save(self.filename) # 每追加一条保存一次
        
        return item # 一定要return，不然下一个管道拿不到数据;如果当前为最后一个管道，那么终端不会有打印记录

    def close_spider(self, spider):
        # 当爬虫关闭时要做的事情，收尾工作
        self.wb.save(self.filename) # 爬虫关闭时候再次保存
        self.wb.close() # 关闭文档
```

管道写好后，在项目文件夹下的settings.py中启用管道：

```python
ITEM_PIPELINES = {
   'douban.pipelines.doubanDataToJson': 300, # 保存数据到json
   'douban.pipelines.doubanDataToCsv': 301, # 保存数据到csv
   'douban.pipelines.doubanDataToExcel': 302, # 保存数据到excel
}
```

### d，保存数据到sqlite数据库的管道：

```python
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
```

同样的，在settings.py中开启管道：

```python
ITEM_PIPELINES = {
   'douban.pipelines.doubanDataToJson': 300, # 保存数据到json
   'douban.pipelines.doubanDataToCsv': 301, # 保存数据到csv
   'douban.pipelines.doubanDataToExcel': 302, # 保存数据到excel
   'douban.pipelines.doubanDataToSqlite': 303, # 保存数据到sqlite
}
```

### e，第五个管道是MySql，代码如下：

```python
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

```

写好之后在settings.py中配置管道：

```python
ITEM_PIPELINES = {
   'douban.pipelines.doubanDataToJson': 300, # 保存数据到json
   'douban.pipelines.doubanDataToCsv': 301, # 保存数据到csv
   'douban.pipelines.doubanDataToExcel': 302, # 保存数据到excel
   'douban.pipelines.doubanDataToSqlite': 303, # 保存数据到sqlite
   'douban.pipelines.doubanDataToMySql': 304, # 保存数据到mysql
}
```

### f，保存海报图片的管道：

我在预设字段的时候预设了电影的海报，那就最后再配置一个下载文件的管道，这个管道要继承scrapy内置的文件管道，对海报图片进行重命名（以电影名称命名），代码如下：

```python
class overWriteDoubanImagePipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        # 获取url 如果出现TypeNone之类的字段，url是正确的，那么就是没获取到内容，就需要考虑防盗链referrer和headers了
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
```

写好之后在settings.py中配置管道并开启文件存储路径：

```python
ITEM_PIPELINES = {
   'douban.pipelines.doubanDataToJson': 300, # 保存数据到json
   'douban.pipelines.doubanDataToCsv': 301, # 保存数据到csv
   'douban.pipelines.doubanDataToExcel': 302, # 保存数据到excel
   'douban.pipelines.doubanDataToSqlite': 303, # 保存数据到sqlite
   'douban.pipelines.doubanDataToMySql': 304, # 保存数据到mysql
   'douban.pipelines.overWriteDownloadImageFilePath': 305, # 下载海报图片的管道
}
FILES_STORE = 'playbill' # 图片文件存储位置
```

下载海报图片没有继承scrapy的ImagesPipeline，因为scrapy的图片管道是继承文件管道的，而且scrapy在请求图片下载的时候可能会多几个字节少几个字节都是有可能的，但是下载文件肯定是原数据下载，也就是说，如果在下载高清图片的时候，图片管道和文件管道的质量可能会相差很多。用scrapy下载文件，推荐用文件管道。如果遇到因为robots文件规则禁止下载图片的话，在settings.py里将遵循robots的规则设定改为False就行了：

```python
# Obey robots.txt rules
ROBOTSTXT_OBEY = False # 将True改成False
```

至此，一个爬取豆瓣电影TOP250的爬虫就制作完成了。

最后运行：

scrapy crawl db

不出意外的话，所有数据都会保存到指定的位置。