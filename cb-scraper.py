#!/usr/bin/env python
import os
import asyncio

import aiohttp
import aiofiles
from parsel import Selector

START_URL = 'http://www.classicbookshelf.com/library/'
TEXT_XPATH = '//p[position() >= 2 and position() < last() - 1]/text()'
MAX_CONN = 50 # max number of parallel HTTP connections


class Scraper:
    def __init__(self):
        self.session = None
        self.url = START_URL

        curdir = os.path.dirname(os.path.realpath(__file__))
        self.workdir = os.path.join(curdir, 'books')
        os.makedirs(self.workdir, exist_ok=True)

    async def __get_selector(self, url):
        async with self.session.get(url) as resp:
            return Selector(text=await resp.text())

    async def get_chapter_text(self, url):
        num = int(url.split('/')[-2])
        sel = await self.__get_selector(url)

        return (num, sel.xpath(TEXT_XPATH).getall(),)

    async def get_book_text(self, sel, book_url):
        tasks = []
        text = ''
        for href in sel.xpath('//a/@href').getall():
            if not href.startswith(book_url):
                continue

            # chapter to work with
            tasks.append(self.get_chapter_text(href))
        aio_result = await asyncio.gather(*tasks)

        # build text from list of chapters ordered by chapter id
        rd = {k:''.join(v) for k,v in aio_result}
        return ''.join(rd.values())

    async def download_book(self, book_url):
        sel = await self.__get_selector(book_url)
        text = await self.get_book_text(sel, book_url)

        bu = book_url.split('/')
        title, author = bu[-2], bu[-3]
        filename = '{}-{}.txt'.format(author, title)
        filename = os.path.join(self.workdir, filename)

        async with aiofiles.open(filename, 'w') as f:
            await f.write(text)
        print(book_url, '->', '/'.join(filename.split('/')[-2:]))

    async def get_book_list(self, url):
        book_urls = []
        sel = await self.__get_selector(url)

        for book_url in sel.xpath('//a/@href').getall():
            if book_url.startswith(url):
                book_urls.append(book_url)

        return book_urls

    async def parse_authors(self):
        book_urls = []
        sel = await self.__get_selector(self.url)

        tasks = []
        for href in sel.xpath('//a/@href').getall():
            if href[-4:] == '.htm':
                continue
            if href[-5:] == '/pop/':
                continue

            tasks.append(asyncio.create_task(self.get_book_list(href)))

        for book_list in await asyncio.gather(*tasks):
            book_urls += book_list

        tasks = []
        for book in book_urls:
            tasks.append(asyncio.create_task(self.download_book(book)))
        await asyncio.gather(*tasks)

    async def __call__(self):
        connector = aiohttp.TCPConnector(limit=MAX_CONN)
        self.session = aiohttp.ClientSession(connector=connector)
        try:
            await self.parse_authors()
        finally:
            await self.session.close()

if __name__ == '__main__':
    scraper = Scraper()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(scraper())
