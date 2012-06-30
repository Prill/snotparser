#!/usr/bin/env python

import subprocess, re

ADMINISTRATIVE_START_MARKER = "XXXXXXXXXXXXXXXXXX  Administrative Information Follows  XXXXXXXXXXXXXXXXXXXXXX"

def parseTicket(number):
    process = subprocess.Popen(['snot', '-sr', str(number)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    bodyStartLine = 0
    administrativeStartLine = 0


    rawTicket = process.stdout.readlines()
    #print rawTicket[0]
    if "::::::::::::::" in rawTicket[0]: 
        return "BAD TICKET"

    enumeratedRawTicket = enumerate(rawTicket)
    for index, line in enumeratedRawTicket:
        if len(line) == 1:
            bodyStartLine = index
            break

    for index, line in enumeratedRawTicket:
        if ADMINISTRATIVE_START_MARKER in line:
            administrativeStartLine = index
            break
    return (bodyStartLine, administrativeStartLine)
    #return bodyStartLine

for i in range(100000,110000):
    print i, parseTicket(i)
