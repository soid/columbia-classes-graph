#!/bin/bash

rm data/result.json
scrapy runspider spider/scrapper.py -o data/all-classes.json
python3 spider/converter.py
