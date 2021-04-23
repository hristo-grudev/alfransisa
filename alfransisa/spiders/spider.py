import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import AlfransisaItem
from itemloaders.processors import TakeFirst
import requests

url = "https://www.alfransi.com.sa/Toolkit/GetListingPaging"

base_payload = "pageId=49&pagePortletID=967&page={}&condition=&lang=3&__RequestVerificationToken=o6R7f2fxJcPD9MKSJU4hM_-QExKTYav7FPIt1bu2azdXL_WwVZSeuvucrnn1TjdzEN-O2Io47caIOfnbozpYAxap5ak1"
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Origin': 'https://www.alfransi.com.sa',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.alfransi.com.sa/arabic/news',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'ASP.NET_SessionId=jybhuhd0kohp1jjukqscayga; __RequestVerificationToken=Z-kTmkK0kkl2CwGbFKoPDoVbM5-5b1NPZxrZDFPNIE6riqvkcbez0tBAPxHfco8bArKqZ29ZW7cDXXvEsG86klavfsY1; rl-sticky-key=u0021l2WMAs8jX5F2GIQAfjrtu4a1cusu1eIKXuOE8C7PetaCfaTNgSBsch6xtGUN456bH0oHUJ+NGDuVw5c=; TS013f72e6=01aeaced4be6a15c25dd6f9ce61664b5fb8316ada13e5836d46254bcd2539e143a9fafd757c34787202eb096a5966335b9fa087768; _gcl_au=1.1.268201267.1619175393; _ga=GA1.3.169284279.1619175394; _gid=GA1.3.417681706.1619175394; _scid=90d4cf4c-e690-41b7-90d5-871c4bdea9cd; SkwidCookie=LastViewedPage=49_&PVC-5-3=1&UserSessionID=jybhuhd0kohp1jjukqscayga&PVC-49-3=1; _gat_gtag_UA_150465195_1=1; TS013f72e6=01aeaced4b0154027c12392eeeb58a387ed99b018248e326c9b249bc10c3d5b0a58c8679d9469c0c762ed2d461551c2655b061748d; rl-sticky-key=!9iG4IQNUWPBxXo0Afjrtu4a1cusu1Q0aEkALpngHdxegtwf5wLb+cHXZEWxoNj8fRnwPuwxyqVyXQzc='
}


class AlfransisaSpider(scrapy.Spider):
	name = 'alfransisa'
	page = 1
	start_urls = ['https://www.alfransi.com.sa/arabic/news']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=base_payload.format(self.page))
		data = json.loads(data.text)
		data = scrapy.Selector(text=data['html'])

		post_links = data.xpath('//h3[@class="listingTitle"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if post_links:
			self.page += 1
			yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response):
		title = response.xpath('//h3[@class="detailTitle"]/text()').get()
		if not title:
			return
		description = response.xpath('//div[@class="detailBody contentText"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="detailDate"]/text()').get()

		item = ItemLoader(item=AlfransisaItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
