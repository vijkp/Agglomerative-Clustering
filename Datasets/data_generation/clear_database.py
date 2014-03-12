#!/usr/bin/python
import sys
import pexpect

child = pexpect.spawn ('neo4j-shell -v -host localhost -port 1151')
#child.logfile = open("mylog", "w")
child.expect('.*neo4j-sh.*?')
child.sendline('MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r;')
print "Database cleared!\n"
exit()


