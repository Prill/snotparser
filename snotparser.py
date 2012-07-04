#!/usr/bin/env python

import subprocess, re

ADMINISTRATIVE_START_MARKER = "XXXXXXXXXXXXXXXXXX  Administrative Information Follows  XXXXXXXXXXXXXXXXXXXXXX"
TICKET_ERROR_MARKER = "::::::::::::::"

def parseTicket(number):
    process = subprocess.Popen(['snot', '-sr', str(number)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    bodyStartLine = 0
    administrativeStartLine = 0
    ticketDictionary = {}

    rawTicket = process.stdout.readlines()
    #print rawTicket[0]
    if TICKET_ERROR_MARKER in rawTicket[0]: 
        return None 

    #print "Finding bodyStartLine"
    enumeratedRawTicket = enumerate(rawTicket)
    for index, line in enumeratedRawTicket:
        if len(line) == 1:
            bodyStartLine = index
            break

    #print "Finding administrativeStartLine"
    for index, line in enumeratedRawTicket:
        if ADMINISTRATIVE_START_MARKER in line:
            administrativeStartLine = index
            break

    #print "Searching for from field"
    for line in rawTicket[0:bodyStartLine]:
        match = re.match(r"^From:\s*(?P<from_line>.*)$", line)
        if match:
            ticketDictionary["from_line"] = match.group("from_line")
            break

    for line in rawTicket[administrativeStartLine:]:
        kvMatch = re.match("^(?P<key>.+?):\s+(?P<value>.*)$", line)
        if kvMatch:
            ticketDictionary[kvMatch.group("key").lower()] = kvMatch.group("value")

    return ticketDictionary

def formatTicket(number, formatString):
    ticketDictionary = parseTicket(number)
     
    if ticketDictionary:
        return formatString % ticketDictionary 
    else:
        return "No ticket found"

    #return (bodyStartLine, administrativeStartLine)
    #return bodyStartLine

#for i in range(1,172155):
#    print i, parseTicket(i)
