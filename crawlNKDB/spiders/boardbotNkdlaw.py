# -*- coding: utf-8 -*-
import scrapy
import re
from crawlNKDB.items import CrawlnkdbItem

from bs4 import BeautifulSoup
import requests

class BoardbotnkdlawSpider(scrapy.Spider):
    name = 'boardbotNkdlaw'

# 해당 사이트에서 시작한다.
# * 함수1 > def start_requests(self):
# start_url없어도 가장 먼저 시작하는 함수
# 여러개 사이트 크롤링할 때, 각각 다르게 동작할 때는 start_requests 함수를 구현하고  start_requests 함수에서 별도의 콜백함수를 구현해서 크롤링할 때마다 다르게 동작할 수 있다. 
    def start_requests(self):
        start_url = "http://nkd.or.kr/pds/nk/index/1/category/law"
        yield scrapy.Request(url = start_url, callback = self.parse, meta={'start_url':start_url})

# * 함수2 def parse(self, response): # 북한자료 북한말 board의 각 페이지 접근하는 함수
# def parse(self, response):
# url 가져온다.
    def parse(self, response):
        # >> 없는 경우
        start_url = response.meta['start_url']
        response = requests.get(start_url)
        source = response.text
        soup = BeautifulSoup(source, 'html.parser')

        last_page_list = soup.findAll("a", {"class": "next", "title": '마지막 페이지'})
        # print(last_page_list)
        # ex. [<a class="next" href="/pds/nk/index/29" title="마지막 페이지">&gt;&gt;</a>]
        # >> 없는 경우
        if not last_page_list:
            # maximum = 0
            # page = 2
            # while True:
            #     page_list = soup.findAll("a", {"href": '/pds/nk/index/' + str(page)})
            #     if not page_list:
            #         maximum = page - 1
            #         break
            #     page = page + 1
            # last_page_no = maximum
            last_page_no = 1
        # >> 있는 경우, 마지막 페이지까지 찾기
        else:
            last_page_no = re.findall("\d+", str(last_page_list[0]))
            last_page_no = int(last_page_no[0])

        page_no = 1
        while True:
            if page_no > last_page_no:
                break
            link = "http://nkd.or.kr/pds/nk/index/" +  str(page_no) + "/category/law"
            print(link)
            yield scrapy.Request(link, callback = self.parse_each_pages, meta={'link': link,'page_no':page_no, 'last_page_no':last_page_no})
            page_no += 1

		# 원래 페이지가 1~마지막페이지까지 반복해
		# 만약에 페이지가 마지막페이지와 같다면 종료
		# 페이지의 link를 가져온다. # 페이지의 link 출력
		# 그리고 yield(페이지링크, 콜백 각각의 페이지를 처리하는 함수를 부른다.)

# 각 페이지마다 제목에 해당하는 url 가져온다.
# * 함수3 def parse_each_pages(self, response):
	# response가 있어야 이 함수로 넘어갈 수 있다.
    def parse_each_pages(self, response):
        page_no = response.meta['page_no']
        last_page_no = response.meta['last_page_no']

        last = response.xpath('//*[@id="contents"]/table/tbody/tr[1]/td[1]/text()').get()
        if page_no == last_page_no:
            first = 0
        else:
            first = response.xpath('//*[@id="contents"]/table/tbody/tr[20]/td[1]/text()').get()

        category_last_no = int(last) - int(first)+1
        category_no = 1

        while 1:
        # 해당 url을  item에 넣어준다.
            if(category_no > category_last_no):
                break
            category_link = response.xpath('//*[@id="contents"]/table/tbody/tr[' + str(category_no) + ']/td[2]/a/@href').get()
            url =  "http://nkd.or.kr" + category_link
 			# item 객체생성
            item = CrawlnkdbItem()
 			# item url에 할당
            yield scrapy.Request(url, callback=self.parse_category, meta={'item':item})
            category_no += 1

# * 함수4 각 항목마다 bodys, titles, writers, dates를 가져온다. def parse_category(self, response):
    def parse_category(self, response):
	# 각 항목마다 bodys, titles, writers, dates를 가져온다.
        title = response.xpath('//*[@id="contents"]/table/tbody/tr[1]/th/text()').extract()
        title_text = ''.join(title).strip()
        date =response.xpath('//*[@id="contents"]/table/tbody/tr[1]/th/div/span[2]/text()').extract()
        writer =response.xpath('//*[@id="contents"]/table/tbody/tr[1]/th/div/a/span/text()').extract()
        body =response.css('#read_content').xpath('string()').extract()
        body_text =''.join(body).strip()
        top_category = response.xpath('//*[@id="contents"]/div[1]/h3/text()').extract()
        published_institution = response.xpath('//*[@id="header"]/h1/a/img/@alt').extract()
        item = response.meta['item']
        item["post_title"] = title_text
        item["post_date"] = date
        item["post_body"] = body_text
        item["post_writer"] = writer
        item["published_institution"] = published_institution
        item["published_institution_url"]= "http://nkd.or.kr/"
        item["top_category"] = top_category

        yield item
