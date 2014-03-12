#!/usr/bin/python
import sys
import pexpect

filename = sys.argv[1]
with open(filename) as fp:
    child = pexpect.spawn ('neo4j-shell -v -host localhost -port 1151')
    #child.logfile = open("mylog", "w")
    child.expect('.*neo4j-sh.*?')
    child.sendline('help')
    for line in fp:
        child.expect('.*neo4j-sh.*?')
        #print line
        child.sendline(line)

#child.interact()
exit()


