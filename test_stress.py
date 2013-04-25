#!/usr/bin/env python

import stressme
FI_MSG = stressme.FI_MSG

f = '''
print "hi"

def ho():
    man = 4

ho()

def he():
    moo = 3

    def men():
        right += 2

'''

simple = ('''def ho():
    print "hi"
''', '''def ho():
    raise Exception("%s")
    print "hi"
''' % FI_MSG)

def test_1():
    assert stressme.alter_text(simple[0]) == simple[1]

two = ('''def ho():
    print 'hi'

def hum():
    return 4
''', '''def ho():
    print 'hi'

def hum():
    raise Exception("%s")
    return 4
''' % FI_MSG)
def test_2():
    assert stressme.alter_text(two[0], 1) == two[1]

ind = ('''class man:
    def moo():
        print "hi"
''', '''class man:
    def moo():
        raise Exception("%s")
        print "hi"
''' % FI_MSG)
def test_indent():
    assert stressme.alter_text(ind[0]) == ind[1]

erl = '''======================================================================
ERROR: test_template_test_with_template (flask.testsuite.templating.TemplatingTestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/jared/clone/flask/flask/testsuite/templating.py", line 217, in test_template_test_with_template
    @app.template_test()
  File "/home/jared/clone/flask/flask/app.py", line 1151, in decorator
    self.add_template_test(f, name=name)
  File "/home/jared/clone/flask/flask/app.py", line 63, in wrapper_func
    return f(self, *args, **kwargs)
  File "/home/jared/clone/flask/flask/app.py", line 1165, in add_template_test
    raise Exception("Fault Injected!!!")
Exception: %s
''' % FI_MSG

def test_get_error_line():
    res = stressme.get_error_line(erl.split('\n'))
    assert res[0] == 'test_template_test_with_template'
    assert res[2]

erl_notours = '''======================================================================
ERROR: test_template_test_with_template (flask.testsuite.templating.TemplatingTestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/jared/clone/flask/flask/testsuite/templating.py", line 217, in test_template_test_with_template
    @app.template_test()
  File "/home/jared/clone/flask/flask/app.py", line 1151, in decorator
    self.add_template_test(f, name=name)
  File "/home/jared/clone/flask/flask/app.py", line 63, in wrapper_func
    return f(self, *args, **kwargs)
  File "/home/jared/clone/flask/flask/app.py", line 1165, in add_template_test
    raise Exception("Stuff")
Exception: Stuff
'''

def test_get_error_notours():
    res = stressme.get_error_line(erl_notours.split('\n'))
    assert res[0] == 'test_template_test_with_template'
    assert not res[2]



# vim: et sw=4 sts=4
