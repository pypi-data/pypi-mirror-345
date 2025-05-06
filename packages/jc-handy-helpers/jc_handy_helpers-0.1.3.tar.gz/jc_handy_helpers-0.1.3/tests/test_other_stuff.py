import pytest,doctest
from src import handy
from src.handy import first_match, compile_filename_patterns
from src.handy import non_negative_int, positive_int
from src.handy import shellify
from src.handy import ProgInfo,prog

class Test_file_pattern_stuff:
    def test_file_pattern_stuff(self):
        pats=[
            '2019-*',
            're:^abc[0-9]{4}.dat$',
            'X*.txt',
            '*.txt',
            're:^.*\\.doc$'
        ]
        pats=compile_filename_patterns(pats)
        p,m=first_match('abc1980.dat',pats)
        assert p.pattern == '^abc[0-9]{4}.dat$'
        assert  m.group() == 'abc1980.dat'
        p,m=first_match('X-ray.txt',pats)
        assert p.pattern == '(?s:X.*\\.txt)\\Z'
        assert m.group() == 'X-ray.txt'
        p,m=first_match('Y-ray.txt',pats)
        assert p.pattern == '(?s:.*\\.txt)\\Z'
        assert m.group() == 'Y-ray.txt'
        p,m=first_match('2019-10-26.dat',pats)
        assert p.pattern == '(?s:2019\\-.*)\\Z'
        assert m.group() == '2019-10-26.dat'
        p,m=first_match('somefile.txt',pats)
        assert p.pattern == '(?s:.*\\.txt)\\Z'
        assert m.group() == 'somefile.txt'
        p,m=first_match('somefile.doc',pats)
        assert p.pattern == '^.*\\.doc$'
        assert m.group() == 'somefile.doc'
        p,m=first_match('badfile.xyz',pats)
        assert p is None
        assert m is None

class Test_Integer_Parsers:
    def exception_testing_for_non_negative_int(self,s):
        with pytest.raises(ValueError) as ei:
            n=non_negative_int(s)
            assert False, f"Failed to raise ValueError for {s!r}."
        assert str(ei.value) == f"{s!r} is not a non-negative integer."

    def exception_testing_for_positive_int(self,s):
        with pytest.raises(ValueError) as ei:
            n=positive_int(s)
            assert False, f"Failed to raise ValueError for {s!r}."
        assert str(ei.value) == f"{s!r} is not a positive integer."

    def test_non_negative_int(self):
        assert non_negative_int('10') == 10
        assert non_negative_int(' 10 ') == 10
        assert non_negative_int(' \t\r 10 \r\t ') == 10
        assert non_negative_int('1') == 1
        assert non_negative_int('0') == 0
        self.exception_testing_for_non_negative_int('-1')
        self.exception_testing_for_non_negative_int(' -1 ')
        self.exception_testing_for_non_negative_int('   -10   ')
        self.exception_testing_for_non_negative_int(' \t\r  -10 \r\t ')

    def test_positive_int(self):
        assert positive_int('10') == 10
        assert positive_int(' 10 ') == 10
        assert positive_int(' \t\r 10 \r\t ') == 10
        assert positive_int('1') == 1
        self.exception_testing_for_positive_int('0')
        self.exception_testing_for_positive_int('-1')
        self.exception_testing_for_positive_int(' -1 ')
        self.exception_testing_for_positive_int('   -10   ')
        self.exception_testing_for_positive_int(' \t\r  -10 \r\t ')

class Test_shellify:
    def test_shellify(self):
        assert shellify(None) == "''"
        assert shellify(123) == '123'
        assert shellify(123.456) == '123.456'
        #assert shellify("This 'is' a test of a (messy) string.") == 'This '"'"'is'"'"' a test of a (messy) string.'
        assert shellify("This 'is' a test of a (messy) string.") == "'This '\"'\"'is'\"'\"' a test of a (messy) string.'"
        assert shellify('This "is" another messy test.') == "'This \"is\" another messy test.'"

class Test_ProgInfo:
    def test_ProgInfo(self):
        ###
        ### Run `pytest -s` to see the output printed below.
        ###
        print("\n------------------------------")
        print(f"{prog.name=}")
        print(f"{prog.pid=}")
        print(f"{prog.dir=}")
        print(f"{prog.real_name=}")
        print(f"{prog.real_dir=}")
        print(f"{prog.tempdir=}")
        print(f"{prog.temp=}")
        print("------------------------------")

class Test_docstring_tests:
    def test_docstrings(self):
        ###
        ### Run any docstring tests in the "handy" package.
        ###
       result=doctest.testmod(handy)
       assert result.failed==0
