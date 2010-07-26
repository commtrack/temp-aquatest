#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
"""Tests for utility functions in reportlab.pdfbase.pdfutils.
"""
__version__='''$Id: test_pdfbase_pdfutils.py 3288 2008-09-15 11:03:17Z rgbecker $'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, printLocation
setOutDir(__name__)
import os
import unittest
from reportlab.pdfbase.pdfutils import _AsciiHexEncode, _AsciiHexDecode
from reportlab.pdfbase.pdfutils import _AsciiBase85Encode, _AsciiBase85Decode

class PdfEncodingTestCase(unittest.TestCase):
    "Test various encodings used in PDF files."

    def testAsciiHex(self):
        "Test if the obvious test for whether ASCII-Hex encoding works."

        plainText = 'What is the average velocity of a sparrow?'
        encoded = _AsciiHexEncode(plainText)
        decoded = _AsciiHexDecode(encoded)

        msg = "Round-trip AsciiHex encoding failed."
        assert decoded == plainText, msg


    def testAsciiBase85(self):
        "Test if the obvious test for whether ASCII-Base85 encoding works."

        msg = "Round-trip AsciiBase85 encoding failed."
        plain = 'What is the average velocity of a sparrow?'

        #the remainder block can be absent or from 1 to 4 bytes
        for i in xrange(55):
            encoded = _AsciiBase85Encode(plain)
            decoded = _AsciiBase85Decode(encoded)
            assert decoded == plain, msg
            plain = plain + chr(i)


def makeSuite():
    return makeSuiteForClasses(PdfEncodingTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
