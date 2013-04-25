#!/usr/bin/env python
'''
This does stressting
'''

import re
import os
import sys
import subprocess

import parsers

FN_X = re.compile(r'^\s*def ([\w_]+)', re.M)

FI_MSG = 'Fault Injected!!!'

class FaultTester:
    def __init__(self, project_dir, exclude=[], cmd='python setup.py test',
                       parser=parsers.UnittestParser):
        self.project_dir = project_dir
        self.exclude = exclude
        self.cmd = cmd + '; exit 0'
        self.parser = parser
        self.dependson = {}

    def get_files(self, base=None):
        '''Collect python files to modify'''
        for root, dirs, files in os.walk(self.project_dir):
            for name in files:
                full = os.path.join(root, name)
                if full in self.exclude:
                    continue
                if name.endswith('.py'):
                    yield full
            for dr in list(dirs):
                full = os.path.join(root, dr)
                if full in self.exclude:
                    dirs.remove(dr)

    def run(self):
        '''Run the injection testing!'''
        outfile = open(os.path.join(self.project_dir, 'stress.log'), 'w')
        files = list(self.get_files())
        self.out('Collected %s files' % len(files))
        self.run_initial()
        outfile.write('Tests Found:\n')
        for name in self.all_tests:
            outfile.write('  %s\n' % name)
        outfile.write('\n')
        outfile.flush()
        numfiles = len(files)
        for i, fn in enumerate(files):
            outfile.write('File: %s (%d of %d)\n' % (fn, i+1, numfiles))
            self.process_file(fn, outfile)
            outfile.flush()
        outfile.close()

    def run_initial(self):
        self.out('Running the test suite initially')
        text = subprocess.check_output(self.cmd, stderr=subprocess.STDOUT, shell=True)
        ps = self.parser()
        ps.process(text)
        if ps.failed or not len(ps.tests.keys()):
            print text
            raise Exception('Test suite doesn\'t pass on clear project. Aborting')
        self.all_tests = ps.tests.keys()
        self.out('Found %d tests' % len(self.all_tests))

    def run_suite(self):
        text = subprocess.check_output(self.cmd, stderr=subprocess.STDOUT, shell=True)
        ps = self.parser()
        ps.process(text)
        if not len(ps.tests.keys()):
            print 'Traceback:: (no tests run)', text
        self.out('ran', len(ps.failed), len(ps.tests.keys()), len(ps.errors.keys()))
        return ps

    def out(self, *args):
        print ' '.join(repr(x) for x in args)

    def process_file(self, fname, outfile):
        text = open(fname).read()
        open(fname + '.orig', 'w').write(text)
        defns = list(FN_X.finditer(text))
        lines = text.split('\n')
        self.out('Found %d function definitions in file %s' % (len(defns), fname))
        for defn in defns:
            name = defn.groups()[0]
            newtext = self.inject(text, lines[:], name, defn.end())
            open(fname, 'w').write(newtext)
            print 'injected fault into', name, fname,
            outfile.write('  %s:%d ' % (name, defn.start()))
            ps = self.run_suite()
            outfile.write(':%d:%d:%d\n' % (len(ps.failed), len(ps.tests.keys()), len(ps.errors.keys())))
            for tname in ps.failed:
                outfile.write('    %s\n' % tname)
            outfile.write('\n')
            self.dependson[(name, defn.span(), fname)] = ps.failed
        outfile.write('\n')
        # restore original
        open(fname, 'w').write(text)
        os.remove(fname + '.orig')

    def inject(self, text, lines, name, pos):
        '''Inject the "raise Ex:" into the text'''
        lno = text[:pos].count('\n')
        defline = lines[lno]
        white = re.findall('^\s*', defline)[0]
        lines.insert(lno+1, white + '    raise Exception("%s")' % FI_MSG)
        return '\n'.join(lines)

    def stats(self):
        tst = dict((name, []) for name in self.all_tests)
        for key, failed in self.dependson.iteritems():
            for tname in failed:
                tst[tname].append(key)
        for tname, defs in tst.iteritems():
            self.out(len(defs), tname)

"""
def alter_text(text, at=0):
    new = FN_X.finditer(text)
    lines = text.split('\n')
    [new.next() for x in range(at)]
    mt = new.next()
    lno = text[:mt.end()].count('\n')
    name = mt.groups()[0]
    theline = lines[lno]
    white = re.findall('^\s*', theline)[0]
    lines.insert(lno+1, white + '    raise Exception("%s")' % FI_MSG)
    return name, mt.span(), '\n'.join(lines)

def run_suite(cmd):
    '''Run the test suite (setup.py test) and inspect the output'''
    text = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    return process_suite_output(text)
"""

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: stressme.py directory'
        sys.exit(2)
    stresser = FaultTester(sys.argv[1], exclude=['flask/testsuite'])
    stresser.run()
    stresser.stats()


# vim: et sw=4 sts=4
