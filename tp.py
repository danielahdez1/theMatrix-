#################################Information####################################
#Name: Daniela Hernandez
#Project: The Matrix!
#Description: 112 Term Project, Matrix Calculator with principal matrix operations
################################################################################

from cmu_112_graphics import*
from tkinter import *
import math
import random

#################################Operations####################################

#CITATION: https://realpython.com/python-rounding/
#Using this one instead of the ones in the course notes so I can round to decimal places
def roundHalfUp(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

#Creating A result Matrix
#CITATION: Course Notes - https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html
def makeResultMatrix(rows, cols):
    return [ ([0] * cols) for row in range(rows) ]

#Get the minor matrix of a matrix
#CITATION: Adapted from https://stackoverflow.com/questions/53934405/find-minor-matrix-in-python
def minorMatrix(m1, a, b):
    return [row[:b] + row[b+1:] for row in (m1[:a]+m1[a+1:])]

#Format Matrix for Steps
def formatMatrix(m1):

    if(isinstance(m1,str)):
        return m1

    result = []
    for element in m1:
        result.append(f'{element}')

    length = len(result)
    for index in range(length):
        if(index == 0 ):
            result[0] = '[' + result[0]
        elif(index == (length-1)):
            result[index] = '  ' + result[index] + ']'
        else:
            result[index] = ' ' + result[index]

    return result

#################################Graphics####################################

class HomeScreenMode(Mode):
    #CITATION: Load image idea from course notes: https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#imageMethods
    def appStarted(mode):
        mode.image1 = mode.loadImage('matrixWallpaper.png')
        mode.image2 = mode.scaleImage(mode.image1, 0.8)

    def redrawAll(mode, canvas):
        canvas.create_image(500, 300, image=ImageTk.PhotoImage(mode.image2))
        
        font = 'Arial 100 bold'
        cx, cy = mode.width/2, mode.height/2
        canvas.create_text(cx, cy-50, text='THE MATRIX!', font=font, fill='white')
        canvas.create_rectangle(cx-200, cy+150, cx+200, cy+250, fill='Black')
        canvas.create_text(cx, cy+200, text = 'CALCULATE', font = 'Arial 30 bold', fill = 'white')
        
    def mousePressed(mode, event):
        cx, cy = mode.width/2, mode.height/2
        if((cx-200 <= event.x <= cx+200) and (cy+150 <= event.y <= cy+250)):
            mode.app.setActiveMode(mode.app.calculateMode)

class CalculateMode(Mode):
    def redrawAll(mode, canvas):
        #Make the buttons
        font = 'Arial 45 bold'
        canvas.create_rectangle(0,0,200,350,fill='red')
        canvas.create_text(100,175, text='RREF', font=font, fill='white')
        canvas.create_rectangle(200,0,500,350,fill='green')
        canvas.create_text(350,175, text='Multiplication', font=font, fill='white')
        canvas.create_rectangle(500,0,750,525,fill='blue')
        canvas.create_text(625,263, text='Addition', font=font, fill='white')
        canvas.create_rectangle(750,0,1000,263,fill='tan')
        canvas.create_text(875,132, text='Inverse', font=font, fill='white')
        canvas.create_rectangle(0,350,270,700,fill='orange')
        canvas.create_text(135,525, text='Transpose', font=font, fill='white')
        canvas.create_rectangle(270,350,500,700,fill='purple')
        canvas.create_text(385,525, text='Basis', font=font, fill='white')
        canvas.create_rectangle(500,525,1000,700,fill='dark cyan')
        canvas.create_text(750,613, text='Determinant', font=font, fill='white')
        canvas.create_rectangle(750,263,1000,525,fill='palevioletred')
        canvas.create_text(875,394, text='Visualize', font=font, fill='white')

    def mousePressed(mode, event):
        #RREF Mode
        if((0 <= event.x <= 200) and (0 <= event.y <= 350)):
            mode.app.setActiveMode(mode.app.RREFMode)
        elif((200 <= event.x <= 500) and (0 <= event.y <= 350)):
            mode.app.setActiveMode(mode.app.multiplicationMode)
        elif((500 <= event.x <= 750) and (0 <= event.y <= 525)):
            mode.app.setActiveMode(mode.app.additionMode)
        elif((750 <= event.x <= 1000) and (0 <= event.y <= 263)):
            mode.app.setActiveMode(mode.app.inverseMode)
        elif((0 <= event.x <= 270) and (350 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.transposeMode)
        elif((270 <= event.x <= 500) and (350 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.basisMode)
        elif((500 <= event.x <= 1000) and (525 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.determinantMode)
        elif((750 <= event.x <= 1000) and (263 <= event.y <= 525)):
            mode.app.setActiveMode(mode.app.visualizeMode)

class RREFMode(Mode):
    def appStarted(mode):
        #Initializing Values for Grid
        mode.rows = 2
        mode.cols = 2
        mode.marginTop = 223
        mode.margin = 305
        mode.gridWidth = mode.width - 2*mode.margin
        mode.gridHeight = mode.height - 2*mode.marginTop 
        mode.cW = mode.gridWidth / mode.cols
        mode.cH = mode.gridHeight / mode.rows
        #Initialize Matrix Values
        mode.m1 = makeResultMatrix(mode.rows, mode.cols)
        #Initialize Users selecting and typing in screen values
        #Rows
        mode.rowsInput = ''
        mode.inputingRows = False
        mode.outlineColorR = 'black'
        #Cols
        mode.colsInput= ''
        mode.inputingCols = False
        mode.outlineColorC = 'black'
        #Matrix
        mode.cellClicked = (-1,-1)
        mode.inputingMatrix = False
        mode.matrixDigits = dict()
        mode.negativeValue = False
        #Input Error Messages
        mode.invalidInputMessage = ''
        mode.invalidMatrixMessage = ''
        #Initialize Solution
        mode.solution = None

    #This is call by the calculate det class when the back button is pressed
    def resetCalculation(mode):
        mode.appStarted()

    #CITATION (for getCell and getCellBounds): https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCell(mode, x, y):
        col = int((x - mode.margin) / mode.cW)
        row = int((y-mode.marginTop) / mode.cH)
        return (row, col)

    def getCellBounds(mode, row, col):
        x0 = mode.margin + col*mode.cW
        x1 = mode.margin + (col+1)*mode.cW
        y0 = mode.marginTop + row*mode.cH
        y1 = mode.marginTop + (row+1)*mode.cH
        return (x0, y0, x1, y1)
        
    def mousePressed(mode, event):
        #Get the number of rows
        if((400<=event.x<=450) and (100<=event.y<=150)):
            mode.inputingRows = True
            mode.outlineColorR = 'blue'
        #Get the numbet of columns
        if((550<=event.x<=600) and (100<=event.y<=150)):
            mode.inputingCols = True
            mode.outlineColorC = 'blue'
        #If the user clicks inside the grid, initialize inputing matrix
        if((306 <= event.x <= 694) and (220 <= event.y <= 478)):
            (row, col) = mode.getCell(event.x, event.y)
            mode.cellClicked = (row, col)
            mode.inputingMatrix = True
            mode.negativeValue = False
        #Calculate Button
        if((306 <= event.x <= 450) and (559 <= event.y <= 619)):
            mode.solution = mode.RREF(mode.m1)
            mode.app.RREFSolution = mode.solution
            mode.app.setActiveMode(mode.app.calculateRREF)
        #Reset Button
        if((550 <= event.x <= 6940) and (559 <= event.y <= 619)):
            mode.appStarted()
        #Menu Button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.calculateMode)

    def keyPressed(mode, event):
        #Inputing Number of Rows
        if(mode.inputingRows == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.rowsInput = f'{event.key}'
                mode.rows = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cH = mode.gridHeight / mode.rows
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingRows = False
            mode.outlineColorR = 'black'

        #Inputing Number of Cols
        if(mode.inputingCols == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.colsInput = f'{event.key}'
                mode.cols = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cW = mode.gridWidth / mode.cols
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingCols = False
            mode.outlineColorC = 'black'

        #For Negative Inputs
        if(event.key == '-'):
            mode.negativeValue = True

        #Inputing Matrix
        if(mode.inputingMatrix == True and mode.inputingRows == False and mode.inputingCols == False):
            #Only digits allowed
            if(event.key.isdigit()):
                (row,col) = mode.cellClicked
                #Dic allows for multiple digit integers
                value = mode.matrixDigits.get((row,col), '') + event.key 
                mode.matrixDigits[(row,col)] = value
                #Set the row and col of the matrix to the value inputed in the cell
                if(not mode.negativeValue):
                    mode.m1[row][col] = int(value)
                else:
                    mode.m1[row][col] = int(value) * (-1)

                print(mode.m1)
                mode.invalidInputMessage = ''
                
            elif(event.key == '-'):
                mode.negativeValue = True
            else:
                mode.invalidInputMessage = 'Invalid Input' 
                
    def rowSwap(mode, a1, a2, m1):
        m1[a1],m1[a2] = m1[a2],m1[a1]
        return m1

    #CITATION: Code from https://rosettacode.org/wiki/Reduced_row_echelon_form
    #This code follows the pseudocode in the website and it's adapted to use helper functions and some loops are rewrite. 
    #Find the RREF of a matrix
    def RREF(mode, m1):

        rows = len(m1)
        cols = len(m1[0])
        colWeAreIn = 0
        
        for r in range(rows):
            #When we finish looking through the cols in each row
            if (colWeAreIn >= cols):
                mode.app.RREFSteps.append(f'RREF -----> ')
                mode.app.RREFSteps.extend(formatMatrix(m1))
                return

            rowWeAreIn = r
            while (m1[rowWeAreIn][colWeAreIn] == 0):
                #Move to the next row to find a non-zero value
                rowWeAreIn += 1
                #If we rech the end of the rows, go back to the top and check in the next column
                if (rowWeAreIn == rows):
                    rowWeAreIn = r
                    colWeAreIn += 1
                    if (cols == colWeAreIn):
                        return
            
            #Swap row because ther's no pivot in the current one
            #Row Swap Helper Function
            m1 = mode.rowSwap(rowWeAreIn,r,m1)
            mode.app.RREFSteps.append('')
            mode.app.RREFSteps.append('Matrix: ----->')
            mode.app.RREFSteps.extend(formatMatrix(m1))
            mode.app.RREFSteps.append('')

            pivot = m1[r][colWeAreIn]
            mode.app.RREFSteps.append(f'Pivot = {pivot}')
            #Divide each value in the row by the pivot
            mode.app.RREFSteps.append(f'Divide each value in the row by the pivot: {pivot}')
            mode.app.RREFSteps.append(f'Row {m1[r]} / {pivot} ----->')
            rowDivided = []
            for value in m1[r]:
                element = value / pivot
                #The next 4 lines rounds the values of the matrix and displays them better
                element = roundHalfUp(element, 2)
                #CITATION: Learned about is_integer from:  https://note.nkmk.me/en/python-check-int-float/
                if(element.is_integer()):
                    element = int(element)
                if(int(abs(element) == 0)):
                    element = 0

                rowDivided.append(element)
            m1[r] = rowDivided
            mode.app.RREFSteps.extend(formatMatrix(m1))
            mode.app.RREFSteps.append('')
            
            #Subtract multiple of one row from another
            for rowWeAreIn in range(rows):
                if (rowWeAreIn != r):
                    pivot = m1[rowWeAreIn][colWeAreIn]
                    mode.app.RREFSteps.append('Subtract multiple of one row from another:')
                    mode.app.RREFSteps.append(f'Pivot = {pivot}')
                
                    rowReduced = []
                    for (value1,value2) in zip(m1[r],m1[rowWeAreIn]):
                        element = value2 - pivot*value1
                
                        element = roundHalfUp(element, 2) 
                        if(element.is_integer()):
                            element = int(element)
                        if(int(abs(element) == 0)):
                            element = 0
                    
                        rowReduced.append(element)

                    m1[rowWeAreIn] =  rowReduced
                    mode.app.RREFSteps.append('Reduced Row ----->')
                    mode.app.RREFSteps.extend(formatMatrix(m1))
                    mode.app.RREFSteps.append('')

            colWeAreIn += 1

        return m1

    def drawTitleAndInputs(mode,canvas):
        font = 'Verdana 20 bold'
        #Title and row and col input
        canvas.create_text(500,50, text='RREF: Input the Number of Rows and Columns', font=font)
        canvas.create_rectangle(400,100,450,150, width = 3, outline=mode.outlineColorR)
        canvas.create_text(425,180, text='ROWS', font=font)
        canvas.create_rectangle(550,100,600,150, width = 3, outline=mode.outlineColorC)
        canvas.create_text(575,180, text='COLS', font=font)
        #Display Inputs
        canvas.create_text(425,125, text=f'{mode.rowsInput}', font='Arial 25', fill='blue')
        canvas.create_text(575,125, text=f'{mode.colsInput}', font='Arial 25', fill='blue')
        #Invalid Input
        canvas.create_text(500,520, text=f'{mode.invalidInputMessage}', font='Arial 25', fill='red')

    def drawGridAndMatrix(mode, canvas):
        #Draw default matrix in default grid
        for row in range(mode.rows):
            for col in range(mode.cols):
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1)

        #Draw Inputed matrix In Grid
        for row in range(len(mode.m1)):
            for col in range(len(mode.m1[0])):
                value = mode.m1[row][col]
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                (cx, cy) = (x1-(mode.cW/2)), (y1-(mode.cH/2))
                if((row,col) == mode.cellClicked):
                    canvas.create_text(cx,cy, text=value, font='Verdana 20', fill = 'blue')
                else:
                    canvas.create_text(cx,cy, text=value, fill = 'black')

    def drawCalculateAndReset(mode,canvas):
        font = 'Verdana 20 bold'
        #Draw Calculate & Reset Button
        canvas.create_rectangle(306,559,450,619, fill='green')
        calculateCx = 306 + 72
        calculateCy = 559 + 30
        canvas.create_text(calculateCx,calculateCy, text='CALCULATE', font=font, fill='white')
        canvas.create_rectangle(550,559,694,619, fill='red')
        resetCx = 550 + 72
        resetCy = 559 + 30
        canvas.create_text(resetCx,resetCy, text='RESET', font=font, fill='white')

        #Invalid Matrix 
        canvas.create_text(500,520, text=f'{mode.invalidMatrixMessage}', font='Arial 25', fill='red')

    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawTitleAndInputs(canvas)
        mode.drawTitleAndInputs(canvas)
        mode.drawGridAndMatrix(canvas)
        mode.drawCalculateAndReset(canvas)
        mode.drawMenuButton(canvas)

class CalculateRREF(Mode):
    def appStarted(mode):
        mode.solution = mode.app.RREFSolution
        mode.steps = mode.app.RREFSteps
        mode.scrollY = 0

    def mousePressed(mode, event):
        #Clciked on Menu button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.RREFSteps = ['Finding RREF using row operations:','','(Use the up and down keys to scroll)','']
            mode.app.setActiveMode(mode.app.calculateMode)
        #Clicked on back button
        if((900 <= event.x <= 1000) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.RREFMode)
            mode.app.RREFSteps = ['Finding RREF using row operations:','','(Use the up and down keys to scroll)','']
            RREFMode.resetCalculation(mode)

    #CITATION: Up and Down Scrolling algorithm adapted from side scrolling example: http://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#sidescrollerExamples
    def keyPressed(mode, event):
        if(event.key == 'Up'):
            mode.scrollY += 20
        elif(event.key == 'Down'):
            mode.scrollY -= 20

    def drawSteps(mode, canvas):
        Titlefont = 'Verdana 20 bold'
        font = 'Verdana 16'
        spacing = 0
        items = 0
        #For when scrolling
        yPosition = 0
        yPosition += mode.scrollY

        #Go Through the list printing the Steps
        for step in mode.steps:
    
            items += 1
            spacing += 20
            if(items == 1):
                canvas.create_text(mode.width/2, 40 + yPosition, text = step, font = Titlefont)
            
            else: 
                canvas.create_text(mode.width/2, 20 + spacing + yPosition, text=step, font = font)
    
    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def drawBackButton(mode,canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(900,650,1000,700,fill = 'orange',outline='orange')
        canvas.create_text(950,675, text = 'BACK',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawSteps(canvas)
        mode.drawBackButton(canvas)
        mode.drawMenuButton(canvas)

class MultiplicationMode(Mode):
    def appStarted(mode):
        #Initializing Values for Grid
        #Grid for matrix 1
        mode.rows1 = 2
        mode.cols1 = 2
        mode.marginTop1 = 223
        mode.margin1 = 25
        mode.gridWidth1 = mode.width - 22*mode.margin1
        mode.gridHeight1 = mode.height - 2*mode.marginTop1 
        mode.cW1 = mode.gridWidth1 / mode.cols1
        mode.cH1 = mode.gridHeight1 / mode.rows1
        #Grid for matrix 2
        mode.rows2 = 2
        mode.cols2 = 2
        mode.marginTop2 = 223
        mode.margin2 = 525
        mode.gridWidth2 = mode.width - (550/525)*mode.margin2
        mode.gridHeight2 = mode.height - 2*mode.marginTop2 
        mode.cW2 = mode.gridWidth2 / mode.cols2
        mode.cH2 = mode.gridHeight2 / mode.rows2
        #Initialize Matrix Values
        mode.m1 = makeResultMatrix(mode.rows1, mode.cols1)
        mode.m2 = makeResultMatrix(mode.rows2, mode.cols2)
        #Initialize Users selecting and typing in screen values
        #Rows
        mode.rowsInput1 = ''
        mode.rowsInput2 = ''
        mode.inputingRows1 = False
        mode.inputingRows2 = False
        mode.outlineColorR1 = 'black'
        mode.outlineColorR2 = 'black'
        #Cols
        mode.colsInput1= ''
        mode.colsInput2= ''
        mode.inputingCols1 = False
        mode.inputingCols2 = False
        mode.outlineColorC1 = 'black'
        mode.outlineColorC2 = 'black'
        #Matrix
        mode.cellClickedM1 = (-1,-1)
        mode.cellClickedM2 = (-1,-1)
        mode.inputingMatrix1 = False
        mode.inputingMatrix2 = False
        mode.matrixDigits1 = dict()
        mode.matrixDigits2 = dict()
        mode.negativeValue = False
        #Input Error Messages
        mode.invalidInputMessage = ''
        mode.invalidMatrixMessage = ''
        #Initialize Solution
        mode.solution = None

    #This is call by the calculate multiplication class when the back button is pressed
    def resetCalculation(mode):
        mode.appStarted()

    #CITATION (for getCell and getCellBounds): https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCellM1(mode, x, y):
        col = int((x - mode.margin1) / mode.cW1)
        row = int((y - mode.marginTop1) / mode.cH1)
        return (row, col)

    def getCellM2(mode, x, y):
        col = int((x - mode.margin2) / mode.cW2)
        row = int((y - mode.marginTop2) / mode.cH2)
        return (row, col)

    def getCellBoundsM1(mode, row, col):
        x0 = mode.margin1 + col*mode.cW1
        x1 = mode.margin1 + (col+1)*mode.cW1
        y0 = mode.marginTop1 + row*mode.cH1
        y1 = mode.marginTop1 + (row+1)*mode.cH1
        return (x0, y0, x1, y1)

    def getCellBoundsM2(mode, row, col):
        x0 = mode.margin2 + col*mode.cW2
        x1 = mode.margin2 + (col+1)*mode.cW2
        y0 = mode.marginTop2 + row*mode.cH2
        y1 = mode.marginTop2 + (row+1)*mode.cH2
        return (x0, y0, x1, y1)
        
    def mousePressed(mode, event):
        #Get the number of rows
        if((150<=event.x<=200) and (100<=event.y<=150)):
            mode.inputingRows1 = True
            mode.outlineColorR1 = 'blue'
            mode.inputingMatrix1 = False
            mode.inputingMatrix2 = False
        if((650<=event.x<=700) and (100<=event.y<=150)):
            mode.inputingRows2 = True
            mode.outlineColorR2 = 'blue'
            mode.inputingMatrix1 = False
            mode.inputingMatrix2 = False
        #Get the numbet of columns
        if((300<=event.x<=350) and (100<=event.y<=150)):
            mode.inputingCols1 = True
            mode.outlineColorC1 = 'blue'
            mode.inputingMatrix1 = False
            mode.inputingMatrix2 = False
        if((800<=event.x<=850) and (100<=event.y<=150)):
            mode.inputingCols2 = True
            mode.outlineColorC2 = 'blue'
            mode.inputingMatrix1 = False
            mode.inputingMatrix2 = False
        #If the user clicks inside the grid for matrix 1, initialize inputing matrix 1
        if((25 <= event.x <= 475) and (220 <= event.y <= 478)):
            (row, col) = mode.getCellM1(event.x, event.y)
            mode.cellClickedM1 = (row, col)
            mode.inputingMatrix1 = True
            mode.inputingMatrix2 = False
            mode.negativeValue = False
        #If the user clicks inside the grid for matrix 2, initialize inputing matrix 2
        if((525 <= event.x <= 975) and (220 <= event.y <= 478)):
            (row, col) = mode.getCellM2(event.x, event.y)
            mode.cellClickedM2 = (row, col)
            mode.inputingMatrix2 = True
            mode.inputingMatrix1 = False
            mode.negativeValue = False
        #Calculate Button
        if((306 <= event.x <= 450) and (559 <= event.y <= 619)):
            #Non-Multtiplicable Matrices
            if(mode.cols1 != mode.rows2):
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = 'Matrix Multiplication is not legal.'
            #Use inputed matrices to call the multiplication function
            else:
                mode.solution = mode.matrixMultiplication(mode.m1,mode.m2)
                mode.app.multiplicationSolution = mode.solution
                mode.app.setActiveMode(mode.app.calculateMultiplication)
        #Reset Button
        if((550 <= event.x <= 6940) and (559 <= event.y <= 619)):
            mode.appStarted()
        #Menu Button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.calculateMode)

    def keyPressed(mode, event):
        #Inputing Number of Rows for Matrix 1
        if(mode.inputingRows1 == True):
            mode.inputingMatrix1 = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.rowsInput1 = f'{event.key}'
                mode.rows1 = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows1,mode.cols1)
                mode.cH1 = mode.gridHeight1 / mode.rows1
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingRows1 = False
            mode.outlineColorR = 'black'
        #Inputing Number of Rows for Matrix 2
        if(mode.inputingRows2 == True):
            mode.inputingMatrix2 = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.rowsInput2 = f'{event.key}'
                mode.rows2 = int(event.key)
                mode.m2 = makeResultMatrix(mode.rows2,mode.cols2)
                mode.cH2 = mode.gridHeight2 / mode.rows2
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingRows2 = False
            mode.outlineColorR = 'black'

        #Inputing Number of Cols for matrix 1
        if(mode.inputingCols1 == True):
            mode.inputingMatrix1 = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.colsInput1 = f'{event.key}'
                mode.cols1 = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows1,mode.cols1)
                mode.cW1 = mode.gridWidth1 / mode.cols1
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingCols1 = False
            mode.outlineColorC = 'black'
        #Inputing Number of Cols for matrix 1
        if(mode.inputingCols2 == True):
            mode.inputingMatrix2 = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.colsInput2 = f'{event.key}'
                mode.cols2 = int(event.key)
                mode.m2 = makeResultMatrix(mode.rows2,mode.cols2)
                mode.cW2 = mode.gridWidth2 / mode.cols2
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingCols2 = False
            mode.outlineColorC = 'black'

        #For Negative Inputs
        if(event.key == '-'):
            mode.negativeValue = True

        #Inputing Matrix 1
        if(mode.inputingMatrix1 == True and mode.inputingMatrix2 == False
            and mode.inputingRows1 == False and mode.inputingCols1 == False 
            and mode.inputingRows2 == False and mode.inputingCols2 == False):
            #Only digits allowed
            if(event.key.isdigit()):
                (row,col) = mode.cellClickedM1
                #Dic allows for multiple digit integers
                value = mode.matrixDigits1.get((row,col), '') + event.key 
                mode.matrixDigits1[(row,col)] = value
                #Set the row and col of the matrix to the value inputed in the cell
                if(not mode.negativeValue):
                    mode.m1[row][col] = int(value)
                else:
                    mode.m1[row][col] = int(value) * (-1)

                print(mode.m1)
                mode.invalidInputMessage = ''
                
            elif(event.key == '-'):
                mode.negativeValue = True
            else:
                mode.invalidInputMessage = 'Invalid Input' 
                
        #Inputing Matrix 2
        if(mode.inputingMatrix2 == True and mode.inputingMatrix1 == False
            and mode.inputingRows1 == False and mode.inputingCols1 == False 
            and mode.inputingRows2 == False and mode.inputingCols2 == False):
            #Only digits allowed
            if(event.key.isdigit()):
                (row,col) = mode.cellClickedM2
                #Dic allows for multiple digit integers
                value = mode.matrixDigits2.get((row,col), '') + event.key 
                mode.matrixDigits2[(row,col)] = value
                #Set the row and col of the matrix to the value inputed in the cell
                if(not mode.negativeValue):
                    mode.m2[row][col] = int(value)
                else:
                    mode.m2[row][col] = int(value) * (-1)

                print(mode.m2)
                mode.invalidInputMessage = ''
                
            elif(event.key == '-'):
                mode.negativeValue = True
            else:
                mode.invalidInputMessage = 'Invalid Input' 

    #Multiplication of two Matrices
    def matrixMultiplication(mode, m1, m2):
 
        rowsM1 = len(m1)
        colsM1 = len(m1[0])

        rowsM2 = len(m2)
        colsM2 = len(m2[0])
        
        #Build Result Matrix
        result = makeResultMatrix(rowsM1, colsM2)

        #Each row in m1 is multiplied by its corresponding element in the col of m2
        #for each row in m2
        mode.app.multiplicationSteps.extend(formatMatrix(m1))
        mode.app.multiplicationSteps.append('X')
        mode.app.multiplicationSteps.extend(formatMatrix(m2))
        mode.app.multiplicationSteps.append('')
        mode.app.multiplicationSteps.append('Multiply each element in the row with the corresponding element in the column')
        mode.app.multiplicationSteps.append('')
        for a in range(rowsM1):
            for b in range(colsM2):
                for c in range(rowsM2):

                    result[a][b] += m1[a][c] * m2[c][b]
                    
                    mode.app.multiplicationSteps.append(f'{m1[a][c]} * {m2[c][b]} = {m1[a][c] * m2[c][b]}')
                
                mode.app.multiplicationSteps.append('')
                mode.app.multiplicationSteps.append(f'Sum of row {a+1} times column {b+1} = {result[a][b]}')
                mode.app.multiplicationSteps.append(f'Element ({a+1},{b+1}) = {result[a][b]}')
                mode.app.multiplicationSteps.append('')

        mode.app.multiplicationSteps.append('Product Matrix ----->')
        mode.app.multiplicationSteps.extend(formatMatrix(result))
        return result

    def drawTitleAndInputs(mode,canvas):
        font = 'Verdana 20 bold'
        #Title and row and col input
        canvas.create_text(500,50, text='MULTIPLICATION: Input the Number of Rows and Columns', font=font)
        #Matrix 1 Inputs
        canvas.create_rectangle(150,100,200,150, width = 3, outline=mode.outlineColorR1)
        canvas.create_text(175,180, text='ROWS', font=font)
        canvas.create_rectangle(300,100,350,150, width = 3, outline=mode.outlineColorC1)
        canvas.create_text(325,180, text='COLS', font=font)
        #Matrix 2 Inputs
        canvas.create_rectangle(650,100,700,150, width = 3, outline=mode.outlineColorR2)
        canvas.create_text(675,180, text='ROWS', font=font)
        canvas.create_rectangle(800,100,850,150, width = 3, outline=mode.outlineColorC2)
        canvas.create_text(825,180, text='COLS', font=font)
        #Display Matrix 1 Inputs
        canvas.create_text(175,125, text=f'{mode.rowsInput1}', font='Arial 25', fill='blue')
        canvas.create_text(325,125, text=f'{mode.colsInput1}', font='Arial 25', fill='blue')
        #Display Matrix 2 Inputs
        canvas.create_text(675,125, text=f'{mode.rowsInput2}', font='Arial 25', fill='blue')
        canvas.create_text(825,125, text=f'{mode.colsInput2}', font='Arial 25', fill='blue')
        #Invalid Input
        canvas.create_text(500,520, text=f'{mode.invalidInputMessage}', font='Arial 25', fill='red')

    def drawGridAndMatrix1(mode, canvas):
        #Draw default matrix in default grid
        for row in range(mode.rows1):
            for col in range(mode.cols1):
                x0, y0, x1, y1 = mode.getCellBoundsM1(row, col)
                canvas.create_rectangle(x0, y0, x1, y1)

        #Draw Inputed matrix In Grid
        for row in range(len(mode.m1)):
            for col in range(len(mode.m1[0])):
                value = mode.m1[row][col]
                x0, y0, x1, y1 = mode.getCellBoundsM1(row, col)
                (cx, cy) = (x1-(mode.cW1/2)), (y1-(mode.cH1/2))
                if((row,col) == mode.cellClickedM1):
                    canvas.create_text(cx,cy, text=value, font='Verdana 20', fill = 'blue')
                else:
                    canvas.create_text(cx,cy, text=value, fill = 'black')

    def drawGridAndMatrix2(mode, canvas):
        #Draw default matrix in default grid
        for row in range(mode.rows2):
            for col in range(mode.cols2):
                x0, y0, x1, y1 = mode.getCellBoundsM2(row, col)
                canvas.create_rectangle(x0, y0, x1, y1)

        #Draw Inputed matrix In Grid
        for row in range(len(mode.m2)):
            for col in range(len(mode.m2[0])):
                value = mode.m2[row][col]
                x0, y0, x1, y1 = mode.getCellBoundsM2(row, col)
                (cx, cy) = (x1-(mode.cW2/2)), (y1-(mode.cH2/2))
                if((row,col) == mode.cellClickedM2):
                    canvas.create_text(cx,cy, text=value, font='Verdana 20', fill = 'blue')
                else:
                    canvas.create_text(cx,cy, text=value, fill = 'black')

    def drawCalculateAndReset(mode,canvas):
        font = 'Verdana 20 bold'
        #Draw Calculate & Reset Button
        canvas.create_rectangle(306,559,450,619, fill='green')
        calculateCx = 306 + 72
        calculateCy = 559 + 30
        canvas.create_text(calculateCx,calculateCy, text='CALCULATE', font=font, fill='white')
        canvas.create_rectangle(550,559,694,619, fill='red')
        resetCx = 550 + 72
        resetCy = 559 + 30
        canvas.create_text(resetCx,resetCy, text='RESET', font=font, fill='white')

        #Invalid Matrix 
        canvas.create_text(500,520, text=f'{mode.invalidMatrixMessage}', font='Arial 25', fill='red')

    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawTitleAndInputs(canvas)
        mode.drawTitleAndInputs(canvas)
        mode.drawGridAndMatrix1(canvas)
        mode.drawGridAndMatrix2(canvas)
        mode.drawCalculateAndReset(canvas)
        mode.drawMenuButton(canvas)

class CalculateMultiplication(Mode):
    def appStarted(mode):
        mode.solution = mode.app.multiplicationSolution
        mode.steps = mode.app.multiplicationSteps
        mode.scrollY = 0

    def mousePressed(mode, event):
        #Clciked on Menu button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.detSteps = mode.app.multiplicationSteps = ['Multiplying two matrices row-by-column:','','(Use the up and down keys to scroll)','']
            mode.app.setActiveMode(mode.app.calculateMode)
        #Clicked on back button
        if((900 <= event.x <= 1000) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.multiplicationMode)
            mode.app.detSteps = mode.app.multiplicationSteps = ['Multiplying two matrices row-by-column:','','(Use the up and down keys to scroll)','']
            MultiplicationMode.resetCalculation(mode)

    #CITATION: Up and Down Scrolling algorithm adapted from side scrolling example: http://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#sidescrollerExamples
    def keyPressed(mode, event):
        if(event.key == 'Up'):
            mode.scrollY += 20
        elif(event.key == 'Down'):
            mode.scrollY -= 20

    def drawSteps(mode, canvas):
        Titlefont = 'Verdana 20 bold'
        font = 'Verdana 16'
        spacing = 0
        items = 0
        #For when scrolling
        yPosition = 0
        yPosition += mode.scrollY

        #Go Through the list printing the Steps
        for step in mode.steps:
            items += 1
            spacing += 20
            if(items == 1):
                canvas.create_text(mode.width/2, 40 + yPosition, text = step, font = Titlefont)
            else: 
                canvas.create_text(mode.width/2, 20 + spacing + yPosition, text=step, font = font)
    
    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def drawBackButton(mode,canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(900,650,1000,700,fill = 'orange',outline='orange')
        canvas.create_text(950,675, text = 'BACK',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawSteps(canvas)
        mode.drawBackButton(canvas)
        mode.drawMenuButton(canvas)

class AdditionMode(Mode):
    def appStarted(mode):
        #Initializing Values for Grid
        #Grid for matrix 1
        mode.rows1 = 2
        mode.cols1 = 2
        mode.marginTop1 = 223
        mode.margin1 = 25
        mode.gridWidth1 = mode.width - 22*mode.margin1
        mode.gridHeight1 = mode.height - 2*mode.marginTop1 
        mode.cW1 = mode.gridWidth1 / mode.cols1
        mode.cH1 = mode.gridHeight1 / mode.rows1
        #Grid for matrix 2
        mode.rows2 = 2
        mode.cols2 = 2
        mode.marginTop2 = 223
        mode.margin2 = 525
        mode.gridWidth2 = mode.width - (550/525)*mode.margin2
        mode.gridHeight2 = mode.height - 2*mode.marginTop2 
        mode.cW2 = mode.gridWidth2 / mode.cols2
        mode.cH2 = mode.gridHeight2 / mode.rows2
        #Initialize Matrix Values
        mode.m1 = makeResultMatrix(mode.rows1, mode.cols1)
        mode.m2 = makeResultMatrix(mode.rows2, mode.cols2)
        #Initialize Users selecting and typing in screen values
        #Rows
        mode.rowsInput1 = ''
        mode.rowsInput2 = ''
        mode.inputingRows1 = False
        mode.inputingRows2 = False
        mode.outlineColorR1 = 'black'
        mode.outlineColorR2 = 'black'
        #Cols
        mode.colsInput1= ''
        mode.colsInput2= ''
        mode.inputingCols1 = False
        mode.inputingCols2 = False
        mode.outlineColorC1 = 'black'
        mode.outlineColorC2 = 'black'
        #Matrix
        mode.cellClickedM1 = (-1,-1)
        mode.cellClickedM2 = (-1,-1)
        mode.inputingMatrix1 = False
        mode.inputingMatrix2 = False
        mode.matrixDigits1 = dict()
        mode.matrixDigits2 = dict()
        mode.negativeValue = False
        #Input Error Messages
        mode.invalidInputMessage = ''
        mode.invalidMatrixMessage = ''
        #Initialize Solution
        mode.solution = None

    #This is call by the calculate multiplication class when the back button is pressed
    def resetCalculation(mode):
        mode.appStarted()

    #CITATION (for getCell and getCellBounds): https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCellM1(mode, x, y):
        col = int((x - mode.margin1) / mode.cW1)
        row = int((y - mode.marginTop1) / mode.cH1)
        return (row, col)

    def getCellM2(mode, x, y):
        col = int((x - mode.margin2) / mode.cW2)
        row = int((y - mode.marginTop2) / mode.cH2)
        return (row, col)

    def getCellBoundsM1(mode, row, col):
        x0 = mode.margin1 + col*mode.cW1
        x1 = mode.margin1 + (col+1)*mode.cW1
        y0 = mode.marginTop1 + row*mode.cH1
        y1 = mode.marginTop1 + (row+1)*mode.cH1
        return (x0, y0, x1, y1)

    def getCellBoundsM2(mode, row, col):
        x0 = mode.margin2 + col*mode.cW2
        x1 = mode.margin2 + (col+1)*mode.cW2
        y0 = mode.marginTop2 + row*mode.cH2
        y1 = mode.marginTop2 + (row+1)*mode.cH2
        return (x0, y0, x1, y1)
        
    def mousePressed(mode, event):
        #Get the number of rows
        if((150<=event.x<=200) and (100<=event.y<=150)):
            mode.inputingRows1 = True
            mode.outlineColorR1 = 'blue'
            mode.inputingMatrix1 = False
            mode.inputingMatrix2 = False
        if((650<=event.x<=700) and (100<=event.y<=150)):
            mode.inputingRows2 = True
            mode.outlineColorR2 = 'blue'
            mode.inputingMatrix1 = False
            mode.inputingMatrix2 = False
        #Get the numbet of columns
        if((300<=event.x<=350) and (100<=event.y<=150)):
            mode.inputingCols1 = True
            mode.outlineColorC1 = 'blue'
            mode.inputingMatrix1 = False
            mode.inputingMatrix2 = False
        if((800<=event.x<=850) and (100<=event.y<=150)):
            mode.inputingCols2 = True
            mode.outlineColorC2 = 'blue'
            mode.inputingMatrix1 = False
            mode.inputingMatrix2 = False
        #If the user clicks inside the grid for matrix 1, initialize inputing matrix 1
        if((25 <= event.x <= 475) and (220 <= event.y <= 478)):
            (row, col) = mode.getCellM1(event.x, event.y)
            mode.cellClickedM1 = (row, col)
            mode.inputingMatrix1 = True
            mode.inputingMatrix2 = False
            mode.negativeValue = False
        #If the user clicks inside the grid for matrix 2, initialize inputing matrix 2
        if((525 <= event.x <= 975) and (220 <= event.y <= 478)):
            (row, col) = mode.getCellM2(event.x, event.y)
            mode.cellClickedM2 = (row, col)
            mode.inputingMatrix2 = True
            mode.inputingMatrix1 = False
            mode.negativeValue = False
        #Calculate Button
        if((306 <= event.x <= 450) and (559 <= event.y <= 619)):
            #Non-Additive Matrices
            if(mode.cols1 != mode.cols2 or mode.rows1 != mode.rows2):
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = 'Matrix Addition is not legal.'
            #Use inputed matrices to call the addition function
            else:
                mode.solution = mode.matrixAddition(mode.m1,mode.m2)
                mode.app.additionSolution = mode.solution
                mode.app.setActiveMode(mode.app.calculateAddition)
        #Reset Button
        if((550 <= event.x <= 6940) and (559 <= event.y <= 619)):
            mode.appStarted()
        #Menu Button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.calculateMode)

    def keyPressed(mode, event):
        #Inputing Number of Rows for Matrix 1
        if(mode.inputingRows1 == True):
            mode.inputingMatrix1 = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.rowsInput1 = f'{event.key}'
                mode.rows1 = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows1,mode.cols1)
                mode.cH1 = mode.gridHeight1 / mode.rows1
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingRows1 = False
            mode.outlineColorR = 'black'
        #Inputing Number of Rows for Matrix 2
        if(mode.inputingRows2 == True):
            mode.inputingMatrix2 = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.rowsInput2 = f'{event.key}'
                mode.rows2 = int(event.key)
                mode.m2 = makeResultMatrix(mode.rows2,mode.cols2)
                mode.cH2 = mode.gridHeight2 / mode.rows2
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingRows2 = False
            mode.outlineColorR = 'black'

        #Inputing Number of Cols for matrix 1
        if(mode.inputingCols1 == True):
            mode.inputingMatrix1 = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.colsInput1 = f'{event.key}'
                mode.cols1 = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows1,mode.cols1)
                mode.cW1 = mode.gridWidth1 / mode.cols1
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingCols1 = False
            mode.outlineColorC = 'black'
        #Inputing Number of Cols for matrix 1
        if(mode.inputingCols2 == True):
            mode.inputingMatrix2 = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.colsInput2 = f'{event.key}'
                mode.cols2 = int(event.key)
                mode.m2 = makeResultMatrix(mode.rows2,mode.cols2)
                mode.cW2 = mode.gridWidth2 / mode.cols2
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingCols2 = False
            mode.outlineColorC = 'black'

        #For Negative Inputs
        if(event.key == '-'):
            mode.negativeValue = True

        #Inputing Matrix 1
        if(mode.inputingMatrix1 == True and mode.inputingMatrix2 == False
            and mode.inputingRows1 == False and mode.inputingCols1 == False 
            and mode.inputingRows2 == False and mode.inputingCols2 == False):
            #Only digits allowed
            if(event.key.isdigit()):
                (row,col) = mode.cellClickedM1
                #Dic allows for multiple digit integers
                value = mode.matrixDigits1.get((row,col), '') + event.key 
                mode.matrixDigits1[(row,col)] = value
                #Set the row and col of the matrix to the value inputed in the cell
                if(not mode.negativeValue):
                    mode.m1[row][col] = int(value)
                else:
                    mode.m1[row][col] = int(value) * (-1)

                print(mode.m1)
                mode.invalidInputMessage = ''
            
            elif(event.key == '-'):
                mode.negativeValue = True
            else:
                mode.invalidInputMessage = 'Invalid Input' 
                
        #Inputing Matrix 2
        if(mode.inputingMatrix2 == True and mode.inputingMatrix1 == False
            and mode.inputingRows1 == False and mode.inputingCols1 == False 
            and mode.inputingRows2 == False and mode.inputingCols2 == False):
            #Only digits allowed
            if(event.key.isdigit()):
                (row,col) = mode.cellClickedM2
                #Dic allows for multiple digit integers
                value = mode.matrixDigits2.get((row,col), '') + event.key 
                mode.matrixDigits2[(row,col)] = value
                #Set the row and col of the matrix to the value inputed in the cell
                if(not mode.negativeValue):
                    mode.m2[row][col] = int(value)
                else:
                    mode.m2[row][col] = int(value) * (-1)

                print(mode.m2)
                mode.invalidInputMessage = ''
                
            elif(event.key == '-'):
                mode.negativeValue = True
            else:
                mode.invalidInputMessage = 'Invalid Input' 

    #Add two matrices
    def matrixAddition(mode,m1, m2):
        rowsM1 = len(m1)
        colsM1 = len(m1[0])

        rowsM2 = len(m2)
        colsM2 = len(m2[0])
        
        #Build Result Matrix
        result = makeResultMatrix(rowsM1, colsM2)

        mode.app.additionSteps.extend(formatMatrix(m1))
        mode.app.additionSteps.append('+')
        mode.app.additionSteps.extend(formatMatrix(m2))
        mode.app.additionSteps.append('')
        mode.app.additionSteps.append('Add each element in Matrix 1 to the element in the corresponding row and column of Matrix 2')
        for a in range(rowsM1):
            for b in range(colsM2):
                result[a][b] += m1[a][b] + m2[a][b]
                mode.app.additionSteps.append('')
                mode.app.additionSteps.append(f'Element ({a+1},{b+1}) = {m1[a][b]} + {m2[a][b]} = {m1[a][b] + m2[a][b]}')
            
        mode.app.additionSteps.append('')
        mode.app.additionSteps.append('Sum Matrix ----->')
        mode.app.additionSteps.extend(formatMatrix(result))
        return result

    def drawTitleAndInputs(mode,canvas):
        font = 'Verdana 20 bold'
        #Title and row and col input
        canvas.create_text(500,50, text='ADDITION: Input the Number of Rows and Columns', font=font)
        #Matrix 1 Inputs
        canvas.create_rectangle(150,100,200,150, width = 3, outline=mode.outlineColorR1)
        canvas.create_text(175,180, text='ROWS', font=font)
        canvas.create_rectangle(300,100,350,150, width = 3, outline=mode.outlineColorC1)
        canvas.create_text(325,180, text='COLS', font=font)
        #Matrix 2 Inputs
        canvas.create_rectangle(650,100,700,150, width = 3, outline=mode.outlineColorR2)
        canvas.create_text(675,180, text='ROWS', font=font)
        canvas.create_rectangle(800,100,850,150, width = 3, outline=mode.outlineColorC2)
        canvas.create_text(825,180, text='COLS', font=font)
        #Display Matrix 1 Inputs
        canvas.create_text(175,125, text=f'{mode.rowsInput1}', font='Arial 25', fill='blue')
        canvas.create_text(325,125, text=f'{mode.colsInput1}', font='Arial 25', fill='blue')
        #Display Matrix 2 Inputs
        canvas.create_text(675,125, text=f'{mode.rowsInput2}', font='Arial 25', fill='blue')
        canvas.create_text(825,125, text=f'{mode.colsInput2}', font='Arial 25', fill='blue')
        #Invalid Input
        canvas.create_text(500,520, text=f'{mode.invalidInputMessage}', font='Arial 25', fill='red')

    def drawGridAndMatrix1(mode, canvas):
        #Draw default matrix in default grid
        for row in range(mode.rows1):
            for col in range(mode.cols1):
                x0, y0, x1, y1 = mode.getCellBoundsM1(row, col)
                canvas.create_rectangle(x0, y0, x1, y1)

        #Draw Inputed matrix In Grid
        for row in range(len(mode.m1)):
            for col in range(len(mode.m1[0])):
                value = mode.m1[row][col]
                x0, y0, x1, y1 = mode.getCellBoundsM1(row, col)
                (cx, cy) = (x1-(mode.cW1/2)), (y1-(mode.cH1/2))
                if((row,col) == mode.cellClickedM1):
                    canvas.create_text(cx,cy, text=value, font='Verdana 20', fill = 'blue')
                else:
                    canvas.create_text(cx,cy, text=value, fill = 'black')

    def drawGridAndMatrix2(mode, canvas):
        #Draw default matrix in default grid
        for row in range(mode.rows2):
            for col in range(mode.cols2):
                x0, y0, x1, y1 = mode.getCellBoundsM2(row, col)
                canvas.create_rectangle(x0, y0, x1, y1)

        #Draw Inputed matrix In Grid
        for row in range(len(mode.m2)):
            for col in range(len(mode.m2[0])):
                value = mode.m2[row][col]
                x0, y0, x1, y1 = mode.getCellBoundsM2(row, col)
                (cx, cy) = (x1-(mode.cW2/2)), (y1-(mode.cH2/2))
                if((row,col) == mode.cellClickedM2):
                    canvas.create_text(cx,cy, text=value, font='Verdana 20', fill = 'blue')
                else:
                    canvas.create_text(cx,cy, text=value, fill = 'black')

    def drawCalculateAndReset(mode,canvas):
        font = 'Verdana 20 bold'
        #Draw Calculate & Reset Button
        canvas.create_rectangle(306,559,450,619, fill='green')
        calculateCx = 306 + 72
        calculateCy = 559 + 30
        canvas.create_text(calculateCx,calculateCy, text='CALCULATE', font=font, fill='white')
        canvas.create_rectangle(550,559,694,619, fill='red')
        resetCx = 550 + 72
        resetCy = 559 + 30
        canvas.create_text(resetCx,resetCy, text='RESET', font=font, fill='white')

        #Invalid Matrix 
        canvas.create_text(500,520, text=f'{mode.invalidMatrixMessage}', font='Arial 25', fill='red')

    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawTitleAndInputs(canvas)
        mode.drawTitleAndInputs(canvas)
        mode.drawGridAndMatrix1(canvas)
        mode.drawGridAndMatrix2(canvas)
        mode.drawCalculateAndReset(canvas)
        mode.drawMenuButton(canvas)

class CalculateAddition(Mode):
    def appStarted(mode):
        mode.solution = mode.app.additionSolution
        mode.steps = mode.app.additionSteps
        mode.scrollY = 0

    def mousePressed(mode, event):
        #Clciked on Menu button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.detSteps = mode.app.additionSteps = ['Addition two matrices element-by-element:','','(Use the up and down keys to scroll)','']
            mode.app.setActiveMode(mode.app.calculateMode)
        #Clicked on back button
        if((900 <= event.x <= 1000) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.additionMode)
            mode.app.detSteps = mode.app.additionSteps = ['Addition two matrices element-by-element:','','(Use the up and down keys to scroll)','']
            AdditionMode.resetCalculation(mode)

    #CITATION: Up and Down Scrolling algorithm adapted from side scrolling example: http://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#sidescrollerExamples
    def keyPressed(mode, event):
        if(event.key == 'Up'):
            mode.scrollY += 20
        elif(event.key == 'Down'):
            mode.scrollY -= 20

    def drawSteps(mode, canvas):
        Titlefont = 'Verdana 20 bold'
        font = 'Verdana 16'
        spacing = 0
        items = 0
        #For when scrolling
        yPosition = 0
        yPosition += mode.scrollY

        #Go Through the list printing the Steps
        for step in mode.steps:
            items += 1
            spacing += 20
            if(items == 1):
                canvas.create_text(mode.width/2, 40 + yPosition, text = step, font = Titlefont)
            else: 
                canvas.create_text(mode.width/2, 20 + spacing + yPosition, text=step, font = font)
    
    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def drawBackButton(mode,canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(900,650,1000,700,fill = 'orange',outline='orange')
        canvas.create_text(950,675, text = 'BACK',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawSteps(canvas)
        mode.drawBackButton(canvas)
        mode.drawMenuButton(canvas)

class InverseMode(Mode):
    def appStarted(mode):
        #Initializing Values for Grid
        mode.rows = 2
        mode.cols = 2
        mode.marginTop = 223
        mode.margin = 305
        mode.gridWidth = mode.width - 2*mode.margin
        mode.gridHeight = mode.height - 2*mode.marginTop 
        mode.cW = mode.gridWidth / mode.cols
        mode.cH = mode.gridHeight / mode.rows
        #Initialize Matrix Values
        mode.m1 = makeResultMatrix(mode.rows, mode.cols)
        #Initialize Users selecting and typing in screen values
        #Rows
        mode.rowsInput = ''
        mode.inputingRows = False
        mode.outlineColorR = 'black'
        #Cols
        mode.colsInput= ''
        mode.inputingCols = False
        mode.outlineColorC = 'black'
        #Matrix
        mode.cellClicked = (-1,-1)
        mode.inputingMatrix = False
        mode.matrixDigits = dict()
        mode.negativeValue = False
        #Input Error Messages
        mode.invalidInputMessage = ''
        mode.invalidMatrixMessage = ''
        #Initialize Solution
        mode.solution = None

    #This is call by the calculate det class when the back button is pressed
    def resetCalculation(mode):
        mode.appStarted()

    #CITATION (for getCell and getCellBounds): https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCell(mode, x, y):
        col = int((x - mode.margin) / mode.cW)
        row = int((y-mode.marginTop) / mode.cH)
        return (row, col)

    def getCellBounds(mode, row, col):
        x0 = mode.margin + col*mode.cW
        x1 = mode.margin + (col+1)*mode.cW
        y0 = mode.marginTop + row*mode.cH
        y1 = mode.marginTop + (row+1)*mode.cH
        return (x0, y0, x1, y1)
        
    def mousePressed(mode, event):
        #Get the number of rows
        if((400<=event.x<=450) and (100<=event.y<=150)):
            mode.inputingRows = True
            mode.outlineColorR = 'blue'
        #Get the numbet of columns
        if((550<=event.x<=600) and (100<=event.y<=150)):
            mode.inputingCols = True
            mode.outlineColorC = 'blue'
        #If the user clicks inside the grid, initialize inputing matrix
        if((306 <= event.x <= 694) and (220 <= event.y <= 478)):
            (row, col) = mode.getCell(event.x, event.y)
            mode.cellClicked = (row, col)
            mode.inputingMatrix = True
            mode.negativeValue = False
        #Calculate Button
        if((306 <= event.x <= 450) and (559 <= event.y <= 619)):
            #Non-Square Matrix
            if(mode.cols != mode.rows):
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = 'The inverse only exists for square matrices!'
            #Non-Invertible Matrix
            elif(mode.determinant(mode.m1) == 0):
                mode.invalidMatrixMessage = 'Non-Invertible Matrix'
            #Use inputed matrix to call the inverse function
            else:
                mode.solution = mode.inverse(mode.m1)
                mode.app.inverseSolution = mode.solution
                mode.app.setActiveMode(mode.app.calculateInverse)
        #Reset Button
        if((550 <= event.x <= 6940) and (559 <= event.y <= 619)):
            mode.appStarted()
        #Menu Button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.calculateMode)

    def keyPressed(mode, event):
        #Inputing Number of Rows
        if(mode.inputingRows == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.rowsInput = f'{event.key}'
                mode.rows = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cH = mode.gridHeight / mode.rows
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingRows = False
            mode.outlineColorR = 'black'

        #Inputing Number of Cols
        if(mode.inputingCols == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.colsInput = f'{event.key}'
                mode.cols = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cW = mode.gridWidth / mode.cols
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingCols = False
            mode.outlineColorC = 'black'

        #For Negative Inputs
        if(event.key == '-'):
            mode.negativeValue = True

        #Inputing Matrix
        if(mode.inputingMatrix == True and mode.inputingRows == False and mode.inputingCols == False):
            #Only digits allowed
            if(event.key.isdigit()):
                (row,col) = mode.cellClicked
                #Dic allows for multiple digit integers
                value = mode.matrixDigits.get((row,col), '') + event.key 
                mode.matrixDigits[(row,col)] = value
                #Set the row and col of the matrix to the value inputed in the cell
                if(not mode.negativeValue):
                    mode.m1[row][col] = int(value)
                else:
                    mode.m1[row][col] = int(value) * (-1)

                
                print(mode.m1)
                mode.invalidInputMessage = ''
                
            elif(event.key == '-'):
                mode.negativeValue = True
            else:
                mode.invalidInputMessage = 'Invalid Input' 
           
    def inverse(mode, m1):
        mode.app.inverseSteps.append('Matrix ----->')
        mode.app.inverseSteps.extend(formatMatrix(m1))
        mode.app.inverseSteps.append('First, find the determinant of the matrix and take its reciprocal')
        reciprocal = 1/mode.determinant(m1)
        reciprocal = roundHalfUp(reciprocal,2)
        mode.app.inverseSteps.append('')
        mode.app.inverseSteps.append('')
        mode.app.inverseSteps.append('Use the cofactors in the determinant calculation to build a cofactor matrix') 
        mode.app.inverseSteps.append('')
        mode.app.inverseSteps.append('')
        mode.app.inverseSteps.append('Then, transpose the cofactor matrix')
        Ct = mode.transpose(mode.cofactorMatrix(m1))
        mode.app.inverseSteps.append('')
        mode.app.inverseSteps.append('')
        mode.app.inverseSteps.append('Finally, multiply the reciprocal of the determinant by the transpose of the cofactor matrix')
        inverse = mode.constantMultiplication(Ct, reciprocal)
        mode.app.inverseSteps.append('')
        mode.app.inverseSteps.append('')
        mode.app.inverseSteps.append(f'Inverse ----->')
        mode.app.inverseSteps.extend(formatMatrix(inverse))
        return inverse

    #Helper Function:
    def determinant(mode, m1):
        mode.app.inverseSteps.append(f'Matrix ----->')
        mode.app.inverseSteps.extend(formatMatrix(m1))
        mode.app.inverseSteps.append('')
        
        #Single element matrix
        if(len(m1)==1 and len(m1[0])==1):
            mode.app.inverseSteps.append('')
            mode.app.inverseSteps.extend(formatMatrix(m1))
            mode.app.inverseSteps.append(f'DET = {m1[0][0]}')
            return m1[0][0]

        rows = len(m1)
        cols = len(m1[0])

        #Base case: 2*2 Matrix
        if(len(m1)==2):
            det = (m1[0][0]*m1[1][1]) - (m1[0][1]*m1[1][0])
            mode.app.inverseSteps.append(f'DET = ({m1[0][0]}*{m1[1][1]}) - ({m1[0][1]}*{m1[1][0]}) = {det}')
        
            return det
        else:
            det = 0
            #Iterate through the elements in the first row
            #The row is 0, what's changing is the columns
            for b in range(cols):
                subMatrix = minorMatrix(m1,0,b)
                mode.app.inverseSteps.append('')
                mode.app.inverseSteps.append(f'For value {m1[0][b]} in Row 1:')
                mode.app.inverseSteps.append('Find the Determinant of the Sub-Matrix')
                intermediateStep = m1[0][b] * (-1)**(b) * mode.determinant(subMatrix)

                mode.app.inverseSteps.append(f'C_({1},{b+1}) = (-1)^({1}+{b+1}) * {m1[0][b]} * DET(Sub-Matrix)')
                mode.app.inverseSteps.append(f'C_({1},{b+1}) = {intermediateStep}')
                mode.app.inverseSteps.append('')
                det += intermediateStep
                
            mode.app.inverseSteps.append('Sum All the cofactors:')
            mode.app.inverseSteps.append('DET -----> ')
            mode.app.inverseSteps.append(f'{det}')
            return det

    #Helper Function:
    #Generate the cofactor matrix of a given matrix
    def cofactorMatrix(mode, m1):
        rows = len(m1)
        cols = len(m1[0])
        
        #Build the cofactorMatrix
        C = makeResultMatrix(rows, cols)

        for a in range(rows):
            for b in range(cols):
                subMatrix = minorMatrix(m1,a,b)
                C[a][b] = (-1)**(a+b) * mode.determinant(subMatrix)
        mode.app.inverseSteps.append(f'Cofactor Matrix -----> = {C})')
        mode.app.inverseSteps.extend(formatMatrix(C))
        return C

    #Helper Function:
    #Transpose a matrix
    def transpose(mode,m1):
        rows = len(m1)
        cols = len(m1[0])

        mode.app.inverseSteps.extend(formatMatrix(m1))
    
        result = makeResultMatrix(cols, rows)

        newRows = len(result)
        newCols = len(result[0])

        for a in range(newRows):
            for b in range(newCols):
                result[a][b] += m1[b][a]

        mode.app.inverseSteps.append('')
        mode.app.inverseSteps.append('')
        mode.app.inverseSteps.append('Transpose ----->')
        mode.app.inverseSteps.extend(formatMatrix(result))
        return result

    #Helper Function
    #Multiply a matrix by a constant
    def constantMultiplication(mode, m1, n):
        rows = len(m1)
        cols = len(m1[0])

        for a in range(rows):
            for b in range(cols):
                m1[a][b] = roundHalfUp(m1[a][b] * n,2)        

        return m1

    def drawTitleAndInputs(mode,canvas):
        font = 'Verdana 20 bold'
        #Title and row and col input
        canvas.create_text(500,50, text='INVERSE: Input the Number of Rows and Columns', font=font)
        canvas.create_rectangle(400,100,450,150, width = 3, outline=mode.outlineColorR)
        canvas.create_text(425,180, text='ROWS', font=font)
        canvas.create_rectangle(550,100,600,150, width = 3, outline=mode.outlineColorC)
        canvas.create_text(575,180, text='COLS', font=font)
        #Display Inputs
        canvas.create_text(425,125, text=f'{mode.rowsInput}', font='Arial 25', fill='blue')
        canvas.create_text(575,125, text=f'{mode.colsInput}', font='Arial 25', fill='blue')
        #Invalid Input
        canvas.create_text(500,520, text=f'{mode.invalidInputMessage}', font='Arial 25', fill='red')

    def drawGridAndMatrix(mode, canvas):
        #Draw default matrix in default grid
        for row in range(mode.rows):
            for col in range(mode.cols):
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1)

        #Draw Inputed matrix In Grid
        for row in range(len(mode.m1)):
            for col in range(len(mode.m1[0])):
                value = mode.m1[row][col]
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                (cx, cy) = (x1-(mode.cW/2)), (y1-(mode.cH/2))
                if((row,col) == mode.cellClicked):
                    canvas.create_text(cx,cy, text=value, font='Verdana 20', fill = 'blue')
                else:
                    canvas.create_text(cx,cy, text=value, fill = 'black')

    def drawCalculateAndReset(mode,canvas):
        font = 'Verdana 20 bold'
        #Draw Calculate & Reset Button
        canvas.create_rectangle(306,559,450,619, fill='green')
        calculateCx = 306 + 72
        calculateCy = 559 + 30
        canvas.create_text(calculateCx,calculateCy, text='CALCULATE', font=font, fill='white')
        canvas.create_rectangle(550,559,694,619, fill='red')
        resetCx = 550 + 72
        resetCy = 559 + 30
        canvas.create_text(resetCx,resetCy, text='RESET', font=font, fill='white')

        #Invalid Matrix 
        canvas.create_text(500,520, text=f'{mode.invalidMatrixMessage}', font='Arial 25', fill='red')

    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawTitleAndInputs(canvas)
        mode.drawTitleAndInputs(canvas)
        mode.drawGridAndMatrix(canvas)
        mode.drawCalculateAndReset(canvas)
        mode.drawMenuButton(canvas)

class CalculateInverse(Mode):
    def appStarted(mode):
        mode.solution = mode.app.inverseSolution
        mode.steps = mode.app.inverseSteps
        mode.scrollY = 0

    def mousePressed(mode, event):
        #Clciked on Menu button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.inverseSteps = ['Finding the inverse by using the cofactor matrix: A^-1 = 1/det(A) * C^T','','(Use the up and down keys to scroll)','']
            mode.app.setActiveMode(mode.app.calculateMode)
        #Clicked on back button
        if((900 <= event.x <= 1000) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.inverseMode)
            mode.app.inverseSteps = ['Finding the inverse by using the cofactor matrix: A^-1 = 1/det(A) * C^T','','(Use the up and down keys to scroll)','']
            InverseMode.resetCalculation(mode)

    #CITATION: Up and Down Scrolling algorithm adapted from side scrolling example: http://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#sidescrollerExamples
    def keyPressed(mode, event):
        if(event.key == 'Up'):
            mode.scrollY += 20
        elif(event.key == 'Down'):
            mode.scrollY -= 20

    def drawSteps(mode, canvas):
        Titlefont = 'Verdana 20 bold'
        font = 'Verdana 16'
        spacing = 0
        items = 0
        #For when scrolling
        yPosition = 0
        yPosition += mode.scrollY

        #Go Through the list printing the Steps
        for step in mode.steps:
            items += 1
            spacing += 20
            if(items == 1):
                canvas.create_text(mode.width/2, 40 + yPosition, text = step, font = Titlefont)
            else: 
                canvas.create_text(mode.width/2, 20 + spacing + yPosition, text=step, font = font)
    
    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def drawBackButton(mode,canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(900,650,1000,700,fill = 'orange',outline='orange')
        canvas.create_text(950,675, text = 'BACK',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawSteps(canvas)
        mode.drawBackButton(canvas)
        mode.drawMenuButton(canvas)

class TransposeMode(Mode):
     
    def appStarted(mode):
        #Initializing Values for Grid
        mode.rows = 2
        mode.cols = 2
        mode.marginTop = 223
        mode.margin = 305
        mode.gridWidth = mode.width - 2*mode.margin
        mode.gridHeight = mode.height - 2*mode.marginTop 
        mode.cW = mode.gridWidth / mode.cols
        mode.cH = mode.gridHeight / mode.rows
        #Initialize Matrix Values
        mode.m1 = makeResultMatrix(mode.rows, mode.cols)
        #Initialize Users selecting and typing in screen values
        #Rows
        mode.rowsInput = ''
        mode.inputingRows = False
        mode.outlineColorR = 'black'
        #Cols
        mode.colsInput= ''
        mode.inputingCols = False
        mode.outlineColorC = 'black'
        #Matrix
        mode.cellClicked = (-1,-1)
        mode.inputingMatrix = False
        mode.matrixDigits = dict()
        mode.negativeValue = False
        #Input Error Messages
        mode.invalidInputMessage = ''
        #Initialize Solution
        mode.solution = None

    #This is call by the calculate det class when the back button is pressed
    def resetCalculation(mode):
        mode.appStarted()

    #CITATION (for getCell and getCellBounds): https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCell(mode, x, y):
        col = int((x - mode.margin) / mode.cW)
        row = int((y-mode.marginTop) / mode.cH)
        return (row, col)

    def getCellBounds(mode, row, col):
        x0 = mode.margin + col*mode.cW
        x1 = mode.margin + (col+1)*mode.cW
        y0 = mode.marginTop + row*mode.cH
        y1 = mode.marginTop + (row+1)*mode.cH
        return (x0, y0, x1, y1)
        
    def mousePressed(mode, event):
        #Get the number of rows
        if((400<=event.x<=450) and (100<=event.y<=150)):
            mode.inputingRows = True
            mode.outlineColorR = 'blue'
        #Get the numbet of columns
        if((550<=event.x<=600) and (100<=event.y<=150)):
            mode.inputingCols = True
            mode.outlineColorC = 'blue'
        #If the user clicks inside the grid, initialize inputing matrix
        if((306 <= event.x <= 694) and (220 <= event.y <= 478)):
            (row, col) = mode.getCell(event.x, event.y)
            mode.cellClicked = (row, col)
            mode.inputingMatrix = True
            mode.negativeValue = False
        #Calculate Button
        if((306 <= event.x <= 450) and (559 <= event.y <= 619)):
            #Use inputed matrix to call the determinant function
            mode.solution = mode.transpose(mode.m1)
            mode.app.transposeSolution = mode.solution
            mode.app.setActiveMode(mode.app.calculateTranspose)
        #Reset Button
        if((550 <= event.x <= 6940) and (559 <= event.y <= 619)):
            mode.appStarted()
        #Menu Button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.calculateMode)

    def keyPressed(mode, event):
        #Inputing Number of Rows
        if(mode.inputingRows == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.rowsInput = f'{event.key}'
                mode.rows = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cH = mode.gridHeight / mode.rows
                mode.invalidInputMessage = ''
            #Set back to not selected
            mode.inputingRows = False
            mode.outlineColorR = 'black'

        #Inputing Number of Cols
        if(mode.inputingCols == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.colsInput = f'{event.key}'
                mode.cols = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cW = mode.gridWidth / mode.cols
                mode.invalidInputMessage = ''
            #Set back to not selected
            mode.inputingCols = False
            mode.outlineColorC = 'black'

        #For Negative Inputs
        if(event.key == '-'):
            mode.negativeValue = True

        #Inputing Matrix
        if(mode.inputingMatrix == True and mode.inputingRows == False and mode.inputingCols == False):
            #Only digits allowed
            if(event.key.isdigit()):
                (row,col) = mode.cellClicked
                #Dic allows for multiple digit integers
                value = mode.matrixDigits.get((row,col), '') + event.key 
                mode.matrixDigits[(row,col)] = value
                #Set the row and col of the matrix to the value inputed in the cell
                if(not mode.negativeValue):
                    mode.m1[row][col] = int(value)
                else:
                    mode.m1[row][col] = int(value) * (-1)

                print(mode.m1)
                
            elif(event.key == '-'):
                mode.negativeValue = True
            else:
                mode.invalidInputMessage = 'Invalid Input' 
                
    #Transpose a matrix
    def transpose(mode,m1):
        rows = len(m1)
        cols = len(m1[0])

        mode.app.transposeSteps.extend(formatMatrix(m1))
    
        result = makeResultMatrix(cols, rows)

        newRows = len(result)
        newCols = len(result[0])

        for a in range(newRows):
            for b in range(newCols):
                result[a][b] += m1[b][a]

        mode.app.transposeSteps.append('')
        mode.app.transposeSteps.append('')
        mode.app.transposeSteps.append('Transpose ----->')
        mode.app.transposeSteps.extend(formatMatrix(result))
        return result

    def drawTitleAndInputs(mode,canvas):
        font = 'Verdana 20 bold'
        #Title and row and col input
        canvas.create_text(500,50, text='TRANSPOSE: Input the Number of Rows and Columns', font=font)
        canvas.create_rectangle(400,100,450,150, width = 3, outline=mode.outlineColorR)
        canvas.create_text(425,180, text='ROWS', font=font)
        canvas.create_rectangle(550,100,600,150, width = 3, outline=mode.outlineColorC)
        canvas.create_text(575,180, text='COLS', font=font)
        #Display Inputs
        canvas.create_text(425,125, text=f'{mode.rowsInput}', font='Arial 25', fill='blue')
        canvas.create_text(575,125, text=f'{mode.colsInput}', font='Arial 25', fill='blue')
        #Invalid Input
        canvas.create_text(500,520, text=f'{mode.invalidInputMessage}', font='Arial 25', fill='red')

    def drawGridAndMatrix(mode, canvas):
        #Draw default matrix in default grid
        for row in range(mode.rows):
            for col in range(mode.cols):
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1)

        #Draw Inputed matrix In Grid
        for row in range(len(mode.m1)):
            for col in range(len(mode.m1[0])):
                value = mode.m1[row][col]
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                (cx, cy) = (x1-(mode.cW/2)), (y1-(mode.cH/2))
                if((row,col) == mode.cellClicked):
                    canvas.create_text(cx,cy, text=value, font='Verdana 20', fill = 'blue')
                else:
                    canvas.create_text(cx,cy, text=value, fill = 'black')

    def drawCalculateAndReset(mode,canvas):
        font = 'Verdana 20 bold'
        #Draw Calculate & Reset Button
        canvas.create_rectangle(306,559,450,619, fill='green')
        calculateCx = 306 + 72
        calculateCy = 559 + 30
        canvas.create_text(calculateCx,calculateCy, text='CALCULATE', font=font, fill='white')
        canvas.create_rectangle(550,559,694,619, fill='red')
        resetCx = 550 + 72
        resetCy = 559 + 30
        canvas.create_text(resetCx,resetCy, text='RESET', font=font, fill='white')

    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawTitleAndInputs(canvas)
        mode.drawTitleAndInputs(canvas)
        mode.drawGridAndMatrix(canvas)
        mode.drawCalculateAndReset(canvas)
        mode.drawMenuButton(canvas)
        
class CalculateTranspose(Mode):
    def appStarted(mode):
        mode.solution = mode.app.transposeSolution
        mode.steps = mode.app.transposeSteps
        mode.scrollY = 0

    def mousePressed(mode, event):
        #Clciked on Menu button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.transposeSteps = ['Make the rows the columns and the columns the rows:','','(Use the up and down keys to scroll)','']
            mode.app.setActiveMode(mode.app.calculateMode)
        #Clicked on back button
        if((900 <= event.x <= 1000) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.determinantMode)
            mode.app.transposeSteps = ['Make the rows the columns and the columns the rows:','','(Use the up and down keys to scroll)','']
            DeterminantMode.resetCalculation(mode)

    #CITATION: Up and Down Scrolling algorithm adapted from side scrolling example: http://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#sidescrollerExamples
    def keyPressed(mode, event):
        if(event.key == 'Up'):
            mode.scrollY += 20
        elif(event.key == 'Down'):
            mode.scrollY -= 20

    def drawSteps(mode, canvas):
        Titlefont = 'Verdana 20 bold'
        font = 'Verdana 16'
        spacing = 0
        items = 0
        #For when scrolling
        yPosition = 0
        yPosition += mode.scrollY

        #Go Through the list printing the Steps
        for step in mode.steps:
            items += 1
            spacing += 20
            if(items == 1):
                canvas.create_text(mode.width/2, 40 + yPosition, text = step, font = Titlefont)
            else: 
                canvas.create_text(mode.width/2, 20 + spacing + yPosition, text=step, font = font)
    
    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def drawBackButton(mode,canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(900,650,1000,700,fill = 'orange',outline='orange')
        canvas.create_text(950,675, text = 'BACK',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawSteps(canvas)
        mode.drawBackButton(canvas)
        mode.drawMenuButton(canvas)

class BasisMode(Mode):
    def appStarted(mode):
        #Initializing Values for Grid
        mode.rows = 2
        mode.cols = 2
        mode.marginTop = 223
        mode.margin = 305
        mode.gridWidth = mode.width - 2*mode.margin
        mode.gridHeight = mode.height - 2*mode.marginTop 
        mode.cW = mode.gridWidth / mode.cols
        mode.cH = mode.gridHeight / mode.rows
        #Initialize Matrix Values
        mode.m1 = makeResultMatrix(mode.rows, mode.cols)
        #Initialize Users selecting and typing in screen values
        #Rows
        mode.rowsInput = ''
        mode.inputingRows = False
        mode.outlineColorR = 'black'
        #Cols
        mode.colsInput= ''
        mode.inputingCols = False
        mode.outlineColorC = 'black'
        #Matrix
        mode.cellClicked = (-1,-1)
        mode.inputingMatrix = False
        mode.matrixDigits = dict()
        mode.negativeValue = False
        #Input Error Messages
        mode.invalidInputMessage = ''
        mode.invalidMatrixMessage = ''
        #Initialize Solution
        mode.solution = None

    #This is call by the calculate det class when the back button is pressed
    def resetCalculation(mode):
        mode.appStarted()

    #CITATION (for getCell and getCellBounds): https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCell(mode, x, y):
        col = int((x - mode.margin) / mode.cW)
        row = int((y-mode.marginTop) / mode.cH)
        return (row, col)

    def getCellBounds(mode, row, col):
        x0 = mode.margin + col*mode.cW
        x1 = mode.margin + (col+1)*mode.cW
        y0 = mode.marginTop + row*mode.cH
        y1 = mode.marginTop + (row+1)*mode.cH
        return (x0, y0, x1, y1)
        
    def mousePressed(mode, event):
        #Get the number of rows
        if((400<=event.x<=450) and (100<=event.y<=150)):
            mode.inputingRows = True
            mode.outlineColorR = 'blue'
        #Get the numbet of columns
        if((550<=event.x<=600) and (100<=event.y<=150)):
            mode.inputingCols = True
            mode.outlineColorC = 'blue'
        #If the user clicks inside the grid, initialize inputing matrix
        if((306 <= event.x <= 694) and (220 <= event.y <= 478)):
            (row, col) = mode.getCell(event.x, event.y)
            mode.cellClicked = (row, col)
            mode.inputingMatrix = True
            mode.negativeValue = False
        #Calculate Button
        if((306 <= event.x <= 450) and (559 <= event.y <= 619)):
            mode.solution = mode.basis(mode.m1)
            mode.app.basisSolution = mode.solution
            mode.app.setActiveMode(mode.app.calculateBasis)
        #Reset Button
        if((550 <= event.x <= 6940) and (559 <= event.y <= 619)):
            mode.appStarted()
        #Menu Button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.calculateMode)

    def keyPressed(mode, event):
        #Inputing Number of Rows
        if(mode.inputingRows == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.rowsInput = f'{event.key}'
                mode.rows = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cH = mode.gridHeight / mode.rows
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingRows = False
            mode.outlineColorR = 'black'

        #Inputing Number of Cols
        if(mode.inputingCols == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.colsInput = f'{event.key}'
                mode.cols = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cW = mode.gridWidth / mode.cols
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingCols = False
            mode.outlineColorC = 'black'

        #For Negative Inputs
        if(event.key == '-'):
            mode.negativeValue = True

        #Inputing Matrix
        if(mode.inputingMatrix == True and mode.inputingRows == False and mode.inputingCols == False):
            #Only digits allowed
            if(event.key.isdigit()):
                (row,col) = mode.cellClicked
                #Dic allows for multiple digit integers
                value = mode.matrixDigits.get((row,col), '') + event.key 
                mode.matrixDigits[(row,col)] = value
                #Set the row and col of the matrix to the value inputed in the cell
                if(not mode.negativeValue):
                    mode.m1[row][col] = int(value)
                else:
                    mode.m1[row][col] = int(value) * (-1)

                print(mode.m1)
                mode.invalidInputMessage = ''
                
            elif(event.key == '-'):
                mode.negativeValue = True
            else:
                mode.invalidInputMessage = 'Invalid Input' 
    
    #Helper Function for RREF
    def rowSwap(mode, a1, a2, m1):
        m1[a1],m1[a2] = m1[a2],m1[a1]
        print(type(m1))
        return m1

    #CITATION: Code from https://rosettacode.org/wiki/Reduced_row_echelon_form
    #This code follows the pseudocode in the website and it's adapted to use helper functions and some loops are rewrite. 
    #Find the RREF of a matrix
    #Helper Function for basis
    def RREF(mode, m1):
        rows = len(m1)
        cols = len(m1[0])
        colWeAreIn = 0
        
        for r in range(rows):
            #When we finish looking through the cols in each row
            if (colWeAreIn >= cols):
                mode.app.RREFSteps.append(f'RREF -----> ')
                mode.app.RREFSteps.extend(formatMatrix(m1))
                return m1

            rowWeAreIn = r
            while (m1[rowWeAreIn][colWeAreIn] == 0):
                #Move to the next row to find a non-zero value
                rowWeAreIn += 1
                #If we rech the end of the rows, go back to the top and check in the next column
                if (rowWeAreIn == rows):
                    rowWeAreIn = r
                    colWeAreIn += 1
                    if (cols == colWeAreIn):
                        return m1
            
            #Swap row because ther's no pivot in the current one
            #Row Swap Helper Function
            m1 = mode.rowSwap(rowWeAreIn,r,m1)
            mode.app.basisSteps.append('')
            mode.app.basisSteps.append('Matrix: ----->')
            mode.app.basisSteps.extend(formatMatrix(m1))
            mode.app.basisSteps.append('')

            pivot = m1[r][colWeAreIn]
            mode.app.basisSteps.append(f'Pivot = {pivot}')
            #Divide each value in the row by the pivot
            mode.app.basisSteps.append(f'Divide each value in the row by the pivot: {pivot}')
            mode.app.basisSteps.append(f'Row {m1[r]} / {pivot} ----->')
            rowDivided = []
            for value in m1[r]:
                element = value / pivot
                #The next 4 lines rounds the values of the matrix and displays them better
                element = roundHalfUp(element, 2) 
                #CITATION: Learned about is_integer from:  https://note.nkmk.me/en/python-check-int-float/
                if(element.is_integer()):
                    element = int(element)
                if(int(abs(element) == 0)):
                    element = 0

                rowDivided.append(element)
            m1[r] = rowDivided
            mode.app.basisSteps.extend(formatMatrix(m1))
            mode.app.basisSteps.append('')
            
            #Subtract multiple of one row from another
            for rowWeAreIn in range(rows):
                if (rowWeAreIn != r):
                    pivot = m1[rowWeAreIn][colWeAreIn]
                    mode.app.basisSteps.append('Subtract multiple of one row from another:')
                    mode.app.basisSteps.append(f'Pivot = {pivot}')
                
                    rowReduced = []
                    for (value1,value2) in zip(m1[r],m1[rowWeAreIn]):
                        element = value2 - pivot*value1
                
                        element = roundHalfUp(element, 2) 
                        if(element.is_integer()):
                            element = int(element)
                        if(int(abs(element) == 0)):
                            element = 0
                    
                        rowReduced.append(element)

                    m1[rowWeAreIn] =  rowReduced
                    mode.app.basisSteps.append('Reduced Row ----->')
                    mode.app.basisSteps.extend(formatMatrix(m1))
                    mode.app.basisSteps.append('')

            colWeAreIn += 1

        return m1

    def RREFnoSteps(mode, m1):
        rows = len(m1)
        cols = len(m1[0])
        colWeAreIn = 0
        
        for r in range(rows):
            #When we finish looking through the cols in each row
            if (colWeAreIn >= cols):
                mode.app.RREFSteps.append(f'RREF -----> ')
                mode.app.RREFSteps.extend(formatMatrix(m1))
                return m1

            rowWeAreIn = r
            while (m1[rowWeAreIn][colWeAreIn] == 0):
                #Move to the next row to find a non-zero value
                rowWeAreIn += 1
                #If we rech the end of the rows, go back to the top and check in the next column
                if (rowWeAreIn == rows):
                    rowWeAreIn = r
                    colWeAreIn += 1
                    if (cols == colWeAreIn):
                        return m1
            
            #Swap row because ther's no pivot in the current one
            #Row Swap Helper Function
            m1 = mode.rowSwap(rowWeAreIn,r,m1)
            mode.app.basisSteps.append('')
    
            pivot = m1[r][colWeAreIn]
            #Divide each value in the row by the pivot

            rowDivided = []
            for value in m1[r]:
                element = value / pivot
                #The next 4 lines rounds the values of the matrix and displays them better
                element = roundHalfUp(element, 2) 
                if(element.is_integer()):
                    element = int(element)
                if(int(abs(element) == 0)):
                    element = 0

                rowDivided.append(element)
            m1[r] = rowDivided
            
            #Subtract multiple of one row from another
            for rowWeAreIn in range(rows):
                if (rowWeAreIn != r):
                    pivot = m1[rowWeAreIn][colWeAreIn]
                
                    rowReduced = []
                    for (value1,value2) in zip(m1[r],m1[rowWeAreIn]):
                        element = value2 - pivot*value1
                
                        element = roundHalfUp(element, 2) 
                        if(element.is_integer()):
                            element = int(element)
                        if(int(abs(element) == 0)):
                            element = 0
                    
                        rowReduced.append(element)

                    m1[rowWeAreIn] =  rowReduced

            colWeAreIn += 1

        return m1

    #Helper Function for column space and left-null space
    #Transpose a matrix
    #Transpose a matrix
    def transpose(mode,m1):
        rows = len(m1)
        cols = len(m1[0])

        mode.app.basisSteps.extend(formatMatrix(m1))
    
        result = makeResultMatrix(cols, rows)

        newRows = len(result)
        newCols = len(result[0])

        for a in range(newRows):
            for b in range(newCols):
                result[a][b] += m1[b][a]

        mode.app.basisSteps.append('')
        mode.app.basisSteps.append('Transpose ----->')
        mode.app.basisSteps.extend(formatMatrix(result))
        return result

    #Helper Function for Nullspace
    def identityMatrix(mode,rows,cols):
        identity = makeResultMatrix(rows,cols)

        for a in range(rows):
            for b in range(cols):
                if(a == b):
                    identity[a][b] = 1
                else:
                    identity[a][b] = 0

        return identity

    def rowSpace(mode,rref,original):
        mode.app.basisSteps.append('Look at the Non-Zero Rows in the matrix in RREF')
        mode.app.basisSteps.append('Find the index of these rows in the original matrix')
        rows = len(rref)
        cols = len(rref[0])
        
        nonZeroRows = []
        rowSpace = []
        zeroRow = [0]*cols

        for row in range(rows):
            if(rref[row] != zeroRow):
                nonZeroRows.append(row)

        for row in nonZeroRows:
            rowSpace.append(original[row])

        return rowSpace

    def columnSpace(mode,rref,original):

        mode.app.basisSteps.append('Transpose the original matrix')
        original = mode.transpose(original)

        mode.app.basisSteps.append('Look at the Non-Zero Rows in the matrix in RREF')
        mode.app.basisSteps.append('Find the index of these rows in the original matrix')

        rows = len(rref)
        cols = len(rref[0])
        
        nonZeroRows = []
        columnSpace = []
        zeroRow = [0]*cols

        for row in range(rows):
            if(rref[row] != zeroRow):
                nonZeroRows.append(row)

        for row in nonZeroRows:
            columnSpace.append(original[row])

        return columnSpace

    #Finding the Basis for the null Space
    def nullSpace(mode,rref):
        
        rows = len(rref)
        cols = len(rref[0])
        
        freeRowsIndex = []
        freeRows = []
        zeroRow = [0]*cols

        nullSpace = []
    
        for row in range(rows):
            if(rref[row] != zeroRow):
                freeRowsIndex.append(row)

        #Finding the free Rows through indexing
        if(len(freeRowsIndex) == rows):
            startOfFreeRows = rows
            for row in range(rows):
                 item = rref[row][startOfFreeRows:]
                 freeRows.append(item)

            mode.app.basisSteps.append('Find the free columns:')
            mode.app.basisSteps.extend(formatMatrix(freeRows))
            
            #Change the sign of the elements in the free cols
            for a in range(len(freeRows)):
                for b in range(len(freeRows[0])):
                    freeRows[a][b] = freeRows[a][b] * (-1)

            mode.app.basisSteps.append('Multiply the elements by (-1):')
            mode.app.basisSteps.extend(formatMatrix(freeRows))

            nullSpace = freeRows

        else:
            startOfFreeRows = len(freeRowsIndex)
            for row in freeRowsIndex:
                 item = rref[row][startOfFreeRows:]
                 freeRows.append(item)

            mode.app.basisSteps.append('Find the free columns:')
            mode.app.basisSteps.extend(formatMatrix(freeRows))

            #Find the Identity Matrix to Complete the columns
            sizeOfId = cols - len(freeRowsIndex)
            idMatrix = mode.identityMatrix(sizeOfId,sizeOfId)

            print('Identity add on', idMatrix)


            #Change the sign of the elements in the free cols
            for a in range(len(freeRows)):
                for b in range(len(freeRows[0])):
                    freeRows[a][b] = freeRows[a][b] * (-1)

            mode.app.basisSteps.append('Multiply the elements by (-1):')
            mode.app.basisSteps.extend(formatMatrix(freeRows))

            for element in idMatrix:
                freeRows.append(element)

            mode.app.basisSteps.append('Add the Identity Matrix to complete the columns:')
            mode.app.basisSteps.extend(formatMatrix(freeRows))

            nullSpace = freeRows
        
        if(len(nullSpace[0]) == 0):
            nullSpace = ['No Basis for the Null Space']

        return nullSpace

    #Finding the Basis for the LEFT null Space
    def leftNullSpace(mode,original):
        #Tranpose the Matrix before begining
        mode.app.basisSteps.append('Find the RREF of the Transpose of the Matrix')
        original = mode.transpose(original)
        rref = mode.RREFnoSteps(original)

        rows = len(rref)
        cols = len(rref[0])
        
        freeRowsIndex = []
        freeRows = []
        zeroRow = [0]*cols

        leftNullSpace = []
    
        for row in range(rows):
            if(rref[row] != zeroRow):
                freeRowsIndex.append(row)

        #Finding the free Rows through indexing
        if(len(freeRowsIndex) == rows):
            startOfFreeRows = rows
            for row in range(rows):
                 item = rref[row][startOfFreeRows:]
                 freeRows.append(item)

            mode.app.basisSteps.append('Find the free columns:')
            mode.app.basisSteps.extend(formatMatrix(freeRows))
            
            #Change the sign of the elements in the free cols
            for a in range(len(freeRows)):
                for b in range(len(freeRows[0])):
                    freeRows[a][b] = freeRows[a][b] * (-1)

            mode.app.basisSteps.append('Multiply the elements by (-1):')
            mode.app.basisSteps.extend(formatMatrix(freeRows))

            leftNullSpace = freeRows

        else:
            startOfFreeRows = len(freeRowsIndex)
            for row in freeRowsIndex:
                 item = rref[row][startOfFreeRows:]
                 freeRows.append(item)

            mode.app.basisSteps.append('Find the free columns:')
            mode.app.basisSteps.extend(formatMatrix(freeRows))

            #Find the Identity Matrix to Complete the columns
            sizeOfId = cols - len(freeRowsIndex)
            idMatrix = mode.identityMatrix(sizeOfId,sizeOfId)

            #Change the sign of the elements in the free cols
            for a in range(len(freeRows)):
                for b in range(len(freeRows[0])):
                    freeRows[a][b] = freeRows[a][b] * (-1)

            mode.app.basisSteps.append('Multiply the elements by (-1):')
            mode.app.basisSteps.extend(formatMatrix(freeRows))

            for element in idMatrix:
                freeRows.append(element)

            mode.app.basisSteps.append('Add the Identity Matrix to complete the columns:')
            mode.app.basisSteps.extend(formatMatrix(freeRows))

            leftNullSpace = freeRows


        if(len(leftNullSpace[0]) == 0):
            leftNullSpace = ['No Basis for the Left Null Space']

        return leftNullSpace

    #Basis for four fundamental subspaces
    def basis(mode, m1):
        originalM = copy.deepcopy(m1)
        rrefM = mode.RREF(m1)
        mode.app.basisSteps.append('Use the RREF Matrix to find the four Fundamental Subspaces')
        mode.app.basisSteps.append('Matrix ----->')
        mode.app.basisSteps.extend(formatMatrix(rrefM))
        mode.app.basisSteps.append('')

        mode.app.basisSteps.append('Row Space Basis:')
        rowSpaceBasis = mode.rowSpace(rrefM, originalM)
        mode.app.basisSteps.append('Basis ----->')
        mode.app.basisSteps.extend(formatMatrix(rowSpaceBasis))
        mode.app.basisSteps.append('')

        mode.app.basisSteps.append('Column Space Basis:')
        columnSpaceBasis = mode.columnSpace(rrefM, originalM)
        mode.app.basisSteps.append('Basis ----->')
        mode.app.basisSteps.extend(formatMatrix(columnSpaceBasis))
        mode.app.basisSteps.append('')

        mode.app.basisSteps.append('Null-Space Basis:')
        nullSpaceBasis = mode.nullSpace(rrefM)
        mode.app.basisSteps.append('Basis ----->')
        mode.app.basisSteps.extend(formatMatrix(nullSpaceBasis))
        mode.app.basisSteps.append('')

        mode.app.basisSteps.append('Left-Null Space Basis:')
        leftNullSpaceBasis = mode.leftNullSpace(originalM)
        mode.app.basisSteps.append('Basis ----->')
        mode.app.basisSteps.extend(formatMatrix(leftNullSpaceBasis))
        mode.app.basisSteps.append('')

        
    def drawTitleAndInputs(mode,canvas):
        font = 'Verdana 20 bold'
        #Title and row and col input
        canvas.create_text(500,50, text='BASIS: Input the Number of Rows and Columns', font=font)
        canvas.create_rectangle(400,100,450,150, width = 3, outline=mode.outlineColorR)
        canvas.create_text(425,180, text='ROWS', font=font)
        canvas.create_rectangle(550,100,600,150, width = 3, outline=mode.outlineColorC)
        canvas.create_text(575,180, text='COLS', font=font)
        #Display Inputs
        canvas.create_text(425,125, text=f'{mode.rowsInput}', font='Arial 25', fill='blue')
        canvas.create_text(575,125, text=f'{mode.colsInput}', font='Arial 25', fill='blue')
        #Invalid Input
        canvas.create_text(500,520, text=f'{mode.invalidInputMessage}', font='Arial 25', fill='red')

    def drawGridAndMatrix(mode, canvas):
        #Draw default matrix in default grid
        for row in range(mode.rows):
            for col in range(mode.cols):
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1)

        #Draw Inputed matrix In Grid
        for row in range(len(mode.m1)):
            for col in range(len(mode.m1[0])):
                value = mode.m1[row][col]
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                (cx, cy) = (x1-(mode.cW/2)), (y1-(mode.cH/2))
                if((row,col) == mode.cellClicked):
                    canvas.create_text(cx,cy, text=value, font='Verdana 20', fill = 'blue')
                else:
                    canvas.create_text(cx,cy, text=value, fill = 'black')

    def drawCalculateAndReset(mode,canvas):
        font = 'Verdana 20 bold'
        #Draw Calculate & Reset Button
        canvas.create_rectangle(306,559,450,619, fill='green')
        calculateCx = 306 + 72
        calculateCy = 559 + 30
        canvas.create_text(calculateCx,calculateCy, text='CALCULATE', font=font, fill='white')
        canvas.create_rectangle(550,559,694,619, fill='red')
        resetCx = 550 + 72
        resetCy = 559 + 30
        canvas.create_text(resetCx,resetCy, text='RESET', font=font, fill='white')

        #Invalid Matrix 
        canvas.create_text(500,520, text=f'{mode.invalidMatrixMessage}', font='Arial 25', fill='red')

    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawTitleAndInputs(canvas)
        mode.drawTitleAndInputs(canvas)
        mode.drawGridAndMatrix(canvas)
        mode.drawCalculateAndReset(canvas)
        mode.drawMenuButton(canvas)

class CalculateBasis(Mode):
    def appStarted(mode):
        mode.solution = mode.app.basisSolution
        mode.steps = mode.app.basisSteps
        mode.scrollY = 0

    def mousePressed(mode, event):
        #Clciked on Menu button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.basisSteps = ['Find the RREF to find the basis for the four fundamental subspaces','','(Use the up and down keys to scroll)','']
            mode.app.setActiveMode(mode.app.calculateMode)
        #Clicked on back button
        if((900 <= event.x <= 1000) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.basisMode)
            mode.app.basisSteps = ['Find the RREF to find the basis for the four fundamental subspaces','','(Use the up and down keys to scroll)','']
            BasisMode.resetCalculation(mode)

    #CITATION: Up and Down Scrolling algorithm adapted from side scrolling example: http://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#sidescrollerExamples
    def keyPressed(mode, event):
        if(event.key == 'Up'):
            mode.scrollY += 20
        elif(event.key == 'Down'):
            mode.scrollY -= 20

    def drawSteps(mode, canvas):
        Titlefont = 'Verdana 20 bold'
        font = 'Verdana 16'
        spacing = 0
        items = 0
        #For when scrolling
        yPosition = 0
        yPosition += mode.scrollY

        #Go Through the list printing the Steps
        for step in mode.steps:
            items += 1
            spacing += 20
            
            if(items == 1):
                canvas.create_text(mode.width/2, 40 + yPosition, text = step, font = Titlefont)
            elif(step == 'Row Space Basis:'):
                canvas.create_text(mode.width/2, 20 + spacing + yPosition, text = step, font = 'Verdana 20 bold')
            elif(step == 'Column Space Basis:'):
                canvas.create_text(mode.width/2, 20 + spacing + yPosition, text = step, font = 'Verdana 20 bold')
            elif(step == 'Null-Space Basis:'):
                canvas.create_text(mode.width/2, 20 + spacing + yPosition, text = step, font = 'Verdana 20 bold')
            elif(step == 'Left-Null Space Basis:'):
                canvas.create_text(mode.width/2, 20 + spacing + yPosition, text = step, font = 'Verdana 20 bold')
            else: 
                canvas.create_text(mode.width/2, 20 + spacing + yPosition, text=step, font = font)
    
    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def drawBackButton(mode,canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(900,650,1000,700,fill = 'orange',outline='orange')
        canvas.create_text(950,675, text = 'BACK',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawSteps(canvas)
        mode.drawBackButton(canvas)
        mode.drawMenuButton(canvas)

class DeterminantMode(Mode):

    def appStarted(mode):
        #Initializing Values for Grid
        mode.rows = 2
        mode.cols = 2
        mode.marginTop = 223
        mode.margin = 305
        mode.gridWidth = mode.width - 2*mode.margin
        mode.gridHeight = mode.height - 2*mode.marginTop 
        mode.cW = mode.gridWidth / mode.cols
        mode.cH = mode.gridHeight / mode.rows
        #Initialize Matrix Values
        mode.m1 = makeResultMatrix(mode.rows, mode.cols)
        #Initialize Users selecting and typing in screen values
        #Rows
        mode.rowsInput = ''
        mode.inputingRows = False
        mode.outlineColorR = 'black'
        #Cols
        mode.colsInput= ''
        mode.inputingCols = False
        mode.outlineColorC = 'black'
        #Matrix
        mode.cellClicked = (-1,-1)
        mode.inputingMatrix = False
        mode.matrixDigits = dict()
        mode.negativeValue = False
        #Input Error Messages
        mode.invalidInputMessage = ''
        mode.invalidMatrixMessage = ''
        #Initialize Solution
        mode.solution = None

    #This is call by the calculate det class when the back button is pressed
    def resetCalculation(mode):
        mode.appStarted()

    #CITATION (for getCell and getCellBounds): https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCell(mode, x, y):
        col = int((x - mode.margin) / mode.cW)
        row = int((y-mode.marginTop) / mode.cH)
        return (row, col)

    def getCellBounds(mode, row, col):
        x0 = mode.margin + col*mode.cW
        x1 = mode.margin + (col+1)*mode.cW
        y0 = mode.marginTop + row*mode.cH
        y1 = mode.marginTop + (row+1)*mode.cH
        return (x0, y0, x1, y1)
        
    def mousePressed(mode, event):
        #Get the number of rows
        if((400<=event.x<=450) and (100<=event.y<=150)):
            mode.inputingRows = True
            mode.outlineColorR = 'blue'
        #Get the numbet of columns
        if((550<=event.x<=600) and (100<=event.y<=150)):
            mode.inputingCols = True
            mode.outlineColorC = 'blue'
        #If the user clicks inside the grid, initialize inputing matrix
        if((306 <= event.x <= 694) and (220 <= event.y <= 478)):
            (row, col) = mode.getCell(event.x, event.y)
            mode.cellClicked = (row, col)
            mode.inputingMatrix = True
            mode.negativeValue = False
        #Calculate Button
        if((306 <= event.x <= 450) and (559 <= event.y <= 619)):
            #Non-Square Matrix
            if(mode.cols != mode.rows):
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = 'The determinant only exists for square matrices!'
            #Use inputed matrix to call the determinant function
            else:
                mode.solution = mode.determinant(mode.m1)
                mode.app.detSolution = mode.solution
                mode.app.setActiveMode(mode.app.calculateDet)
        #Reset Button
        if((550 <= event.x <= 6940) and (559 <= event.y <= 619)):
            mode.appStarted()
        #Menu Button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.calculateMode)

    def keyPressed(mode, event):
        #Inputing Number of Rows
        if(mode.inputingRows == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.rowsInput = f'{event.key}'
                mode.rows = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cH = mode.gridHeight / mode.rows
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingRows = False
            mode.outlineColorR = 'black'

        #Inputing Number of Cols
        if(mode.inputingCols == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.colsInput = f'{event.key}'
                mode.cols = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cW = mode.gridWidth / mode.cols
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingCols = False
            mode.outlineColorC = 'black'

        #For Negative Inputs
        if(event.key == '-'):
            mode.negativeValue = True

        #Inputing Matrix
        if(mode.inputingMatrix == True and mode.inputingRows == False and mode.inputingCols == False):
            #Only digits allowed
            if(event.key.isdigit()):
                (row,col) = mode.cellClicked
                #Dic allows for multiple digit integers
                value = mode.matrixDigits.get((row,col), '') + event.key 
                mode.matrixDigits[(row,col)] = value
                #Set the row and col of the matrix to the value inputed in the cell
                if(not mode.negativeValue):
                    mode.m1[row][col] = int(value)
                else:
                    mode.m1[row][col] = int(value) * (-1)

                
                print(mode.m1)
                mode.invalidInputMessage = ''
                
            elif(event.key == '-'):
                mode.negativeValue = True
            else:
                mode.invalidInputMessage = 'Invalid Input' 
                
    #Determinant of a Matrix
    def determinant(mode, m1):
        mode.app.detSteps.append(f'Matrix ----->')
        mode.app.detSteps.extend(formatMatrix(m1))
        mode.app.detSteps.append('')
        
        #Single element matrix
        if(len(m1)==1 and len(m1[0])==1):
            mode.app.detSteps.append('')
            mode.app.detSteps.extend(formatMatrix(m1))
            mode.app.detSteps.append(f'DET = {m1[0][0]}')
            return m1[0][0]

        rows = len(m1)
        cols = len(m1[0])

        #Base case: 2*2 Matrix
        if(len(m1)==2):
            det = (m1[0][0]*m1[1][1]) - (m1[0][1]*m1[1][0])
            mode.app.detSteps.append(f'DET = ({m1[0][0]}*{m1[1][1]}) - ({m1[0][1]}*{m1[1][0]}) = {det}')
        
            return det
        else:
            det = 0
            #Iterate through the elements in the first row
            #The row is 0, what's changing is the columns
            for b in range(cols):
                subMatrix = minorMatrix(m1,0,b)
                mode.app.detSteps.append('')
                mode.app.detSteps.append(f'For value {m1[0][b]} in Row 1:')
                mode.app.detSteps.append('Find the Determinant of the Sub-Matrix')
                intermediateStep = m1[0][b] * (-1)**(b) * mode.determinant(subMatrix)

                mode.app.detSteps.append(f'C_({1},{b+1}) = (-1)^({1}+{b+1}) * {m1[0][b]} * DET(Sub-Matrix)')
                mode.app.detSteps.append(f'C_({1},{b+1}) = {intermediateStep}')
                mode.app.detSteps.append('')
                det += intermediateStep
                
            mode.app.detSteps.append('Sum All the cofactors:')
            mode.app.detSteps.append('DET -----> ')
            mode.app.detSteps.append(f'{det}')
            return det

    def drawTitleAndInputs(mode,canvas):
        font = 'Verdana 20 bold'
        #Title and row and col input
        canvas.create_text(500,50, text='DETERMINANT: Input the Number of Rows and Columns', font=font)
        canvas.create_rectangle(400,100,450,150, width = 3, outline=mode.outlineColorR)
        canvas.create_text(425,180, text='ROWS', font=font)
        canvas.create_rectangle(550,100,600,150, width = 3, outline=mode.outlineColorC)
        canvas.create_text(575,180, text='COLS', font=font)
        #Display Inputs
        canvas.create_text(425,125, text=f'{mode.rowsInput}', font='Arial 25', fill='blue')
        canvas.create_text(575,125, text=f'{mode.colsInput}', font='Arial 25', fill='blue')
        #Invalid Input
        canvas.create_text(500,520, text=f'{mode.invalidInputMessage}', font='Arial 25', fill='red')

    def drawGridAndMatrix(mode, canvas):
        #Draw default matrix in default grid
        for row in range(mode.rows):
            for col in range(mode.cols):
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1)

        #Draw Inputed matrix In Grid
        for row in range(len(mode.m1)):
            for col in range(len(mode.m1[0])):
                value = mode.m1[row][col]
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                (cx, cy) = (x1-(mode.cW/2)), (y1-(mode.cH/2))
                if((row,col) == mode.cellClicked):
                    canvas.create_text(cx,cy, text=value, font='Verdana 20', fill = 'blue')
                else:
                    canvas.create_text(cx,cy, text=value, fill = 'black')

    def drawCalculateAndReset(mode,canvas):
        font = 'Verdana 20 bold'
        #Draw Calculate & Reset Button
        canvas.create_rectangle(306,559,450,619, fill='green')
        calculateCx = 306 + 72
        calculateCy = 559 + 30
        canvas.create_text(calculateCx,calculateCy, text='CALCULATE', font=font, fill='white')
        canvas.create_rectangle(550,559,694,619, fill='red')
        resetCx = 550 + 72
        resetCy = 559 + 30
        canvas.create_text(resetCx,resetCy, text='RESET', font=font, fill='white')

        #Invalid Matrix 
        canvas.create_text(500,520, text=f'{mode.invalidMatrixMessage}', font='Arial 25', fill='red')

    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawTitleAndInputs(canvas)
        mode.drawTitleAndInputs(canvas)
        mode.drawGridAndMatrix(canvas)
        mode.drawCalculateAndReset(canvas)
        mode.drawMenuButton(canvas)
        
class CalculateDet(Mode):

    def appStarted(mode):
        mode.solution = mode.app.detSolution
        mode.steps = mode.app.detSteps
        mode.scrollY = 0

    def mousePressed(mode, event):
        #Clciked on Menu button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.detSteps = ['Finding the determinant by summing the cofactors of row 1:','','(Use the up and down keys to scroll)','']
            mode.app.setActiveMode(mode.app.calculateMode)
        #Clicked on back button
        if((900 <= event.x <= 1000) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.determinantMode)
            mode.app.detSteps = ['Finding the determinant by summing the cofactors of row 1:','','(Use the up and down keys to scroll)','']
            DeterminantMode.resetCalculation(mode)

    #CITATION: Up and Down Scrolling algorithm adapted from side scrolling example: http://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#sidescrollerExamples
    def keyPressed(mode, event):
        if(event.key == 'Up'):
            mode.scrollY += 20
        elif(event.key == 'Down'):
            mode.scrollY -= 20

    def drawSteps(mode, canvas):
        Titlefont = 'Verdana 20 bold'
        font = 'Verdana 16'
        spacing = 0
        items = 0
        #For when scrolling
        yPosition = 0
        yPosition += mode.scrollY

        #Go Through the list printing the Steps
        for step in mode.steps:
            items += 1
            spacing += 20
            if(items == 1):
                canvas.create_text(mode.width/2, 40 + yPosition, text = step, font = Titlefont)
            elif(items == len(mode.steps)):
                canvas.create_text(mode.width/2, 40 + spacing + yPosition, text = step, font = font, fill = 'green')
            else: 
                canvas.create_text(mode.width/2, 20 + spacing + yPosition, text=step, font = font)
    
    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def drawBackButton(mode,canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(900,650,1000,700,fill = 'orange',outline='orange')
        canvas.create_text(950,675, text = 'BACK',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawSteps(canvas)
        mode.drawBackButton(canvas)
        mode.drawMenuButton(canvas)
   
class VisualizeMode(Mode):
    def appStarted(mode):
        #Initializing Values for Grid
        mode.rows = 2
        mode.cols = 2
        mode.marginTop = 223
        mode.margin = 305
        mode.gridWidth = mode.width - 2*mode.margin
        mode.gridHeight = mode.height - 2*mode.marginTop 
        mode.cW = mode.gridWidth / mode.cols
        mode.cH = mode.gridHeight / mode.rows
        #Initialize Matrix Values
        mode.m1 = makeResultMatrix(mode.rows, mode.cols)
        #Initialize Users selecting and typing in screen values
        #Rows
        mode.rowsInput = ''
        mode.inputingRows = False
        mode.outlineColorR = 'black'
        #Cols
        mode.colsInput= ''
        mode.inputingCols = False
        mode.outlineColorC = 'black'
        #Matrix
        mode.cellClicked = (-1,-1)
        mode.inputingMatrix = False
        mode.matrixDigits = dict()
        mode.negativeValue = False
        #Input Error Messages
        mode.invalidInputMessage = ''
        mode.invalidMatrixMessage = ''
        #Initialize Solution
        mode.solution = None
        mode.diagonalLegal = True

    #This is call by the calculate det class when the back button is pressed
    def resetCalculation(mode):
        mode.appStarted()

    #CITATION (for getCell and getCellBounds): https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCell(mode, x, y):
        col = int((x - mode.margin) / mode.cW)
        row = int((y-mode.marginTop) / mode.cH)
        return (row, col)

    def getCellBounds(mode, row, col):
        x0 = mode.margin + col*mode.cW
        x1 = mode.margin + (col+1)*mode.cW
        y0 = mode.marginTop + row*mode.cH
        y1 = mode.marginTop + (row+1)*mode.cH
        return (x0, y0, x1, y1)
        
    def mousePressed(mode, event):
        #Get the number of rows
        if((400<=event.x<=450) and (100<=event.y<=150)):
            mode.inputingRows = True
            mode.outlineColorR = 'blue'
        #Get the numbet of columns
        if((550<=event.x<=600) and (100<=event.y<=150)):
            mode.inputingCols = True
            mode.outlineColorC = 'blue'
        #If the user clicks inside the grid, initialize inputing matrix
        if((306 <= event.x <= 694) and (220 <= event.y <= 478)):
            (row, col) = mode.getCell(event.x, event.y)
            mode.cellClicked = (row, col)
            mode.inputingMatrix = True
            mode.negativeValue = False
        #Calculate Button
        if((306 <= event.x <= 450) and (559 <= event.y <= 619)):
            if(mode.cols != mode.rows):
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = 'An adjacency matrix must be a square matrix!'
            else:
                #Check if Diagonal is all zeroes
                for row in range(mode.rows):
                    if(mode.m1[row][row] != 0):
                        mode.diagonalLegal = False

                if(not mode.diagonalLegal):
                    mode.invalidMatrixMessage = 'To graph, the matrix must have zeroes in the diagonal!'
                else:
                    mode.solution = mode.m1
                    mode.app.visualizeSolution = mode.solution
                    mode.app.setActiveMode(mode.app.calculateVisualize)
        #Reset Button
        if((550 <= event.x <= 6940) and (559 <= event.y <= 619)):
            mode.appStarted()
        #Menu Button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.setActiveMode(mode.app.calculateMode)

    def keyPressed(mode, event):
        #Inputing Number of Rows
        if(mode.inputingRows == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.rowsInput = f'{event.key}'
                mode.rows = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cH = mode.gridHeight / mode.rows
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingRows = False
            mode.outlineColorR = 'black'

        #Inputing Number of Cols
        if(mode.inputingCols == True):
            mode.inputingMatrix = False
            if(not event.key.isdigit() or event.key == '0'):
                mode.invalidMatrixMessage = ''
                mode.invalidInputMessage = 'Invalid Input'
            else:
                mode.colsInput = f'{event.key}'
                mode.cols = int(event.key)
                mode.m1 = makeResultMatrix(mode.rows,mode.cols)
                mode.cW = mode.gridWidth / mode.cols
                mode.invalidInputMessage = ''
                mode.invalidMatrixMessage = ''
            #Set back to not selected
            mode.inputingCols = False
            mode.outlineColorC = 'black'

        #For Negative Inputs
        if(event.key == '-'):
            mode.negativeValue = True

        #Inputing Matrix
        if(mode.inputingMatrix == True and mode.inputingRows == False and mode.inputingCols == False):
            #Only digits allowed
            if(event.key == '0' or event.key == '1'):
                (row,col) = mode.cellClicked
                #Dic allows for multiple digit integers
                if(not mode.negativeValue):
                    value = event.key 
                    #Set the row and col of the matrix to the value inputed in the cell
                    mode.m1[row][col] = int(value)
                else:
                    value = event.key 
                    #Set the row and col of the matrix to the value inputed in the cell
                    mode.m1[row][col] = int(value) * (-1)
                print(mode.m1)
                mode.invalidInputMessage = ''
            elif(event.key == '-'):
                mode.negativeValue = True
            else:
                mode.invalidInputMessage = 'Invalid Input: Values can only be 0s or 1s' 

    def drawTitleAndInputs(mode,canvas):
        font = 'Verdana 20 bold'
        #Title and row and col input
        canvas.create_text(500,50, text='DIRECTED GRAPH: Input the Number of Rows and Columns of the adjacency matrix', font=font)
        canvas.create_rectangle(400,100,450,150, width = 3, outline=mode.outlineColorR)
        canvas.create_text(425,180, text='ROWS', font=font)
        canvas.create_rectangle(550,100,600,150, width = 3, outline=mode.outlineColorC)
        canvas.create_text(575,180, text='COLS', font=font)
        #Display Inputs
        canvas.create_text(425,125, text=f'{mode.rowsInput}', font='Arial 25', fill='blue')
        canvas.create_text(575,125, text=f'{mode.colsInput}', font='Arial 25', fill='blue')
        #Invalid Input
        canvas.create_text(500,520, text=f'{mode.invalidInputMessage}', font='Arial 25', fill='red')

    def drawGridAndMatrix(mode, canvas):
        #Draw default matrix in default grid
        for row in range(mode.rows):
            for col in range(mode.cols):
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1)

        #Draw Inputed matrix In Grid
        for row in range(len(mode.m1)):
            for col in range(len(mode.m1[0])):
                value = mode.m1[row][col]
                x0, y0, x1, y1 = mode.getCellBounds(row, col)
                (cx, cy) = (x1-(mode.cW/2)), (y1-(mode.cH/2))
                if((row,col) == mode.cellClicked):
                    canvas.create_text(cx,cy, text=value, font='Verdana 20', fill = 'blue')
                else:
                    canvas.create_text(cx,cy, text=value, fill = 'black')

    def drawCalculateAndReset(mode,canvas):
        font = 'Verdana 20 bold'
        #Draw Calculate & Reset Button
        canvas.create_rectangle(306,559,450,619, fill='green')
        calculateCx = 306 + 72
        calculateCy = 559 + 30
        canvas.create_text(calculateCx,calculateCy, text='CALCULATE', font=font, fill='white')
        canvas.create_rectangle(550,559,694,619, fill='red')
        resetCx = 550 + 72
        resetCy = 559 + 30
        canvas.create_text(resetCx,resetCy, text='RESET', font=font, fill='white')

        #Invalid Matrix 
        canvas.create_text(500,520, text=f'{mode.invalidMatrixMessage}', font='Arial 25', fill='red')

    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawTitleAndInputs(canvas)
        mode.drawTitleAndInputs(canvas)
        mode.drawGridAndMatrix(canvas)
        mode.drawCalculateAndReset(canvas)
        mode.drawMenuButton(canvas)

class CalculateVisualize(Mode):
    def appStarted(mode):
        mode.solution = mode.app.visualizeSolution
        mode.numberOfNodes = len(mode.solution)
        mode.arcs = []
        mode.nodesCenters = []
        mode.nodesRadius = 20
        mode.nodesColors = ['red','yellow','orange','green','purple','cyan','tan','pink','blue','gray']
        mode.steps = mode.app.visualizeSteps
        mode.scrollY = 0
        mode.getNodesCenters()
        mode.getArcs()
        print(mode.arcs)

    def getArcs(mode):
        for node1 in range(len(mode.solution)):
            for node2 in range(len(mode.solution[0])):
                if(mode.solution[node1][node2] != 0):
                    mode.arcs.append((node1,node2))

    def getNodesCenters(mode):
        xStartingPosition = 100
        xIncrement = 400

        yStartingPosition = 200
        yIncrement = 200
        
        for n in range(mode.numberOfNodes):
            if(n == 0):
                cx = xStartingPosition
                cy = yStartingPosition
            elif(n == 1):
                cx = xStartingPosition + xIncrement
                cy = yStartingPosition
            elif(n == 2):
                cx = xStartingPosition + xIncrement/2
                cy = yStartingPosition + yIncrement
            elif(n == 3):
                cx = xStartingPosition 
                cy = yStartingPosition + yIncrement*(2)
            elif(n == 4):
                cx = xStartingPosition + xIncrement
                cy = yStartingPosition + yIncrement*(2)
            elif(n == 5):
                cx = xStartingPosition + xIncrement*(2)
                cy = yStartingPosition 
            elif(n == 6):
                cx = xStartingPosition + 600
                cy = yStartingPosition + yIncrement
            elif(n == 7):
                cx = xStartingPosition + xIncrement*(2)
                cy = yStartingPosition + yIncrement
            elif(n == 8):
                cx = xStartingPosition + xIncrement*(2)
                cy = yStartingPosition + yIncrement*(2)

            mode.nodesCenters.append((cx,cy))

    def mousePressed(mode, event):
        #Clciked on Menu button
        if((0 <= event.x <= 100) and (650 <= event.y <= 700)):
            mode.app.visualizeSteps = ['Directed Graph of Inputed Matrix:']
            mode.app.setActiveMode(mode.app.calculateMode)
        #Clicked on back button
        if((900 <= event.x <= 1000) and (650 <= event.y <= 700)):
            mode.nodesCenters = []
            mode.app.setActiveMode(mode.app.visualizeMode)
            mode.app.visualizeSteps = ['Directed Graph of Inputed Matrix:']
            VisualizeMode.resetCalculation(mode)

    def drawTitle(mode, canvas):
    
        Titlefont = 'Verdana 20 bold'
        font = 'Verdana 16'
    
        for step in mode.app.visualizeSteps:
                canvas.create_text(mode.width/2, 40, text = step, font = Titlefont)


    def drawNodes(mode, canvas):
    
        r = mode.nodesRadius
        colorIndex = -1
        nodeIndex = -1
        for (cx,cy) in mode.nodesCenters:
            colorIndex += 1
            nodeIndex += 1

            color = mode.nodesColors[colorIndex]

            canvas.create_rectangle(cx-r,cy-r,cx+r,cy+r, fill=color)
            canvas.create_text(cx,cy-30, text=nodeIndex, fill='black',font='Arial 20 bold')

    def drawArcs(mode, canvas):
        for (node1,node2) in mode.arcs:
            x1, y1 = mode.nodesCenters[node1]
            x2, y2 = mode.nodesCenters[node2]
            canvas.create_line(x1,y1,x2,y2,arrow='first',width=2)
    
    
    def drawMenuButton(mode, canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(0,650,100,700,fill = 'blue',outline='blue')
        canvas.create_text(50,675, text = 'MENU',font=font,fill='white')

    def drawBackButton(mode,canvas):
        font = 'Verdana 20 bold'
        canvas.create_rectangle(900,650,1000,700,fill = 'orange',outline='orange')
        canvas.create_text(950,675, text = 'BACK',font=font,fill='white')

    def redrawAll(mode, canvas):
        mode.drawTitle(canvas)
        mode.drawNodes(canvas)
        mode.drawArcs(canvas)
        mode.drawBackButton(canvas)
        mode.drawMenuButton(canvas)

class MyModalApp(ModalApp):
    def appStarted(app):
        #Mode Screens
        app.homeScreenMode = HomeScreenMode()
        app.calculateMode = CalculateMode()
        app.RREFMode = RREFMode()
        app.multiplicationMode = MultiplicationMode()
        app.additionMode = AdditionMode()
        app.inverseMode = InverseMode()
        app.transposeMode = TransposeMode()
        app.basisMode = BasisMode()
        app.determinantMode = DeterminantMode()
        app.visualizeMode = VisualizeMode()
        app.setActiveMode(app.homeScreenMode)
        
        #Calculate Screens for each mode
        app.calculateDet = CalculateDet()
        app.calculateInverse = CalculateInverse()
        app.calculateMultiplication = CalculateMultiplication()
        app.calculateAddition = CalculateAddition()
        app.calculateTranspose = CalculateTranspose()
        app.calculateVisualize = CalculateVisualize()
        app.calculateRREF = CalculateRREF()
        App.calculateBasis = CalculateBasis()

        #Solution values for each mode
        app.detSolution = []
        app.detSteps = ['Finding the determinant by summing the cofactors of row 1:','','(Use the up and down keys to scroll)','']
        app.inverseSolution = []
        app.inverseSteps = ['Finding the inverse by using the cofactor matrix: A^-1 = 1/det(A) * C^T','','(Use the up and down keys to scroll)','']
        app.multiplicationSolution = []
        app.multiplicationSteps = ['Multiplying two matrices row-by-column:','','(Use the up and down keys to scroll)','']
        app.additionSolution = []
        app.additionSteps = ['Add two matrices element-by-element:','','(Use the up and down keys to scroll)','']
        app.transposeSolution = []
        app.transposeSteps = ['Make the rows the columns and the columns the rows:','','(Use the up and down keys to scroll)','']
        app.visualizeSolution=[]
        app.visualizeSteps = ['Directed Graph of Inputed Matrix:']
        app.RREFSolution = []
        app.RREFSteps = ['Finding RREF using row operations:','','(Use the up and down keys to scroll)','']
        app.basisSolution = []
        app.basisSteps = ['Find the RREF to find the basis for the four fundamental subspaces','','(Use the up and down keys to scroll)','']


app = MyModalApp(width=1000, height=700)
