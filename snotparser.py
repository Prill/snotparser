#!/usr/bin/env python

import subprocess, re

def parseTicket(number):
    process = subprocess.Popen(['snot', '-sr', str(number)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    rawTicket = process.stdout.readlines()
    for index, line in enumerate(rawTicket):
        print index, line,

parseTicket(171171)
