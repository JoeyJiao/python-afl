# encoding=UTF-8

# Copyright © 2015 Jakub Wilk <jwilk@jwilk.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import signal

from nose.tools import assert_equal
from . import tools

import afl

def test_non_persistent():
    os.environ.pop('AFL_PERSISTENT', None)
    _test_non_persistent()
    _test_non_persistent(1)
    _test_non_persistent(max=1)
    _test_non_persistent(42)
    _test_non_persistent(max=42)

@tools.fork_isolation
def _test_non_persistent(*args, **kwargs):
    assert os.getenv('AFL_PERSISTENT') is None
    x = 0
    while afl.persistent(*args, **kwargs):
        x += 1
    assert_equal(x, 1)

def test_persistent():
    try:
        os.environ['AFL_PERSISTENT'] = '1'
        _test_persistent(None)
        _test_persistent(1, 1)
        _test_persistent(1, max=1)
        _test_persistent(42, 42)
        _test_persistent(42, max=42)
        os.environ['AFL_PERSISTENT'] = ''
        # empty string should enable persistent mode, too
        _test_persistent(None)
    finally:
        os.environ.pop('AFL_PERSISTENT', None)

@tools.fork_isolation
def _test_persistent(n, *args, **kwargs):
    assert os.getenv('AFL_PERSISTENT') is not None
    n_max = 1000
    k = [0]
    def kill(pid, sig):
        assert_equal(pid, os.getpid())
        assert_equal(sig, signal.SIGSTOP)
        k[0] += 1
    os.kill = kill
    x = 0
    while afl.persistent(*args, **kwargs):
        x += 1
        if x == n_max:
            break
    if n is None:
        assert_equal(x, n_max)
        assert_equal(k[0], n_max - 1)
    else:
        assert_equal(x, n)
        assert_equal(k[0], n)

# vim:ts=4 sts=4 sw=4 et