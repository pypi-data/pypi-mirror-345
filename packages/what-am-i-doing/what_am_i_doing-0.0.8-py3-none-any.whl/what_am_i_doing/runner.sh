#!/bin/sh

if pidof "what-am-i-doing"; then
        kill -s 10 $(pidof what-am-i-doing)
    else
        python3 __main__.py
fi
# python3 _main.py