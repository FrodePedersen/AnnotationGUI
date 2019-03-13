import string
import decimal
import math
import tkinter as tk
import tkinter.scrolledtext
from tkinter.font import Font
from tkinter import messagebox
from tkinter import filedialog
import json
import taboo_core.load_trees as load_trees


####
# Data structure of the annotations are as follows:
# {"Doc_ID": [{
#           "annotations": {
#                           "stringStartPos,stringEndPos": {
#                                                                "label": value,
#                                                                "annotatedString": string value,
#                                                                "user": string value
#                                                           }
#                           },
#           "sentence": entire sentence string shown in the GUI,
#           "sentenceIndex": index of the sentence start in the monsanto Doc,
#           "mon_fileName": filename of the monsanto Doc
#       }]
# }
#
# with annotations being a dictionary containing possibly multiple annotations per doc, with different labels and users.
####

####
# E X A M P L E
#
# {"Doc_ID": 23,
#  "annotations": {
#                  "1.7,1.18": {
#                                 "label": "sensitive",
#                                 "annotatedString": "HIV positive,
#                                 "user": Bob
#                               }
#                 },
#  "doc_string": "he was HIV positive"
#
####

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

        #Header:
        labelClass = 'NONE'
        fileName = 'NONE'
        doc_ID = 'NONE'
        amountOfSentencesInDoc = 0
        self.amountOfSentencesInFile = 0
        self.amountOfSentencesProcessed = 0
        self.amountOfAnnotations = 0

        self.headerLabelClass = tk.Label(self.root, text=f'label Class: {labelClass}', width=30)
        self.headerLabelFilename = tk.Label(self.root, text=f'Filename: {fileName}',  width=30)
        self.headerLabelDoc_ID = tk.Label(self.root, text=f'Doc_ID: {doc_ID}', width=30)
        self.headerLabelSentencesInDoc = tk.Label(self.root, text=f'Sentences in Document: {amountOfSentencesInDoc}', width=30)
        self.headerLabelSentencesInFile = tk.Label(self.root, text=f'Sentences in File: {self.amountOfSentencesInFile}', width=25)
        self.headerLabelSentencesInProcessed = tk.Label(self.root, text=f'Current Sentence index: {self.amountOfSentencesProcessed}',width=35)
        self.headerLabelAnnotationsSoFar = tk.Label(self.root, text=f'Amount of annotations so far: {self.amountOfAnnotations}',width=30)
        self.headerLabelUser = tk.Label(self.root, text=f'User:',width=20)



        self.textField.tag_configure("ANNOTATE_SENSITIVE", font=self.annotate_font, background=self.annotateFontColor)

        buttonWidth = 15
        self.annotationButton = tk.Button(self.root, width = buttonWidth, text="Annotate Sensitive", command = self.annotateButtonAction)
        self.loadSessionButton = tk.Button(self.root, width = buttonWidth, text="Load Session", command=self.loadSessionButtonAction)
        self.loadDataButton = tk.Button(self.root, width = buttonWidth, text="Load Data", command=self.loadDataButtonAction)
        self.saveSessionButton = tk.Button(self.root, width = buttonWidth, text="Save Session", command=self.saveAnnotationButtonAction)
        self.nextButton = tk.Button(self.root, width = buttonWidth, text="Next", command=self.nextButtonAction)
        self.prevButton = tk.Button(self.root, width = buttonWidth, text="Prev", command=self.prevButtonAction)

        options = []
        with open('res/Users.txt', 'r') as txt:
            for line in txt.readlines():
                options.append(line.strip())

        self.userMenuList = tk.StringVar(self.root)
        self.userMenuList.set('Frode')
        menu = tk.OptionMenu(self.root, self.userMenuList, *options)

        #Layout
        numberOfButtons = 6
        numberOfHeaderLabels = 7
        self.headerLabelClass.grid(row=0, column=1, padx=2)
        self.headerLabelFilename.grid(row=0, column=2, padx=2)
        self.headerLabelDoc_ID.grid(row=0, column=3, padx=2)
        self.headerLabelUser.grid(row=0, column=5, padx=2)
        self.headerLabelSentencesInDoc.grid(row=1, column=1, padx=2)
        self.headerLabelSentencesInFile.grid(row=1, column=2, padx=2)
        self.headerLabelSentencesInProcessed.grid(row=1, column=3, padx=2)
        self.headerLabelAnnotationsSoFar.grid(row=1, column=4, padx=2)


        menu.grid(row=1, column=5)

        self.annotationButton.grid(row=2, column=0, padx=10)
        self.loadSessionButton.grid(row=3, column=0)
        self.loadDataButton.grid(row=4, column=0)
        self.saveSessionButton.grid(row=5, column=0)
        self.nextButton.grid(row=6, column=0)
        self.prevButton.grid(row=7, column=0)

        self.textField.grid(row=2, column=1, rowspan=6, columnspan=4)
        self.annotationTextFieldLabel.grid(row=numberOfButtons+2, column=0)
        self.annotationTextField.grid(row=numberOfButtons+2, column=1, rowspan=numberOfButtons, columnspan=4)

        self.listOfdictOfDocs = []
        self.workingSentenceIndex = 0
        self.workingDocIndex = 0
        self.workingDocKey = ''

    def formatHeaderLabels(self):

        fileName = self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex]['mon_fileName']
        doc_ID = list(self.listOfdictOfDocs)[self.workingDocIndex]
        if len(fileName) > 20:
            fileName = fileName[:20] + '...'

        self.headerLabelDoc_ID['text'] = f'Doc_ID: {doc_ID}'
        self.headerLabelFilename['text'] = f'Filename: {fileName}'
        self.headerLabelSentencesInFile['text'] = f'Sentences in File: {self.amountOfSentencesInFile}'
        self.headerLabelSentencesInDoc['text'] = f'Sentences in Document: {len(self.listOfdictOfDocs[self.workingDocKey])}'
        self.headerLabelSentencesInProcessed['text'] = f'Current Sentence index: {self.amountOfSentencesProcessed}'
        self.headerLabelAnnotationsSoFar['text'] = f'Amount of annotations so far: {self.amountOfAnnotations}'



    def startGUI(self):
        self.root.mainloop()

    def setup(self):
        pass

    def insertInitialtext(self):
        
        self.workingDocKey = list(self.listOfdictOfDocs)[0]
        self.amountOfSentencesInFile = 0
        for v in self.listOfdictOfDocs.values():
            self.amountOfSentencesInFile += len(list(v))

        self.amountOfSentencesProcessed = 0
        self.workingDocIndex = 0
        self.workingSentenceIndex = 0

        self.textField.config(state='normal')
        self.textField.delete('1.0', tk.END)
        self.textField.insert(tk.INSERT, self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex]['sentence'])
        self.textField.config(state='disabled')
        self.formatHeaderLabels()

    def annotateButtonAction(self, _event=None):

        if self.userMenuList.get() == '':
            messagebox.showinfo('Invalid Action', 'Invalid User, please select a User')
            return

        # tk.TclError exception is raised if not text is selected
        try:
            indexStart, indexEnd = self.findSelection()
            annotatedText = self.textField.get(indexStart, indexEnd)
            informationDict = self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex] #get dictionary of string currently being worked on
            if f'{indexStart},{indexEnd}' not in informationDict['annotations']:
                self.textField.tag_add('ANNOTATE_SENSITIVE', indexStart, indexEnd)
                informationDict['annotations'][f"{indexStart},{indexEnd}"] = {'label': 'sensitive',
                                                                              'annotatedString': annotatedText,
                                                                              'user': self.userMenuList.get()}
                self.amountOfAnnotations += 1

            else:
                self.textField.tag_remove('ANNOTATE_SENSITIVE', '1.0', tk.END)
                del informationDict['annotations'][f"{indexStart},{indexEnd}"]
                self.amountOfAnnotations -= 1
                self.redrawAnnotations()
        except tk.TclError:
            print(f'No text selected')

        self.updateAnnotationField()
        #print(f'annotations: {self.listOfdictOfDocs}')

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
        for k in self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex]['annotations']:
            indeces = k.split(",")
            self.textField.tag_add('ANNOTATE_SENSITIVE', indeces[0], indeces[1])

    def updateAnnotationField(self):
        self.annotationTextField.config(state='normal')
        self.annotationTextField.delete('1.0', tk.END)
        for k, v in self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex]['annotations'].items():
            label = v['label']
            annotatedString = v['annotatedString']
            user = v['user']
            self.annotationTextField.insert(tk.INSERT,(f'{label}: "{annotatedString}", User: {user}\n'))
        self.annotationTextField.config(state='disabled')
        self.formatHeaderLabels()

    def saveAnnotationButtonAction(self, _event=None):
        filename = tk.filedialog.asksaveasfilename()
        with open(filename, 'w+') as file:
            json.dump(self.listOfdictOfDocs, file)

    def loadSessionButtonAction(self, _event=None):
        file = tk.filedialog.askopenfile()
        fileName = file.name
        with open(fileName, 'r') as file:
            self.listOfdictOfDocs = json.load(file)

        self.insertInitialtext()
        self.updateAnnotationField()
        self.redrawAnnotations()

    def loadDataButtonAction(self, _event=None):
        file = tk.filedialog.askopenfile()
        fileName = file.name
        listOfDocs = self.readFile(fileName)
        self.listOfdictOfDocs = listOfDocs

        self.insertInitialtext()


    def nextButtonAction(self, _event=None):
        if self.workingSentenceIndex < len(list(self.listOfdictOfDocs[self.workingDocKey]))-1:
            self.workingSentenceIndex += 1
        else:
            self.workingSentenceIndex = 0
            if self.workingDocIndex+1 < len(list(self.listOfdictOfDocs[self.workingDocKey]))-1:
                self.workingDocIndex += 1
                self.workingDocKey = list(self.listOfdictOfDocs)[self.workingDocIndex]

        self.textField.config(state='normal')
        self.textField.delete('1.0', tk.END)
        self.textField.insert(tk.INSERT, self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex]['sentence'])
        self.textField.config(state='disabled')
        if self.amountOfSentencesProcessed < self.amountOfSentencesInFile-1:
            self.amountOfSentencesProcessed += 1
        self.updateAnnotationField()
        self.redrawAnnotations()

    def prevButtonAction(self, _event=None):
        if self.workingSentenceIndex > 0:
            self.workingSentenceIndex -= 1
        else:
            if self.workingDocIndex > 0:
                self.workingDocIndex -= 1
                self.workingDocKey = list(self.listOfdictOfDocs)[self.workingDocIndex]
                self.workingSentenceIndex = len(list(self.listOfdictOfDocs[self.workingDocKey])) - 1

        self.textField.config(state='normal')
        self.textField.delete('1.0', tk.END)
        self.textField.insert(tk.INSERT, self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex]['sentence'])
        self.textField.config(state='disabled')
        if self.amountOfSentencesProcessed > 0:
            self.amountOfSentencesProcessed -= 1
        self.updateAnnotationField()
        self.redrawAnnotations()

    def bindKey(self, key, func):
        self.root.bind(key, func)

    #Reads a file containing trees
    #Returns a dictionary of docs with strings and meta data
    def readFile(self, fileName):
        trees = []

        with open(fileName, 'r') as file:
            for line in file.readlines():
                trees.append(load_trees.get_tree(line.rstrip(), fileName))

        initialDictOfDocs = {}

        for tree in trees:
            doc_ID = tree.word
            startCharIndex = tree.syntax
            textNode = tree.left
            mon_fileNameNode = tree.right
            text = load_trees.unescape_sentence(load_trees.output_sentence(textNode))
            mon_fileName = load_trees.output_sentence(mon_fileNameNode)
            if doc_ID not in initialDictOfDocs:
                initialDictOfDocs[doc_ID] = []

            initialDictOfDocs[doc_ID].append({"sentence": text,
                                              "sentenceIndex": startCharIndex,
                                              "mon_fileName": mon_fileName,
                                              "annotations": {} })
        return initialDictOfDocs
