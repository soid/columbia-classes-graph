#!/bin/bash

rm data/all-classes.json
scrapy runspider spider/scrapper.py -o data/all-classes.json
python3 spider/converter.py
