# Columbia University Course Map

I just wanted to see the class requirements on a graph. 

## Online

http://cugraph.info/

## Setup

You may need to run `setup.sh` first.


## Running Crawler Locally

Run `run-crawler.sh` for crawling data files.




## Running Debug Server Locally

Then run `run-debug-server.sh`. Navigate the browser to the provided URL.

## Development

Scrapy shell is very handy:

```
scrapy shell 'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=Michael+Collins+Columbia+University&utf8=&format=json'
...
>>> import json
>>> jsonresponse = json.loads(response.body_as_unicode())
>>> jsonresponse
>>> jsonresponse['query']
>>> import html
>>> from scrapy.selector import Selector
>>> s = Selector(text=html.unescape( jsonresponse['query']['search'][0]['snippet'] ))
>>> s.text()
```
