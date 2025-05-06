import pytest
from src.handy import CIString

alpha=CIString('alpha')
bravo=CIString('bravo')
charlie=CIString('charlie')

Alpha=CIString('Alpha')
Bravo=CIString('Bravo')
Charlie=CIString('Charlie')

class Test_CIString:
    def test_initialization(self):
        assert isinstance(alpha,str)
        assert isinstance(alpha,CIString)
        assert alpha == 'alpha'

    def test_equality_with_CaselessString(self):
        assert alpha == alpha
        assert alpha == Alpha
        assert alpha != bravo
        assert not (alpha == bravo)

    def test_equality_with_str(self):
        assert alpha == 'alpha'
        assert alpha == 'Alpha'
        assert 'alpha' == alpha
        assert 'Alpha' == alpha
        assert alpha != 'bravo'
        assert not (alpha == 'bravo')

    def test_other_comparisons(self):
        assert alpha<Bravo<charlie
        assert charlie>Bravo>alpha
        assert alpha<'Bravo'<charlie
        assert charlie>'Bravo'>alpha

    def test_repr(self):
        repr(alpha) == CIString('alpha')
        repr(Bravo) == CIString('Bravo')
        repr(charlie) == CIString('charlie')

    def test_sorting(self):
        l=[Bravo,alpha,charlie]
        assert repr(l) == "[CIString('Bravo'), CIString('alpha'), CIString('charlie')]"
        l.sort()
        assert repr(l) == "[CIString('alpha'), CIString('Bravo'), CIString('charlie')]"
        l.sort(reverse=True)
        assert repr(l) == "[CIString('charlie'), CIString('Bravo'), CIString('alpha')]"

        l=['Bravo',alpha,charlie]
        assert repr(l) == "['Bravo', CIString('alpha'), CIString('charlie')]"
        l.sort()
        assert repr(l) == "[CIString('alpha'), 'Bravo', CIString('charlie')]"
        l.sort(reverse=True)
        assert repr(l) == "[CIString('charlie'), 'Bravo', CIString('alpha')]"

    def test_str(self):
        bravo=CIString('Bravo')
        assert type(str(bravo)) == str
        assert bravo == str(bravo)
        assert str(bravo) == bravo

# Run all the same tests using the legacy name for CIString.
Test_CaselessString=Test_CIString
