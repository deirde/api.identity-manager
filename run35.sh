#!/bin/bash

sudo kill -9 $(sudo lsof -t -i:8082) &> /dev/null
python3.5 -m pip install setuptools
python3.5 -m pip install -r requirements
python3.5 bootstrap.py
