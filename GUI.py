import string
import decimal
import math
import tkinter as tk
import tkinter.scrolledtext
from tkinter.font import Font
from tkinter import messagebox
from tkinter import filedialog
import json


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

        self.textField = tk.scrolledtext.ScrolledText(self.root, height = textFieldSize[0], width = textFieldSize[1], font=(self.textFontFamily, self.textFieldFontSize))
        self.annotationTextField = tk.scrolledtext.ScrolledText(self.root, height=textFieldSize[0], width = textFieldSize[1], font=(self.textFontFamily, self.textFieldFontSize))

        self.textField.config(state='disabled')
        self.annotationTextField.config(state='disabled')

        self.annotationTextFieldLabel = tk.Label(self.root, text='Annotation Labels:')


        self.textField.tag_configure("ANNOTATE_SENSITIVE", font=self.annotate_font, background=self.annotateFontColor)

        buttonWidth = 15
        self.annotationButton = tk.Button(self.root, width = buttonWidth, text="Annotate Sensitive", command = self.annotateButtonAction)
        self.loadSessionButton = tk.Button(self.root, width = buttonWidth, text="Load Session", command=self.loadSessionButtonAction)                     #Todo
        self.loadDataButton = tk.Button(self.root, width = buttonWidth, text="Load Data", command=self.loadDataButtonAction)                     #Todo
        self.saveSessionButton = tk.Button(self.root, width = buttonWidth, text="Save Session", command=self.saveAnnotationButtonAction)   #Todo
        self.nextButton = tk.Button(self.root, width = buttonWidth, text="Next", command=self.nextButtonAction)                                  #Todo
        self.prevButton = tk.Button(self.root, width = buttonWidth, text="Prev", command=self.prevButtonAction)                                  #Todo

        numberOfButtons = 6
        self.annotationButton.grid(row=0, column=0, padx=10)
        self.loadSessionButton.grid(row=1, column=0)
        self.loadDataButton.grid(row=2, column=0)
        self.saveSessionButton.grid(row=3, column=0)
        self.nextButton.grid(row=4, column=0)
        self.prevButton.grid(row=5, column=0)
        self.textField.grid(row=0, column=1, rowspan=numberOfButtons)
        self.annotationTextFieldLabel.grid(row=numberOfButtons, column=0)
        self.annotationTextField.grid(row=numberOfButtons, column=1)

        self.workingStringIndex = 0

        options = []
        with open('res/Users.txt', 'r') as txt:
            for line in txt.readlines():
                options.append(line.strip())

        self.userMenuList = tk.StringVar(self.root)
        self.userMenuList.set('Frode')
        menu = tk.OptionMenu(self.root, self.userMenuList, *options)

        menu.grid(row=0, column=2)

        self.listOfAnnotations = []


    def startGUI(self):
        self.root.mainloop()

    def setup(self):
        pass


    def annotateButtonAction(self, _event=None):

        if self.userMenuList.get() == '':
            messagebox.showinfo('Invalid Action', 'Invalid User, please select a User')
            return

        # tk.TclError exception is raised if not text is selected
        try:
            indexStart, indexEnd = self.findSelection()
            annotatedText = self.textField.get(indexStart, indexEnd)
            informationDict = self.listOfAnnotations[self.workingStringIndex] #get dictionary of string currently being worked on
            if (indexStart, indexEnd) not in informationDict['annotations']:
                self.textField.tag_add('ANNOTATE_SENSITIVE', indexStart, indexEnd)
                informationDict['annotations'][f"{indexStart},{indexEnd}"] = {'label': 'sensitive',
                                                                          'annotatedString': annotatedText,
                                                                          'user': self.userMenuList.get()}
            else:
                self.textField.tag_remove('ANNOTATE_SENSITIVE', '1.0', tk.END)
                del informationDict['annotations'][f"{indexStart},{indexEnd}"]
                self.redrawAnnotations()
        except tk.TclError:
            print(f'No text selected')

        self.updateAnnotationField()
        print(f'annotations: {self.listOfAnnotations}')

    #Ugly as Tkinter uses floats as indexing, e.g. third char in line 2 would be 2.3, while 24'th char would be 2.24
    def findSelection(self):
        selStartCol, _ = self.indexToColumn(self.textField.index(tk.SEL_FIRST))
        selEndCol, endColumn = self.indexToColumn(self.textField.index(tk.SEL_LAST))
        selEndCol -= 1
        selStartLine = math.floor(decimal.Decimal(self.textField.index(f'{tk.SEL_FIRST} linestart')))
        selEndLine = math.floor(decimal.Decimal(self.textField.index(f'{tk.SEL_LAST} lineend')))

        #The entire string from selStart's first char to last char of selEnd's line.
        wholeString = self.textField.get(self.textField.index(f'{tk.SEL_FIRST} linestart'), self.textField.index(f'{tk.SEL_LAST} lineend'))

        #Find beginning of word
        for i in range(selStartCol, 0, -1):
            if not ((wholeString[i-1] in string.punctuation ) or ( wholeString[i-1] in string.whitespace )):
                selStartCol -= 1
            else:
                break

        #Find end of word
        for i in range(selEndCol, endColumn-1):
            if not ((wholeString[i+1] in string.punctuation ) or ( wholeString[i+1] in string.whitespace )):
                selEndCol += 1
            else:
                break

        selStartCol = f'{selStartLine}.{selStartCol}'
        selEndCol = f'{selEndLine}.{selEndCol+1}'

        return selStartCol, selEndCol

    def indexToColumn(self, selIndex):

        selIndex = decimal.Decimal(selIndex)

        # calculate line start:
        lineNumber = math.floor(decimal.Decimal(self.textField.index(f'{selIndex} linestart')))

        # calculate line end:
        lineEndIndex = decimal.Decimal(self.textField.index(f'{selIndex} lineend'))
        lineEndDigitAmount = abs(decimal.Decimal(lineEndIndex).as_tuple().exponent)
        lineEndCeiling = round((lineEndIndex - lineNumber) * (10 ** lineEndDigitAmount))

        # calculate selStartIndexCorrected
        selIndexDigitAmount = abs(decimal.Decimal(selIndex - lineNumber).as_tuple().exponent)
        IndexDigitDifference = abs(lineEndDigitAmount - selIndexDigitAmount)
        selColumn = selIndex - lineNumber  # Uncorrected column but without the row
        selIndexCorrected = round(selColumn * decimal.Decimal(10 ** - IndexDigitDifference), lineEndDigitAmount)

        selColumnCorrected = round(selIndexCorrected * 10 ** lineEndDigitAmount)

        return selColumnCorrected, lineEndCeiling

    def redrawAnnotations(self):
        for k in self.listOfAnnotations[self.workingStringIndex]['annotations']:
            indeces = k.split(",")
            self.textField.tag_add('ANNOTATE_SENSITIVE', indeces[0], indeces[1])

    def updateAnnotationField(self):
        self.annotationTextField.config(state='normal')
        self.annotationTextField.delete('1.0', tk.END)
        for k, v in self.listOfAnnotations[self.workingStringIndex]['annotations'].items():
            label = v['label']
            annotatedString = v['annotatedString']
            user = v['user']
            self.annotationTextField.insert(tk.INSERT,(f'{label}: {annotatedString}, User: {user}\n'))
        self.annotationTextField.config(state='disabled')

    def saveAnnotationButtonAction(self, _event=None):
        filename = 'test.json'
        with open(filename, 'w+') as file:
            json.dump(self.listOfAnnotations,file)


    def loadSessionButtonAction(self, _event=None):
        file = tk.filedialog.askopenfile()
        fileName = file.name
        with open(fileName, 'r') as file:
            self.listOfAnnotations = json.load(file)

        self.updateAnnotationField()
        self.redrawAnnotations()

    def loadDataButtonAction(self, _event=None):
        file = tk.filedialog.askopenfile()
        fileName = file.name
        with open(fileName, 'r') as file:
            print("inside read")

    def nextButtonAction(self, _event=None):
        if self.workingStringIndex < len(self.listOfAnnotations)-1:
            self.workingStringIndex += 1
            self.textField.config(state='normal')
            self.textField.delete('1.0', tk.END)
            self.textField.insert(tk.INSERT, self.listOfAnnotations[self.workingStringIndex]['doc_string'])
            self.textField.config(state='disabled')
            self.updateAnnotationField()
            self.redrawAnnotations()

    def prevButtonAction(self, _event=None):
        if self.workingStringIndex > 0:
            self.workingStringIndex -= 1
            self.textField.config(state='normal')
            self.textField.delete('1.0', tk.END)
            self.textField.insert(tk.INSERT, self.listOfAnnotations[self.workingStringIndex]['doc_string'])
            self.textField.config(state='disabled')
            self.updateAnnotationField()
            self.redrawAnnotations()

    def bindKey(self, key, func):
        self.root.bind(key, func)

    def populateListOfAnnotation(self, docs):
        docList = []
        for item in docs:
            docList.append({'doc_ID': item['doc_ID'],
                                         'annotations': {},
                                         'doc_string': item['doc_string']})
        return docList

    def readDocs(self):
        testStrings = [{'doc_ID': 1,
                        'doc_string': "Line 1 sdkljhsadfjkl asdjkhsaduiiuweqruiohasdfkn nm"
                                         "asdfnasdnfb,anasdfjklasdklfjsadkjfjklasdfkljasdjkfhasjkldfj"
                                         "kladsk uioasdiuajk iopsadfjasdklf\n"},
                       {'doc_ID': 2,
                        'doc_string': "Line 2 asdajkhasd kjhsdf uyajk, kjlasdfkjh, kshadf.\n"},
                       {'doc_ID': 3,
                        'doc_string': "Line 3 asdafdjkldf +909kjsdf kljsdfjh, sdfkshadf.\n" },
                       {'doc_ID': 4,
                        'doc_string': "Line 4 with 13\n"}]
        self.listOfAnnotations = self.populateListOfAnnotation(testStrings)
        self.textField.config(state='normal')
        self.textField.delete('1.0', tk.END)
        self.textField.insert(tk.INSERT, self.listOfAnnotations[self.workingStringIndex]['doc_string'])
        self.textField.config(state='disabled')