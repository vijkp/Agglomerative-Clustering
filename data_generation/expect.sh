#!/usr/bin/expect

set timeout 10
set f [open "outputfile.txt"]
set lines [split [read $f] "\n"]
close $f

spawn "/Users/vijaykp/neo4j/bin/neo4j-shell"
expect "neo4j-sh (?)$ " {send "help;\r"}

#expect "neo4j-sh (?)$ " {send "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r; \r"}

foreach line $lines {
    expect "neo4j-sh (?)$ " {send "$line\r"}
}

interact

