I wrote this scraper because wasn't able to master [Scrapy](https://scrapy.org/) for some reason.  Python 3.5+ is required.  This project is an [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://aiohttp.readthedocs.io/en/stable/) usage example.

Downloaded books will be stored in the `books` subdirectory, which is created if does not exist at the time of execution.  The scraper fails if it's unable to create or write to the `books` directory.
