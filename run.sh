#!/bin/bash

rm data/result.json
scrapy runspider spider/scrapper.py -o data/result.json


