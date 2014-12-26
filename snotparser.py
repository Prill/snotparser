#!/usr/bin/env python

import subprocess
import string
import re

from string import Template

ADMINISTRATIVE_START_MARKER = "XXXXXXXXXXXXXXXXXX  Administrative Information Follows  XXXXXXXXXXXXXXXXXXXXXX"
TICKET_ERROR_MARKER = "::::::::::::::"


def parseTicket(number, command='snot'):
    process = subprocess.Popen([command, '-sr', str(number)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

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
    # Usually the second line, which contains both the date and a from address, which may or
    # may not be different from the "From:" line

    for line in rawTicket[0:bodyStartLine]:
        match = re.match(r"^From\s*(?P<summary_line>.+)$", line)
        if match:
            summary_email = re.search(r"(?P<email>\S*@\S*)", match.group("summary_line"))
            if summary_email:
                ticketDictionary["summary_email"] = summary_email.group("email")
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
            ticketDictionary[kvMatch.group("key").lower().replace(" ", "_")] = kvMatch.group("value")
    # if "assigned to" not in ticketDictionary:
    #     ticketDictionary["assigned_to"] = "unassigned"
    ticketDictionary['number'] = number
    if ticketDictionary['priority'].startswith('+'):
        ticketDictionary['status'] = 'completed'
    elif ticketDictionary.get('closed_by') is not None:
        ticketDictionary['status'] = 'completed'
    else:
        ticketDictionary['status'] = 'open'

    return ticketDictionary


def formatTicket(number, formatString, command='snot'):
    ticketDictionary = parseTicket(number, command)

    if ticketDictionary:
        return Template(formatString).safe_substitute(ticketDictionary)
    else:
        return str(number) + ": No ticket found"


# Formats a ticket dict using the newer formatting system
def formatTicketDictSmart(ticketDict, formatString):
    # formatString will be in the form of "assigned_to,from_line,subject" csv
    if not ticketDict:
        return "No such ticket"

    formatKeys = formatString.split(',')
    formattedItems = []
    for key in formatKeys:
        key = key.strip()
        if key == "from":
            from_line = ticketDict["from_line"]
            emailRegex = '\s?(?P<email>(?P<username>\S+?)@(?P<domain>\S+?))\s?'
            m = re.match(r"^%s(\s.*)?$" % emailRegex, from_line) or re.match(r'^\s*?"?(?P<name>.+?)"? \<%s\>' % emailRegex, from_line)
            if m:
                md = m.groupdict()
                emailFormatted = md["email"]
                if re.match("(cat|cecs|ece|ee|cs|etm|me|mme|cee|ce)\.pdx\.edu", md["domain"]):
                    emailFormatted = md["username"]

                itemText = ""
                if "name" in md:
                    formattedItems.append("%s (%s)" % (md["name"], emailFormatted))
                else:
                    formattedItems.append(emailFormatted)
            else:
                formattedItems.append("ERROR (yell at Wren)")
        elif key == "url":
            formattedItems.append("https://cat.pdx.edu/~snot/snot.cgi?command=View&ticket=%s" % ticketDict["number"])
        else:
            if key in ticketDict and ticketDict[key].strip():
                value = ticketDict[key].strip()
                if key == "assigned_to":
                    assignmentMatch = re.match(r"(?P<username>[^@]+)@?(?P<domain>\S*)", value)
                    if (assignmentMatch):
                        formattedItems.append(assignmentMatch.groupdict()["username"])
                else:
                    formattedItems.append(ticketDict[key])
    return string.join(formattedItems, " | ")
    #return (bodyStartLine, administrativeStartLine)
    #return bodyStartLine


def formatTicketSmart(number, formatString, command='snot'):
    ticketDictionary = parseTicket(number, command)

    if ticketDictionary:
        return formatTicketDictSmart(ticketDictionary, formatString)
    else:
        return str(number) + ": No ticket found"


def getTicketHistory(number):
    try:
        number = int(number)
        process = subprocess.Popen(['grep', "TKT: %d" % number, "/u/snot/logs/log"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return process.stdout.readlines()
    except ValueError as e:
        return str(e)


if __name__ == "__main__":
    import sys
    import os
    snot_cmd = os.environ.get('SNOT_CMD', 'snot')
    ticket_num = sys.argv[1]
    print ticket_num, parseTicket(ticket_num, snot_cmd)
