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
import re


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

    def __init__(self, GUIsize): #, textFieldSize):
        #Measured in pixels
        self.GUIheight = GUIsize[0]
        self.GUIwidth = GUIsize[1]

        #Measured in chars
        #self.textFieldHeight = textFieldSize[0]
        #self.textFieldWidth = textFieldSize[1]

        self.root = tk.Tk()
        self.root.geometry(f'{self.GUIheight}x{self.GUIwidth}')
        self.root.title('Annotation Tool')

        dummyFrame = tk.Frame(self.root)
        headerFrame = tk.Frame(self.root)
        buttonFrame = tk.Frame(self.root)
        textFrame = tk.Frame(self.root)


        self.textFontFamily = 'Helvetica'
        self.textFieldFontSize = 14
        self.annotateFontColor = '#00FFFF'
        self.annotate_font = Font(family=self.textFontFamily, size=self.textFieldFontSize, weight='bold')

        self.textField = tk.scrolledtext.ScrolledText(textFrame, font=(self.textFontFamily, self.textFieldFontSize)) #height = textFieldSize[0], width = textFieldSize[1],
        #self.annotationTextField = tk.scrolledtext.ScrolledText(textFrame, height=textFieldSize[0], width = textFieldSize[1], font=(self.textFontFamily, self.textFieldFontSize))
        self.annotationGuideField = tk.scrolledtext.ScrolledText(textFrame, font=(self.textFontFamily, self.textFieldFontSize)) # height=textFieldSize[0], width = int(textFieldSize[1] / 4),

        self.textField.config(state='disabled')
        #self.annotationTextField.config(state='disabled')
        self.annotationGuideField.config(state='disabled')

        #self.annotationTextFieldLabel = tk.Label(textFrame, text='Annotation Labels:')

        #Header:
        labelClass = 'NONE'
        fileName = 'NONE'
        doc_ID = 'NONE'
        amountOfSentencesInDoc = 0
        self.amountOfSentencesInFile = 0
        self.amountOfSentencesProcessed = 0
        self.amountOfAnnotations = 0

        self.headerLabelClass = tk.Label(headerFrame, text=f'label Class: {labelClass}', width=30)
        self.headerLabelFilename = tk.Label(headerFrame, text=f'Filename: {fileName}',  width=30)
        self.headerLabelDoc_ID = tk.Label(headerFrame, text=f'Doc_ID: {doc_ID}', width=30)
        self.headerLabelSentencesInDoc = tk.Label(headerFrame, text=f'Sentences in Document: {amountOfSentencesInDoc}', width=30)
        self.headerLabelSentencesInFile = tk.Label(headerFrame, text=f'Sentences in File: {self.amountOfSentencesInFile}', width=25)
        self.headerLabelSentencesInProcessed = tk.Label(headerFrame, text=f'Current Sentence index: {self.amountOfSentencesProcessed}',width=35)
        self.headerLabelAnnotationsSoFar = tk.Label(headerFrame, text=f'Amount of annotations this session: {self.amountOfAnnotations}',width=30)
        self.headerLabelGuide = tk.Label(headerFrame, text=f'Guide:', width=20)




        self.textField.tag_configure("ANNOTATE_SENSITIVE", font=self.annotate_font, background=self.annotateFontColor)
        buttonWidth = 17
        self.annotationButton = tk.Button(buttonFrame, width = buttonWidth, text="Annotate Sensitive ( s )", command = self.annotateButtonAction)
        self.loadSessionButton = tk.Button(buttonFrame, width = buttonWidth, text="Load Session", command=self.loadSessionButtonAction)
        self.loadDataButton = tk.Button(buttonFrame, width = buttonWidth, text="Load Data", command=self.loadDataButtonAction)
        self.saveSessionButton = tk.Button(buttonFrame, width = buttonWidth, text="Save Session", command=self.saveAnnotationButtonAction)
        self.nextButton = tk.Button(buttonFrame, width = buttonWidth, text="Next ( -> )", command=self.nextButtonAction)
        self.prevButton = tk.Button(buttonFrame, width = buttonWidth, text="Prev ( <- )", command=self.prevButtonAction)
        self.guideButton = tk.Button(buttonFrame, width = buttonWidth, text="Labeling Guide", command=self.guideButtonAction)

        options = []
        with open('res/Users.txt', 'r') as txt:
            for line in txt.readlines():
                options.append(line.strip())

        self.userMenuList = tk.StringVar(self.root)
        self.userMenuList.set('Select User')
        self.menu = tk.OptionMenu(buttonFrame, self.userMenuList, *options)
        self.guide = None

        #Layout
        numberOfRowCells = 6
        numberOfColumnCells = 10
        #root window
        tk.Grid.rowconfigure(self.root, 0, weight=1)
        tk.Grid.rowconfigure(self.root, 1, weight=6)
        tk.Grid.columnconfigure(self.root, 0, weight=1)
        tk.Grid.columnconfigure(self.root, 1, weight=6)

        #Frame windows
        dummyFrame.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        headerFrame.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        buttonFrame.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        textFrame.grid(row=1, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        dummyFrame.grid_propagate(False)
        headerFrame.grid_propagate(False)
        buttonFrame.grid_propagate(False)
        textFrame.grid_propagate(False)

        #Dummy layout
        tk.Grid.rowconfigure(dummyFrame, 0, weight=1)
        tk.Grid.columnconfigure(dummyFrame, 0, weight=1)

        #Header layout
        for i in range(2):
            tk.Grid.rowconfigure(headerFrame, i, weight=1)
            for j in range(5):
                tk.Grid.columnconfigure(headerFrame, j, weight=1)

        # self.headerLabelClass.grid(row=0, column=1, padx=2)
        self.headerLabelDoc_ID.grid(row=0, column=0)
        self.headerLabelFilename.grid(row=0, column=1)
        self.headerLabelSentencesInDoc.grid(row=1, column=0)
        self.headerLabelSentencesInFile.grid(row=1, column=1)
        self.headerLabelSentencesInProcessed.grid(row=1, column=2)
        self.headerLabelAnnotationsSoFar.grid(row=0, column=2)
        self.headerLabelGuide.grid(row=1, column=3)

        #Button layout
        numberOfButtons = 8
        for i in range(numberOfButtons):
            tk.Grid.rowconfigure(buttonFrame, i, weight=1)
            tk.Grid.columnconfigure(buttonFrame,0, weight=1)

        self.annotationButton.grid(row=0, column=0)
        self.loadSessionButton.grid(row=1, column=0)
        self.loadDataButton.grid(row=2, column=0)
        self.saveSessionButton.grid(row=3, column=0)
        self.nextButton.grid(row=4, column=0)
        self.prevButton.grid(row=5, column=0)
        self.menu.grid(row=6, column=0)
        self.guideButton.grid(row=7, column=0)

        #Textframe layouts
        tk.Grid.columnconfigure(textFrame, 0, weight=1)
        tk.Grid.columnconfigure(textFrame, 1,  weight=6)
        tk.Grid.rowconfigure(textFrame, 0, weight=1)

        self.annotationGuideField.grid(row=0, column=1)#, sticky=tk.N+tk.S+tk.E+tk.W, padx=10)
        self.textField.grid(row=0, column=0)#, sticky=tk.N+tk.S+tk.E+tk.W)
        #self.annotationTextFieldLabel.grid(row=numberOfButtons+2, column=0)
        #self.annotationTextField.grid(row=numberOfButtons+2, column=1, rowspan=numberOfButtons, columnspan=4)



        self.listOfdictOfDocs = []
        self.workingSentenceIndex = 0
        self.workingDocIndex = 0
        self.workingDocKey = ''

    def formatHeaderLabels(self):

        fileName = self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex]['mon_fileName']
        doc_ID = list(self.listOfdictOfDocs)[self.workingDocIndex]
        if len(fileName) > 20:
            fileName = fileName[:20] + '...'

        #print(f'doc_ID: {doc_ID}')

        self.headerLabelDoc_ID['text'] = f'Doc_ID: {doc_ID}'
        self.headerLabelFilename['text'] = f'Filename: {fileName}'
        self.headerLabelSentencesInFile['text'] = f'Sentences in File: {self.amountOfSentencesInFile}'
        self.headerLabelSentencesInDoc['text'] = f'Sentences in Document: {len(self.listOfdictOfDocs[self.workingDocKey])}'
        self.headerLabelSentencesInProcessed['text'] = f'Current Sentence index: {self.amountOfSentencesProcessed}'
        self.headerLabelAnnotationsSoFar['text'] = f'Amount of annotations this session: {self.amountOfAnnotations}'



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

        self.amountOfAnnotations = 0

        self.textField.config(state='normal')
        self.textField.delete('1.0', tk.END)
        self.textField.insert(tk.INSERT, self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex]['sentence'])
        self.textField.config(state='disabled')
        self.formatHeaderLabels()

    def annotateButtonAction(self, _event=None):
        user = self.userMenuList.get()
        if user == '' or user == 'Select User' or user == 'None':
            messagebox.showinfo('Invalid Action', f'Invalid User: -> {user} <-, please select a User')
            return

        # tk.TclError exception is raised if not text is selected
        try:
            indexStart, indexEnd = self.findSelection()
            annotatedText = self.textField.get(indexStart, indexEnd)
            informationDict = self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex] #get dictionary of string currently being worked on

            sentence = informationDict['sentence']
            regex = re.compile(r"\b{}\b".format(annotatedText), re.I)  # with the ignorecase option
            matchObj = regex.search(sentence)
            (start, end) = matchObj.span()

            label = 'sensitive'
            try:
                if self.guide:
                    label = self.guide[list(self.listOfdictOfDocs)[self.workingDocIndex]]['label']
            except:
                pass

            #print(f'label: {label}')

            if f'{indexStart},{indexEnd}' not in informationDict['annotations']:
                informationDict['annotations'][f"{indexStart},{indexEnd}"] = {'label': label,
                                                                              'annotatedString': annotatedText,
                                                                              'user': self.userMenuList.get(),
                                                                              'stringIdx': (start, end)}
                self.amountOfAnnotations += 1

                #print(f'annotated idx: {start, end}, text: {annotatedText}')
                entry = informationDict['annotations'][f"{indexStart},{indexEnd}"]
                #print(f'entry: {entry}')

            else:
                self.textField.tag_remove('ANNOTATE_SENSITIVE', '1.0', tk.END)
                del informationDict['annotations'][f"{indexStart},{indexEnd}"]
                self.amountOfAnnotations -= 1
                self.redrawAnnotations()
        except tk.TclError:
            print(f'No text selected')

        self.updateAnnotationField()
        self.redrawAnnotations()
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

    def focusText(self, startIdx, endIdx):
        self.textField.tag_add('ANNOTATE_FOCUS', startIdx, endIdx)

    def updateAnnotationField(self):
        preSentences, postSentences = self.collectText()
        preEndIndex = None
        self.textField.config(state='normal')
        self.textField.delete('1.0', tk.END)
        for sentenceDict in preSentences[::-1]:
            #print(f'sentenceDictPRE: {sentenceDict}')
            self.textField.insert(tk.INSERT, sentenceDict['sentence'])
        if preSentences:
            self.textField.insert(tk.INSERT, '\n\n')
        self.textField.insert(tk.INSERT, '-'*10 + '\n\n')
        self.textField.insert(tk.INSERT, self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex]['sentence']+'\n\n')
        self.textField.insert(tk.INSERT, '-' * 10 + '\n\n')
        for sentenceDict in postSentences:
            self.textField.insert(tk.INSERT, sentenceDict['sentence'])
        self.textField.config(state='disabled')


        #self.annotationTextField.config(state='normal')
        #self.annotationTextField.delete('1.0', tk.END)
        '''
        for k, v in self.listOfdictOfDocs[self.workingDocKey][self.workingSentenceIndex]['annotations'].items():
            label = v['label']
            annotatedString = v['annotatedString']
            user = v['user']
            self.annotationTextField.insert(tk.INSERT,(f'{label}: "{annotatedString}", User: {user}\n'))
        self.annotationTextField.config(state='disabled')
        '''
        self.formatHeaderLabels()
        self.displayGuide()

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
        self.updateAnnotationField()
        self.redrawAnnotations()


    def nextButtonAction(self, _event=None):
        if self.workingSentenceIndex < len(list(self.listOfdictOfDocs[self.workingDocKey]))-1:
            self.workingSentenceIndex += 1
        else:
            self.workingSentenceIndex = 0
            if self.workingDocIndex+1 < len(list(self.listOfdictOfDocs))-1:
                self.workingDocIndex += 1
                self.workingDocKey = list(self.listOfdictOfDocs)[self.workingDocIndex]

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

    def guideButtonAction(self):
        file = tk.filedialog.askopenfile()
        fileName = file.name
        guideJson = []
        self.guide = {}
        with open(fileName, 'r') as file:
            self.guideJson = json.load(file)

        for dict in self.guideJson:
            self.guide[dict['monsantoId']] = {'label': dict['label'],
                                             'uriText': dict['text']['val']}

        self.displayGuide()

    def displayGuide(self):
        #print(self.guide)
        try:
            if self.guide != None:
                currentDoc = self.workingDocKey
                self.annotationGuideField.config(state="normal")
                self.annotationGuideField.delete('1.0', tk.END)
                self.annotationGuideField.insert(tk.INSERT, 'Label:\n' + self.guide[currentDoc]['label'])
                self.annotationGuideField.insert(tk.INSERT, '\n\nGuide Text:\n')
                self.annotationGuideField.insert(tk.INSERT, self.guide[currentDoc]['uriText'])
                self.annotationGuideField.config(state="disabled")
        except:
            self.annotationGuideField.config(state="normal")
            self.annotationGuideField.delete('1.0', tk.END)
            self.annotationGuideField.insert(tk.INSERT, 'NO GUIDE FOUND FOR THIS DOCUMENT')
            self.annotationGuideField.config(state="disabled")

    def collectText(self):
        listOfSentences = list(self.listOfdictOfDocs[self.workingDocKey])
        preSentences = []
        postSentences = []
        if self.workingSentenceIndex > 0:
            for i in range(self.workingSentenceIndex-1,-1,-1):
                preSentences.append(listOfSentences[i])
                if len(preSentences) >= 3:
                    break
        if self.workingSentenceIndex < len(listOfSentences):
            for i in range(self.workingSentenceIndex+1,len(listOfSentences)):
                postSentences.append(listOfSentences[i])
                if len(postSentences) >= 3:
                    break


        return preSentences, postSentences
