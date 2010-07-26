#Copyright ReportLab Europe Ltd. 2000-2008
#see license.txt for license details
"""Tests for the Platypus TableOfContents class.

Currently there is only one such test. Most such tests, like this
one, will be generating a PDF document that needs to be eye-balled
in order to find out if it is 'correct'.
"""
__version__='''$Id: test_platypus_toc.py 3373 2009-01-16 11:51:39Z jonas $'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys, os
from os.path import join, basename, splitext
from math import sqrt
import unittest
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate
from reportlab.platypus import tableofcontents
from reportlab.lib import randomtext


def myMainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."

    canvas.saveState()

    canvas.rect(2.5*cm, 2.5*cm, 15*cm, 25*cm)
    canvas.setFont('Times-Roman', 12)
    pageNumber = canvas.getPageNumber()
    canvas.drawString(10*cm, cm, str(pageNumber))

    canvas.restoreState()


class MyDocTemplate(BaseDocTemplate):
    "The document template used for all PDF documents."

    _invalidInitArgs = ('pageTemplates',)

    def __init__(self, filename, **kw):
        frame1 = Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')
        self.allowSplitting = 0
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        template = PageTemplate('normal', [frame1], myMainPageFrame)
        self.addPageTemplates(template)


    def afterFlowable(self, flowable):
        "Registers TOC entries."

        if flowable.__class__.__name__ == 'Paragraph':
            styleName = flowable.style.name
            if styleName[:7] == 'Heading':
                key = str(hash(flowable))
                self.canv.bookmarkPage(key)

                # Register TOC entries.
                level = int(styleName[7:])
                text = flowable.getPlainText()
                pageNum = self.page
                # Try calling this with and without a key to test both
                # Entries of every second level will have links, others won't
                if level % 2 == 1:
                    self.notify('TOCEntry', (level, text, pageNum, key))
                else:
                    self.notify('TOCEntry', (level, text, pageNum))


def makeHeaderStyle(level, fontName='Times-Roman'):
    "Make a header style for different levels."

    assert level >= 0, "Level must be >= 0."

    PS = ParagraphStyle
    size = 24.0 / sqrt(1+level)
    style = PS(name = 'Heading' + str(level),
               fontName = fontName,
               fontSize = size,
               leading = size*1.2,
               spaceBefore = size/4.0,
               spaceAfter = size/8.0)

    return style


def makeBodyStyle():
    "Body text style - the default will do"
    return ParagraphStyle('body')


def makeTocHeaderStyle(level, delta, epsilon, fontName='Times-Roman'):
    "Make a header style for different levels."

    assert level >= 0, "Level must be >= 0."

    PS = ParagraphStyle
    size = 12
    style = PS(name = 'Heading' + str(level),
               fontName = fontName,
               fontSize = size,
               leading = size*1.2,
               spaceBefore = size/4.0,
               spaceAfter = size/8.0,
               firstLineIndent = -epsilon,
               leftIndent = level*delta + epsilon)

    return style


class TocTestCase(unittest.TestCase):
    "Test TableOfContents class (eyeball-test)."

    def test0(self):
        """Test story with TOC and a cascaded header hierarchy.

        The story should contain exactly one table of contents that is
        immediatly followed by a list of of cascaded levels of header
        lines, each nested one level deeper than the previous one.

        Features to be visually confirmed by a human being are:

            1. TOC lines are indented in multiples of 1 cm.
            2. Wrapped TOC lines continue with additional 0.5 cm indentation.
            3. Only entries of every second level has links
            ...
        """

        maxLevels = 12

        # Create styles to be used for document headers
        # on differnet levels.
        headerLevelStyles = []
        for i in range(maxLevels):
            headerLevelStyles.append(makeHeaderStyle(i))

        # Create styles to be used for TOC entry lines
        # for headers on differnet levels.
        tocLevelStyles = []
        d, e = tableofcontents.delta, tableofcontents.epsilon
        for i in range(maxLevels):
            tocLevelStyles.append(makeTocHeaderStyle(i, d, e))

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']

        description = '<font color=red>%s</font>' % self.test0.__doc__
        story.append(XPreformatted(description, bt))

        toc = tableofcontents.TableOfContents()
        toc.levelStyles = tocLevelStyles
        story.append(toc)

        for i in range(maxLevels):
            story.append(Paragraph('HEADER, LEVEL %d' % i,
                                   headerLevelStyles[i]))
            #now put some body stuff in.
            txt = randomtext.randomText(randomtext.PYTHON, 5)
            para = Paragraph(txt, makeBodyStyle())
            story.append(para)

        path = outputfile('test_platypus_toc.pdf')
        doc = MyDocTemplate(path)
        doc.multiBuild(story)


def makeSuite():
    return makeSuiteForClasses(TocTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
