I wrote this scraper because wasn't able to master [Scrapy](https://scrapy.org/) due to something.  Python 3.5+ is required.  This project is an example of usage of the wonderful [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://aiohttp.readthedocs.io/en/stable/) Python libraries.

Downloaded books will be stored in the `books` subdirectory, which is created if does not exist yet.  The scraper fails if it's unable to write to or create the `books` directory.
