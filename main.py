import sys
import GUI
import decimal

def main():
    gui = GUI.GUI((1200,550), (10,80))
    gui.setup()
    gui.bindKey('s', gui.annotateButtonAction)
    gui.bindKey('<Right>', gui.nextButtonAction)
    gui.bindKey('<Left>', gui.prevButtonAction)
    gui.startGUI()



if __name__ == '__main__':
    main()
