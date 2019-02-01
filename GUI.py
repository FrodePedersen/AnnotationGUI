import string
import decimal
import math
import tkinter as tk
from tkinter.font import Font


class GUI():

    def __init__(self, GUIsize, textFieldSize):
        #Measured in pixels
        self.GUIheight = GUIsize[0]
        self.GUIwidth = GUIsize[1]

        #Measured in chars
        self.textFieldHeight = textFieldSize[0]
        self.textFieldWidth = textFieldSize[1]

        self.root = tk.Tk()
        self.root.geometry(f'{self.GUIheight}x{self.GUIwidth}')
        self.root.title('Annotation Tool')


        self.textFontFamily = 'Helvetica'
        self.textFieldFontSize = 14
        self.annotateFontColor = '#00FFFF'
        self.annotate_font = Font(family=self.textFontFamily, size=self.textFieldFontSize, weight='bold')

        self.textField = tk.Text(self.root, height = textFieldSize[0], width = textFieldSize[1], font=(self.textFontFamily, self.textFieldFontSize))

        self.textField.tag_configure("ANNOTATE_SENSITIVE", font=self.annotate_font, background=self.annotateFontColor)

        self.annotationButton = tk.Button(self.root, text="Sensitive", command = self.annotateButtonAction)
        self.textField.pack()
        self.annotationButton.pack()


    def startGUI(self):
        self.root.mainloop()

    def setup(self):
        self.textField.insert(tk.INSERT, "Line 1 sdkljhsadfjkl asdjkhsaduiiuweqruiohasdfkn nm"
                                         "asdfnasdnfb,anasdfjklasdklfjsadkjfjklasdfkljasdjkfhasjkldfj"
                                         "kladsk uioasdiuajk iopsadfjasdklf\n")
        self.textField.insert(tk.INSERT, "Line 2 asdajkhasd kjhsdf uyajk, kjlasdfkjh, kshadf.\n")
        self.textField.insert(tk.INSERT, "Line 3 asdafdjkldf +909kjsdf kljsdfjh, sdfkshadf.\n")

        self.textField.config(state='disabled')

    def annotateButtonAction(self):
       # print(f'{self.textField.get(tk.SEL_FIRST, tk.SEL_LAST)}')
        #print(f'First: {self.textField.index(tk.SEL_FIRST)}, Last: {self.textField.index(tk.SEL_LAST)}')

        indexStart, indexEnd = self.findSelection()
        print(f'startcol - endcol {indexStart} - {indexEnd}')
        # tk.TclError exception is raised if not text is selected
        try:
            self.textField.tag_add('ANNOTATE_SENSITIVE', indexStart, indexEnd)
        except tk.TclError:
            print(f'No text selected')

    #Ugly as Tkinter uses floats as indexing, e.g. third char in line 2 would be 2.3, while 24'th char would be 2.24
    def findSelection(self):
        selStartCol = self.indexToColumn(self.textField.index(tk.SEL_FIRST))
        selEndCol = self.indexToColumn(self.textField.index(tk.SEL_LAST))

        '''
        for i in range(selStartColumnCorrected, 0, -1):
            char = self.columnToIndex(lineNumber, selStartColumnCorrected, lineEndDigitAmount)
        # s = 0
        #e = lineEnd - lineStart
        '''

        # print(f'lineStart {lineStart}, lineEnd {lineEnd}')
        '''
        #Find first char of selected words
        for i in range(indexStart-1,0,-1):
            char = self.textField.get(i,i)
            if not (( char in string.punctuation ) or ( char in string.whitespace )):
                s += 1
            else:
                break

        #Find last char of selected words
        for i in range(indexEnd+1, lineEnd):
            char = self.textField.get(i,i)
            if not (( char in string.punctuation ) or ( char in string.whitespace )):
                e += 1
            else:
                break

        '''

        return selStartCol, selEndCol

    def columnToIndex(self, lineNumber, correctedCol, lineDigits):
        index = 0.0

        return index

    def indexToColumn(self, selIndex):

        selIndex = decimal.Decimal(selIndex)

        # calculate line start:
        lineNumber = math.floor(decimal.Decimal(self.textField.index(f'{selIndex} linestart')))

        # calculate line end:
        lineEndIndex = decimal.Decimal(self.textField.index(f'{selIndex} lineend'))
        lineEndDigitAmount = abs(decimal.Decimal(lineEndIndex).as_tuple().exponent)
        #lineEndCeiling = round((lineEndIndex - lineNumber) * (10 ** lineEndDigitAmount))

        # calculate selStartIndexCorrected
        selIndexDigitAmount = abs(decimal.Decimal(selIndex - lineNumber).as_tuple().exponent)
        IndexDigitDifference = abs(lineEndDigitAmount - selIndexDigitAmount)
        selColumn = selIndex - lineNumber  # Uncorrected column but without the row
        selIndexCorrected = round(selColumn * decimal.Decimal(10 ** - IndexDigitDifference), lineEndDigitAmount)

        selColumnCorrected = round(selIndexCorrected * 10 ** lineEndDigitAmount)

        return selColumnCorrected
