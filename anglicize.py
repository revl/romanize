#!/usr/bin/env python

"""Perform anglicization of text in UTF-8 encoding.

The script works as a filter: it reads UTF-8 characters from its
standard input and writes the result to its standard output.

Alternatively, it can be used as a Python module:

    from anglicize import Anglicize
    anglicize = Anglicize()
    print anglicize.anglicize(utf8_bytes)

See README.md for more details."""

import xlat_tree

class Anglicize(object):
    """Convert a byte sequence of UTF-8 characters to their English
    transcriptions."""

    def __init__(self):
        self.__state = xlat_tree.xlat_tree
        self.__finite = ''
        self.__buf = ''

    def anglicize(self, text):
        """Process a whole string and return its anglicized version."""
        return self.process_buf(text) + self.finalize()

    def process_buf(self, buf):
        """Anglicize a buffer. Expect more to come. Keep state between calls."""
        output = ''
        for byte in buf:
            output += self.push_byte(byte)
        return output

    def push_byte(self, byte):
        """Input another byte. Return the transliteration when it's ready."""
        # Check if there is no transition from the current state
        # for the given byte.
        if byte not in self.__state:
            if self.__state == xlat_tree.xlat_tree:
                # We're at the start state, which means that
                # no bytes have been accumulated in the
                # buffer and the new byte also cannot be
                # converted - return it right away
                return byte
            return self.__skip_buf_byte() + self.push_byte(byte)

        new_node = self.__state[byte]
        if not new_node[1]:
            self.__state = xlat_tree.xlat_tree
            self.__finite = ''
            self.__buf = ''
            return new_node[0] # Cannot be empty.
        self.__state = new_node[1]
        if new_node[0]:
            self.__finite = new_node[0]
            self.__buf = ''
        else:
            self.__buf += byte
        return ''

    def finalize(self):
        """Process and return the remainder of the internal buffer."""
        output = ''
        while self.__buf or self.__finite:
            output += self.__skip_buf_byte()
        return output

    def __skip_buf_byte(self):
        """Restart character recognition in the internal buffer."""
        self.__state = xlat_tree.xlat_tree
        if self.__finite:
            output = self.__finite
            self.__finite = ''
            buf = self.__buf
        else:
            output = self.__buf[0]
            buf = self.__buf[1:]
        self.__buf = ''
        for byte in buf:
            output += self.push_byte(byte)
        return output

def main():
    """Apply anglicization to the standard input stream and print the result."""

    from sys import stdin, stdout

    anglicize = Anglicize()

    while True:
        line = stdin.readline(1024)
        if not line:
            break
        stdout.write(anglicize.process_buf(line))

    stdout.write(anglicize.finalize())

if __name__ == "__main__":
    main()
