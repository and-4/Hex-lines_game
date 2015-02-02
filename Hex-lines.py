# Смысл игры состоит в том, чтобы первым выстроить 5 своих клеток в ряд

from tkinter import *
import time, sys

class MyCanvas():
    def __init__(self):
        mainRoot = Tk()
        mainRoot.title('Hex-lines')
        self.c = Canvas(mainRoot, width=800, height=600, bg='white')
        self.c.pack(expand=YES, fill=BOTH)
        self.c.bind('<ButtonPress-1>', self.onCanvasClick)
        self.c.bind('a', self.testingFunc)
        self.c.bind('<Configure>', self.chekWindowSize)
        self.mainRoot = mainRoot
        self.initialState()
        self.initialGame()

    def initialState(self):   # перезапускаем в каждой новой игре для обнуления данных
        self.c.lastcell = 0
        self.c.last_indexI = 0
        self.c.last_indexJ = 0
        self.c.involvedCellList = []
        self.c.recountList = []
        self.c.usedCells = []
        self.c.isWinnerStatus = 0

    def initialGame(self):   # запускаем 1 раз в начале
        self.c.c_lengthOfCounting = 5
        self.c.c_numCellsForWin = 5
        self.c.c_rows_numb = 70
        self.c.c_column_numb = 70
        self.c.c_startingCell = 1775  # номер начальной клетки
        self.c.c_directionsList = ['W', 'NW', 'NE', 'E', 'SE', 'SW']  # определяем 6 направлений
        self.c.c_idDict = {}
        self.c.isCheating = 0
        self.c.focus_set()
        self.isTestCellFactorDisplay = 0   # для отображения фактора важности установить 1
        self.startsCounter = 0
        self.createHive()
        self.computerStep(self.c.c_startingCell)  # первый ход компьютера
        self.mainRoot.mainloop()


    def chekWindowSize(self, event):  # проверяет изменение размера окна пользователем для центрирования начальной клетки
        centralCoordX = (self.c.c_idDict[self.c.c_startingCell].coord_X) / (self.c.winfo_width())
        centralCoordY = (self.c.c_idDict[self.c.c_startingCell].coord_Y) / (self.c.winfo_height())
        if 0.45 > centralCoordX or centralCoordX > 0.51:
            shiftX = (self.c.winfo_width()) * 0.48 - self.c.c_idDict[self.c.c_startingCell].coord_X
            shiftX = round(shiftX, 0)
            self.c.move('all', shiftX, 0)
            self.c.c_idDict[self.c.c_startingCell].coord_X += shiftX
        if 0.45 > centralCoordY or centralCoordY > 0.51:
            shiftY = (self.c.winfo_height()) * 0.48 - self.c.c_idDict[self.c.c_startingCell].coord_Y
            shiftY = round(shiftY, 0)
            self.c.move('all', 0, shiftY)
            self.c.c_idDict[self.c.c_startingCell].coord_Y += shiftY

    def testingFunc(self, event):  # тестовая ф-ия для отключения и включения ходов компьютера
        if self.c.isCheating:
            self.c.isCheating = 0
            print('STOP TESTING')
        else:
            self.c.isCheating = 1
            print('START TESTING')


    def createHive(self):  # создает массив клеток
        filled_row = 0
        self.c.matrix = [0] * self.c.c_rows_numb  # создаем пустой массив клеток
        for i in range(self.c.c_rows_numb):
            self.c.matrix[i] = [0] * self.c.c_column_numb
        shift = 0
        for i in range(self.c.c_rows_numb):   # заполняет массив
            for j in range(self.c.c_column_numb):
                self.c.matrix[j][i] = self.HexPolygon(self.c,j * 38 + shift - 540, filled_row * 32 - 510, j, i)
            filled_row += 1
            if shift:
                shift = 0
            else:
                shift = 20

        if self.isTestCellFactorDisplay:  # в тестовом режиме включает отображение фактора важности клеток
            self.test_show_cell_factor()


    def onCanvasClick(self, event): # при клике пользователем происходит ход игрока
        if self.c.isWinnerStatus == 0:
            closest = event.widget.find_closest(event.x, event.y)[0] # определяем клетку, по которой кликнули
            if self.c.c_idDict[closest].status == 0:
                self.changeCellState(closest, 2)
                if self.c.isWinnerStatus == 0 and self.c.c_idDict[self.c.lastcell].status != 1:
                    self.computerStep()   # ход компьютера


    def changeCellState(self, closest, flag):   # меняет состояние клетки
        self.c.usedCells.append(closest)
        self.c.itemconfig(closest, fill='ghost white')  # графичесий эффект мигания
        self.mainRoot.update()
        time.sleep(0.1)
        self.c.lastcell = closest
        self.c.c_idDict[closest].factor = 0
        if closest in self.c.involvedCellList:
            self.c.involvedCellList.remove(closest)

        if flag == 1:  # если ход компьютера
            self.c.itemconfig(closest, fill='coral')
            self.c.c_idDict[closest].status = 1
            self.recount()
        elif flag == 2:  # если ход игрока
            self.c.itemconfig(closest, fill='sky blue')
            self.c.c_idDict[closest].status = 2
            self.recount()

    def recount(self):  # расчитывает фактор важности для окружающих клеток
        if not self.winChek(self.c.lastcell):
            if self.c.isWinnerStatus == 0:
                self.createListForRecount()
                self.recountCellsFactor(self.c.lastcell)

    def showOneNeighborCell(self, index, direction,length):
    # возвращает объект в ячейке, находящийся по направлению direction на удалении length
        if length < 1:
            print('WRONG - length is less than 1')
        elif direction == 'W':
            shift_J = -length
            shift_I = 0
        elif direction == 'E':
            shift_J = length
            shift_I = 0
        elif self.c.c_idDict[index].indexJ % 2 == 0:      # для нечетных рядов
            if direction == 'NE':
                shift_J = length // 2
                shift_I = -length
            elif direction == 'SE':
                shift_J = length // 2
                shift_I = length
            elif direction == 'SW':
                shift_J = -1 * ((length + 1) // 2)
                shift_I = length
            elif direction == 'NW':
                shift_J = -1 * ((length + 1) // 2)
                shift_I = -length
            else:
                print('WRONG direction')
        else:                                          # для четных рядов
            if direction == 'NW':
                shift_J = -1 * (length // 2)
                shift_I = -length
            elif direction == 'NE':
                shift_J = (length + 1) // 2
                shift_I = -length
            elif direction == 'SE':
                shift_J = (length + 1) // 2
                shift_I = length
            elif direction == 'SW':
                shift_J = -1 * (length // 2)
                shift_I = length
            else:
                print('WRONG direction')
        neighbor_index = index + shift_J + shift_I * self.c.c_column_numb
        return self.c.c_idDict[neighbor_index]


    def createListForRecount(self):  # создает список соседних клеток для перерасчета фактора важности этих клеток
        for i in self.c.c_directionsList:
            for j in range(1, 5):
                self.c.recountList.append(self.showOneNeighborCell(self.c.lastcell, i, j))

    def recountCellsFactor(self, index):  # пересчитывает фактор важности для соседних клеток
        for i in self.c.recountList:
            if i.status == 0:
                self.factorCount(i.canv)


    def test_show_cell_factor(self):  # тестовая функция, отображает фактор каждой задействованной клетки
        for i in range(self.c.c_rows_numb):
            for j in range(self.c.c_column_numb):
                self.c.matrix[j][i].textId = self.c.create_text(self.c.matrix[j][i].coord_X,
                                                                self.c.matrix[j][i].coord_Y,
                                                                text='', tag='my_text')

    def factorCount(self, index):  # расчитывает фактор клетки в зависимости от соседних клеткок

        def directionFactorCount(index, direction, length):
        # расчитывает фактор клетки по клеткам в направлении direction на удалении length
            directionFactor = 0
            i = 1
            lastCellStatus = 0
            fiveCellsFlag = 0
            while i < length + 1:
                if self.showOneNeighborCell(index, direction, i).status == 0:
                    break
                elif self.showOneNeighborCell(index, direction,i).status == 1 and lastCellStatus != 2:
                # если это компьютерная клетка
                    directionFactor += i ** 1.2
                    lastCellStatus = 1
                    fiveCellsFlag += 1
                    if fiveCellsFlag >= 4:  # если данная клетка является пятой в ряду компьютерных клеток
                        directionFactor += i ** 3

                elif self.showOneNeighborCell(index, direction,i).status == 2 and lastCellStatus != 1:
                # если это клетка игрока
                    directionFactor += i ** 1.2
                    lastCellStatus = 2
                else:
                    break
                i += 1
            return directionFactor

        def howMuchFriendsFactor(index):  # расчитывает количество соседних дружеских клеток компьютера
            friendsFactor = 0
            for i in self.c.c_directionsList:
                if self.showOneNeighborCell(index, i, 1).status == 1:
                    friendsFactor += 0.3
            return friendsFactor

        cellFactor = 0
        for i in self.c.c_directionsList:
            cellFactor += directionFactorCount(index, i, self.c.c_lengthOfCounting)
        cellFactor += howMuchFriendsFactor(index)
        cellFactor = round(cellFactor, 3)
        if cellFactor and index not in self.c.involvedCellList:
            self.c.involvedCellList.append(index)
        self.c.c_idDict[index].factor = cellFactor
        if  self.isTestCellFactorDisplay:
            if self.c.c_idDict[index].factor:
                print('Factor',index)
                self.c.itemconfig(self.c.c_idDict[index].textId, text=self.c.c_idDict[index].factor)


    def computerStep(self, firstStep=None): # реализует ход компьютера

        def showMaxFactor(): # возвращает индекс клетки с максимальным фактором важности
            maxFactor = 0
            maxCellIndex = None
            for i in self.c.involvedCellList:
                if self.c.c_idDict[i].factor > maxFactor:
                    maxFactor = self.c.c_idDict[i].factor
                    maxCellIndex = self.c.c_idDict[i].canv
            return maxCellIndex

        self.c.update()
        time.sleep(0.3)  # задержка симулирует задумчивость компьютера

        if firstStep:  # если это первый шаг компьютера
            self.changeCellState(firstStep, 1)

        else:
            if self.c.isCheating == 0 and self.c.isWinnerStatus == 0:
                self.changeCellState(showMaxFactor(), 1)


    def winChek(self, index):  # проверка на выйгрыш

        def chekDirectionWin(index, direction, thisCellStatus):
        # проверяет наличие 5 одинаковых клеток в  одном направлении
            statusCounter = 0
            i = 1
            while i <= (self.c.c_numCellsForWin * 2 + 1):
                if self.showOneNeighborCell(index, direction, i).status == thisCellStatus:
                    statusCounter += 1
                    i += 1
                    if statusCounter >= self.c.c_numCellsForWin:
                        break
                else:
                    i += 1
                    statusCounter = 0
            if statusCounter >= self.c.c_numCellsForWin:
                return True
            else:
                return False

        thisCellStatus = self.c.c_idDict[index].status
        i = 0
        while i < 3:  # каждое из 3 направлений проверяется в обе стороны от нажатой клетки
            startPoint = self.showOneNeighborCell(index, self.c.c_directionsList[i], 6)
            if chekDirectionWin(startPoint.canv, self.c.c_directionsList[i + 3], thisCellStatus):
                self.c.isWinnerStatus = 1
                self.weHaveWinner()
                return True
            i += 1


    def weHaveWinner(self): # в случае выйгрыша
        winnerStatus = self.c.c_idDict[self.c.lastcell].status
        self.startsCounter += 1
        self.askingWindow(winnerStatus)
        self.c.isWinnerStatus = 0

        def zeroingUsedCells():
            for i in self.c.usedCells:
                self.c.c_idDict[i].status = 0
                self.c.c_idDict[i].factor = 0
                self.c.itemconfig(self.c.c_idDict[i].canv, fill='gray88')

        zeroingUsedCells()
        if self.isTestCellFactorDisplay:
            self.c.itemconfig('my_text', text='')
        self.initialState()
        if self.startsCounter % 2 == 0:  # компьютер и пользователь начинают играть по очереди
            self.computerStep(self.c.c_startingCell)

    def askingWindow(self, winnerStatus): # окно окончания игры
        if winnerStatus == 1:
            textForWinner = 'Computer win\n'
        else:
            textForWinner = 'You win\n'

        def yourTurnWindow():
            askRoot.destroy()
            if self.startsCounter == 1:   # если ход нечетный - будет ходить пользователь
                yourTurnRoot = Toplevel(self.mainRoot)
                yourTurnRoot.title('')
                yourTurnRoot.geometry('180x100+200+160')
                Button(yourTurnRoot, text='OK', width=6, font=('arial', 10),command=yourTurnRoot.destroy).pack(side=BOTTOM)
                Label(yourTurnRoot, text='Your turn\n', font=('arial', 10)).pack(side=BOTTOM)
                yourTurnRoot.focus_set()
                yourTurnRoot.grab_set()
                yourTurnRoot.wait_window()

        def generalQuit():
            askRoot.destroy()
            sys.exit()

        askRoot = Toplevel(self.mainRoot)
        askRoot.title(textForWinner)
        askRoot.geometry('180x130+200+160')
        Button(askRoot, text='Quit', width=6, font=('arial', 10), command = generalQuit).pack(side=BOTTOM)
        Label(askRoot, text='', font=('arial', 2)).pack(side=BOTTOM)
        Button(askRoot, text='Play again', width=10, font=('arial', 10), command = yourTurnWindow).pack(side=BOTTOM)
        Label(askRoot, text=textForWinner, font=('arial', 12)).pack(side=BOTTOM)
        askRoot.focus_set()
        askRoot.grab_set()
        askRoot.wait_window()

    class HexPolygon():  # создает объекты шестиугольников
        def __init__(self,canvas, X, Y, ind_I, ind_J):
            self.canv = canvas.create_polygon([X, Y - 20], [X + 18, Y - 10], [X + 18, Y + 9], [X, Y + 20],
                                              [X - 16, Y + 10], [X - 16, Y - 10], fill="gray88")
            canvas.c_idDict[self.canv] = self
            self.status = 0  # хранит статус клетки, 0 - пустая, 1 - компьютера, 2 - пользователя
            self.factor = 0  # хранит фактор важности клетки
            self.indexI = ind_I
            self.indexJ = ind_J
            self.coord_X = X
            self.coord_Y = Y
            self.textId = None   # хранит ID текстового поля для тестового режима отображения фактора важности клеток

MyCanvas()
