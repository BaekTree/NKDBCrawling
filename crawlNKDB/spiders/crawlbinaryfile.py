# -*- coding: utf-8 -*-
import scrapy
import sys
from crawlNKDB.items import CrawlnkdbItem
import re
import pymongo
from pymongo import MongoClient #
import gridfs #
from tika import parser
from tempfile import NamedTemporaryFile
from itertools import chain
control_chars = ''.join(map(chr, chain(range(0, 9), range(11, 32), range(127, 160))))
CONTROL_CHAR_RE = re.compile('[%s]' % re.escape(control_chars))

print("Start crawling~ SDG!!!")

class CrawlbinaryfileSpider(scrapy.Spider):
    name = 'crawlbinaryfile'
    allowed_domains = ['www.nuac.go.kr']
    start_urls = ['http://www.nuac.go.kr/actions/BbsDataAction?cmd=list&_max=05&menuid=G0205&bbs_id=G0205&_template=03#']

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.start_urls = 'http://www.nuac.go.kr/actions/BbsDataAction?cmd=list&_max=05&menuid=G0205&bbs_id=G0205&_template=03#'
        self.client = pymongo.MongoClient('mongodb://eunjiwon:eunjiwon@localhost:27017')
        self.db = self.client['attachment']
        self.fs = gridfs.GridFS(self.db)

    def start_requests(self):
        yield scrapy.Request(self.start_urls, self.parse)

    def parse(self, response):
        total_page_text = response.xpath('//*[@id="stxt"]/text()').extract()
        # print(total_page_text)
        last_page_no = re.findall("\d+", str(total_page_text))
        page_no = 1
        # last_page_no[-1]
        last_page_no = int(last_page_no[-1])
        while True:
            if page_no > last_page_no:
                break
            link = "http://www.nuac.go.kr/actions/BbsDataAction?cmd=list&menuid=G0205&bbs_num=&bbs_id=G0205&bbs_idx=&order=&ordertype=&oldmenu=&parent_idx=&_max=05&_page=" + str(page_no) + "&_template=03&searchtype=bbs_title&keyword=&name_confirm=&real_name="
            # print(link)
            yield scrapy.Request(link, callback = self.parse_each_pages, meta={'page_no': page_no, 'last_page_no': last_page_no})
            page_no += 1

    def parse_each_pages(self, response):
        page_no = response.meta['page_no']
        last_page_no = response.meta['last_page_no']
        last = response.xpath('//*[@id="smain_all"]/table[2]/tbody/tr[1]/td[1]/div/font/text()').get()
        if page_no == last_page_no:
            category_last_no = int(last)
        else:
            first = response.xpath('//*[@id="smain_all"]/table[2]/tbody/tr[5]/td[1]/div/font/text()').get()
            category_last_no = int(last) - int(first) + 1
        category_no = 1
        while True:
            if(category_no > category_last_no):
                break
            category_link = '//*[@id="smain_all"]/table[2]/tbody/tr[' + str(category_no) + ']/td[3]/div/a/@onclick'
            onclick_text = response.xpath(category_link).extract()
            url = re.findall("\d+" ,str(onclick_text))
            url = 'http://www.nuac.go.kr/actions/BbsDataAction?cmd=view&menuid=G' + url[1] + '&bbs_id=G' + url[1] + '&bbs_idx=' + url[0] + '&parent_idx=&_template=03&_max=05&_page=' + str(page_no) + '&head='
            item = CrawlnkdbItem() #
            yield scrapy.Request(url, callback=self.parse_post, meta={'item':item})
            category_no += 1

    def parse_post(self, response):
        title = response.css('#smain_all > table > thead > tr > th font::text').get()
        table_text = response.css('#smain_all > table > tbody > tr.boardview2 td::text').extract()
        body = response.css('.descArea p::text').extract()
        top_categorys = response.xpath('//*[@id="left"]/ul/li[2]/ul/li[1]/a/text()').get()
        for text in table_text:
            if "작성일" in text:
                date = text
            if "작성자" in text:
                writer = text
        body_text = ''.join(body)
        item = response.meta['item']
        item['post_title'] = title.strip()
        item['post_date'] = date.strip()
        item['post_writer'] = writer.strip()
        item['post_body'] = body_text.strip()
        item['published_institution'] = "THE NATIONAL UNIFICATION ADVISORY COUNCIL"
        item['published_institution_url'] = "http://www.nuac.go.kr/actions/"
        item['top_category'] = top_categorys.strip()
        file_name = response.xpath('//*[@id="smain_all"]/table/tbody/tr[1]/td[2]/a/text()').get()
        if file_name:
            # if file_name.find("hwp") != -1:
            #     # Using other tool to handle hwp file
            #     print("@@@@ file name contains hwp : ", file_name)
            # else:
            file_download_url = response.xpath('//*[@id="smain_all"]/table/tbody/tr[1]/td[2]/a/@href').extract()
            file_download_url = "http://www.nuac.go.kr" + file_download_url[0]
            item['file_download_url'] = file_download_url
            item['file_name'] = file_name.strip()
            print("@@@@@@file name ", file_name)
            yield scrapy.Request(file_download_url, callback=self.save_file, meta={'item':item})
        else:
            print("###############file does not exist#################")
            yield item

    def save_file(self, response):
        item = response.meta['item']
        file_id = self.fs.put(response.body)
        item['file_id_in_fsfiles'] = file_id

        file_name = item['file_name']
        if file_name.find("hwp") != -1:
            tempfile = NamedTemporaryFile()
            tempfile.write(response.body)
            tempfile.flush()
            # Using other tool to handle hwp file 
            command = "hwp5txt " + tempfile.name + " --output=/home/eunjiwon/crawlNKDB/crawlNKDB/hwptotxt/" + file_name + ".txt"
            print("@@@@ file name contains hwp : ", file_name)
            print("execute following command ", command)
            os.system(command)

        else:
            # check saved status
            #temp_saving_file = "test_saving_fs.pdf"
            #with open(temp_saving_file, 'wb') as f:
            #f.write(self.fs.get(file_id).read())
            #print("#################3", self.fs.get(file_id).read())
            tempfile = NamedTemporaryFile()
            tempfile.write(response.body)
            tempfile.flush()
            #print("tempfile.name is : ", tempfile.name)
            extracted_data = parser.from_file(tempfile.name)
            #print("@@@@@@@@@@@@@@@extracted_data is : ", extracted_data)
            extracted_data = extracted_data["content"]
            extracted_data = CONTROL_CHAR_RE.sub('', extracted_data)
            extracted_data = extracted_data.replace('\n\n', '')
            #print("extracted_data is : ", extracted_data)
            tempfile.close()
            item['file_extracted_content'] = extracted_data
        yield item
