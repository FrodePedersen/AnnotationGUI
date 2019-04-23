import sys
import argparse
import GUI
import decimal

def main(size):
    gui = GUI.GUI(size)#, (20, 60))
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', nargs=2, help="sets the GUI size to be S1xS2. Measured in pixels")
    args = parser.parse_args()
    size = (1200,550)
    if args.s:
        size = (int(args.s[0]), int(args.s[1]))
    #print(size)

    main(size)
