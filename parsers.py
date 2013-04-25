#!/usr/bin/env python

OK = 'ok'
CAUGHT = 'caught'
UNKNOWN = 'unknown'
FI_MSG = 'Fault Injected!!!'

class UnittestParser:

    def __init__(self):
        self.tests = {}
        self.failed = []
        self.maybecaught = []
        self.errors = {}
        self.counts = {OK:0, CAUGHT:0, UNKNOWN:0}

    def process(self, text):
        '''Process the output of the unit tests'''
        lines = text.split('\n')
        if not len(lines):
            return
        while len(lines) and not lines[0].startswith('test_'):
            lines.pop(0)
        while len(lines) and lines[0].startswith('test_'):
            name, status, body = self.test_line(lines)
            self.tests[name] = status, body
            self.counts[status] += 1
            if status == CAUGHT:
                self.maybecaught.append(name)
            if status != OK:
                self.failed.append(name)
        if len(lines):
            lines.pop(0)
            errors = []
            while lines and lines[0].strip() == '='*len(lines[0].strip()):
                name, body, is_ours = self.error_msg(lines)
                self.errors[name] = body, is_ours
        self.check_caught()

    def check_caught(self):
        '''Check the tests labelled "ERROR" to see if they were reporting our
        injected error'''
        for name in self.maybecaught:
            if not (name in self.errors and self.errors[name][1]):
                self.counts[CAUGHT] -= 1
                self.counts[UNKNOWN] += 1
                self.tests[name] = UNKNOWN, self.tests[name][1]

    def error_msg(self, lines):
        lines.pop(0)
        parts = lines.pop(0).split()
        name = parts[1]
        body = []
        while lines[0].strip():
            body.append(lines.pop(0))
        lines.pop(0)
        body = '\n'.join(body).strip()
        is_ours = parts[0] == 'ERROR:' and body.endswith('Exception: %s' % FI_MSG)
        return name, body, is_ours

    def test_line(self, lines):
        parts = lines.pop(0).split()
        name = parts[0]
        txt = ' '.join(parts[1:])
        if '...' not in txt:
            while '...' not in lines[0]:
                txt += '\n' + lines.pop(0)
            txt += '\n' + lines.pop(0)
        if txt.endswith('ok'):
            status = OK
        elif txt.endswith('ERROR'):
            status = CAUGHT
        else:
            status = UNKNOWN
        return (name, status, txt)

# vim: et sw=4 sts=4
