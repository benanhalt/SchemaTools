import re

relationship_re = re.compile(r"(?P<action>[nrf])\s+" +
                             r"(?P<ltable>[^\.]+)\." +
                             r"(?P<lcol>[^\s]+)\s+->\s+" +
                             r"(?P<rtable>[^\.]+)\." +
                             r"(?P<rcol>[^\s]+)")

def parse_relationships(data):
    results = set()
    for line in data:
        match = relationship_re.match(line)
        assert match is not None
        action = match.group("action")
        rtable = match.group("rtable")
        ltable = match.group("ltable")

        if action == "r":
            results.add((rtable, ltable))
        elif action == "f":
            results.add((ltable, rtable))
    return results

if __name__ == '__main__':
    import sys
    print "digraph G {"
    for l, r in parse_relationships(sys.stdin):
        print "  %s -> %s;" % (l, r)
    print "}"


