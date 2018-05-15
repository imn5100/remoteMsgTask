# -*- coding=utf-8 -*-
import re

CMD_CONNECT = 'CONNECT'
CMD_DISCONNECT = 'DISCONNECT'
CMD_SEND = 'SEND'
CMD_SUBSCRIBE = 'SUBSCRIBE'
CMD_UNSUBSCRIBE = 'UNSUBSCRIBE'

LINE_END_RE = re.compile('\n|\r\n')
PREAMBLE_END_RE = re.compile(b'\n\n|\r\n\r\n')
HEADER_LINE_RE = re.compile('(?P<key>[^:]+)[:](?P<value>.*)')
_HEADER_ESCAPES = {
    '\r': '\\r',
    '\n': '\\n',
    ':': '\\c',
    '\\': '\\\\',
}
_HEADER_UNESCAPES = dict((value, key) for (key, value) in _HEADER_ESCAPES.items())


class Frame(object):
    """
    A STOMP frame (or message).

    :param str cmd: the protocol command
    :param dict headers: a map of headers for the frame
    :param body: the content of the frame.
    """

    def __init__(self, cmd=None, headers=None, body=None):
        self.cmd = cmd
        self.headers = headers if headers is not None else {}
        self.body = body

    def __str__(self):
        return '{cmd=%s,headers=[%s],body=%s}' % (self.cmd, self.headers, self.body)

    def convert_to_data(self):
        lines = []
        if self.cmd:
            lines.append(self.cmd)
            lines.append("\n")
        for key, vals in sorted(self.headers.items()):
            if vals is None:
                continue
            if type(vals) != tuple:
                vals = (vals,)
            for val in vals:
                lines.append("%s:%s\n" % (key, val))
        lines.append("\n")
        if self.body:
            lines.append(self.body)

        if self.cmd:
            lines.append('\x00')

        return [''.join(p for p in lines)]

    @staticmethod
    def read_message_to_frame(frame):
        f = Frame()
        if frame == b'\x0a' or frame == 'h':
            f.cmd = 'heartbeat'
            return f
        mat = PREAMBLE_END_RE.search(frame)
        if mat:
            preamble_end = mat.start()
            body_start = mat.end()
        else:
            preamble_end = len(frame)
            body_start = preamble_end
        preamble = frame[0:preamble_end]
        preamble_lines = LINE_END_RE.split(preamble)
        preamble_len = len(preamble_lines)
        f.body = frame[body_start:]

        # Skip any leading newlines
        first_line = 0
        while first_line < preamble_len and len(preamble_lines[first_line]) == 0:
            first_line += 1

        if first_line >= preamble_len:
            return None

        # Extract frame type/command
        f.cmd = preamble_lines[first_line]

        # Put headers into a key/value map
        f.headers = parse_headers(preamble_lines, first_line + 1)

        return f


def parse_headers(lines, offset=0):
    headers = {}
    for header_line in lines[offset:]:
        header_match = HEADER_LINE_RE.match(header_line)
        if header_match:
            key = header_match.group('key')
            key = re.sub(r'\\.', _unescape_header, key)
            if key not in headers:
                value = header_match.group('value')
                value = re.sub(r'\\.', _unescape_header, value)
                headers[key] = value
    return headers


def _unescape_header(matchobj):
    escaped = matchobj.group(0)
    unescaped = _HEADER_UNESCAPES.get(escaped)
    if not unescaped:
        unescaped = escaped
    return unescaped
