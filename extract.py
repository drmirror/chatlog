#!/usr/bin/python

from HTMLParser import HTMLParser
from dateutil.parser import parse
import re, htmlentitydefs

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

class MessageParser(HTMLParser):
    mode = "user"
    user = ""
    ts = ""
    msg = ""
    def handle_starttag(self, tag, attrs):
        if tag == "span":
            if attrs[0][1] == "user":
                self.mode = "user"
            elif attrs[0][1] == "meta":
                self.mode = "ts"
            else:
                self.mode = ""
        if tag == "p":
            self.mode = "msg"
            self.msg = ""
    def handle_endtag(self, tag):
        if tag == "p":
            print self.ts, self.user, self.msg
    def handle_data(self, data):
        if self.mode == "user":
            self.user = data
        elif self.mode == "ts":
            self.ts = parse(data)
        elif self.mode == "msg":
            self.msg += data
    def handle_entityref(self, name):
        if self.mode == "msg":
            ch = "&" + name + ";"
            self.msg += unescape(ch).encode('utf8')
    def handle_charref(self, name):
        if self.mode == "msg":
            ch = "&#" + name + ";"
            self.msg += unescape(ch).encode('utf8')
            
parser = MessageParser()
with open("messages.htm", "r") as ifile:
    while True:
        line = ifile.readline();
        if line == '':
            break
        parser.feed(line)
