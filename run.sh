#!/bin/bash

rm spider/result.json
scrapy runspider spider/scrapper.py -o spider/result.json


