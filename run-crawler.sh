#!/bin/bash

set -x

# TODO: figure out semester automatically
CURRENT_SEMESTER=2020-1

rm data/data-${CURRENT_SEMESTER}.json || true
scrapy runspider spider/allclasses.py --logfile spider.log -o data/data-${CURRENT_SEMESTER}.json
python3 spider/converter.py
