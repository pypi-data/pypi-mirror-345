import pytest
from src.handy import AsciiString

class TestAsciiString:
    def test_initialization(self):
        assert AsciiString('Chrístensen') == 'Christensen'
        assert AsciiString('Chríste▀nsen') == 'Christe▀nsen'
        assert AsciiString('Maxine') == 'Maxine'
        assert AsciiString('Petrosíño') == 'Petrosino'
        assert AsciiString('Spéncer') == 'Spencer'
        assert AsciiString('Ábhinav') == 'Abhinav'
        assert AsciiString('Ñavülurí') == 'Navuluri'

    def test_isascii(self):
        assert AsciiString('Ábhinav').isascii()
        assert not AsciiString('Chríste▀nsen').isascii()
