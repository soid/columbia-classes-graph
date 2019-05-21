#!/bin/bash

rm data/all-classes.json
scrapy runspider spider/allclasses.py -o data/all-classes.json
python3 spider/converter.py
