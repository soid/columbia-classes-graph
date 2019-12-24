#!/bin/bash

set -x

rm data/all-classes.json || true
scrapy runspider spider/allclasses.py --logfile spider.log -o data/all-classes.json
python3 spider/converter.py
