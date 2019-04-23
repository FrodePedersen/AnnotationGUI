import sys
import GUI
import decimal

def main():
    gui = GUI.GUI((1200 ,550), (20, 60))
    gui.setup()
    #gui.readDocs()
    gui.bindKey('s', gui.annotateButtonAction)
    gui.bindKey('<Right>', gui.nextButtonAction)
    gui.bindKey('<Left>', gui.prevButtonAction)
    gui.startGUI()

    '''
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
    '''

if __name__ == '__main__':
    main()
