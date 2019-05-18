#!/bin/bash

rm data/result.json
scrapy runspider spider/scrapper.py -o data/result.json
python3 spider/converter.py
