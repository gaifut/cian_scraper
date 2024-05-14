from scrapy import Spider
from scrapy.utils.url import url_query_parameter


class CianSpider(Spider):
    name = 'cian'
    start_urls = [
        'https://kazan.cian.ru/cat.php?deal_type=sale&'
        'engine_version=2&offer_type=flat&p=1&region=4777&room1=1'
    ]

    def parse(self, response):
        ROOM_INDEX = 0
        AREA_INDEX = 2
        FLOOR_INDEX = 4
        ID_INDEX = -2
        ALLOWED_VALUES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        for offers in response.css('div._93444fe79c--general--BCXJ4'):
            heading_text = offers.css(
                    'span[data-mark="OfferTitle"] span::text'
                ).get()
            print('heading text list', heading_text.split())
            if list(heading_text.split()[0])[0] not in ALLOWED_VALUES:
                continue
            else:
                rooms_values = list(heading_text.split()[ROOM_INDEX])
                rooms = ''
                page_number = url_query_parameter(response.url, 'p')
                for value in rooms_values:
                    try:
                        int_value = int(value)
                        rooms += str(int_value)
                    except ValueError:
                        break

                yield {
                    'heading': offers.css(
                        'span[data-mark="OfferTitle"] span::text').get(),
                    'rooms': rooms,
                    'area': heading_text.split()[AREA_INDEX],
                    'floor': heading_text.split()[FLOOR_INDEX],
                    'address': offers.css(
                        'a[data-name="GeoLabel"]::text').getall(),
                    'price': offers.css(
                        'span[data-mark="MainPrice"] span::text').get(),
                    'id': str(
                        offers.css(
                            'a._93444fe79c--link--VtWj6'
                        ).attrib['href']).split('/')[ID_INDEX],
                    'page_number': page_number,
                }
        show_more_button = response.xpath(
            '//a[contains(text(),"Показать еще")]').get()
        next_page = response.xpath(
            '//nav[@class="_93444fe79c--pagination--VL341"]//a[@class="_93444'
            'fe79c--button--KVooB _93444fe79c--link-button--ujZuh _93444fe79'
            'c--M--I5Xj6 _93444fe79c--button--WChcG"]/span[contains('
            'text(),"Дальше")]/parent::a/@href'
        ).get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
        else:
            if show_more_button is not None:
                yield response.follow(show_more_button, callback=self.parse)
