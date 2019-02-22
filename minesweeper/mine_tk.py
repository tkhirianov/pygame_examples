from tkinter import *
import random
 
GRID_SIZE = 8 # Ширина и высота игрового поля
SQUARE_SIZE = 50 # Размер одной клетки на поле
MINES_NUM = 10 # Количество мин на поле
 
# Функция реагирования на клик
def click(event):
    ids = c.find_withtag(CURRENT)[0]  # Определяем по какой клетке кликнули
    if ids in mines:
        c.itemconfig(CURRENT, fill="red") # Если кликнули по клетке с миной - красим ее в красный цвет
    elif ids not in clicked:
        c.itemconfig(CURRENT, fill="green") # Иначе красим в зеленый
    c.update()
 
# Функция для обозначения мин
def mark_mine(event):
    ids = c.find_withtag(CURRENT)[0]
    # Если мы не кликали по клетке - красим ее в желтый цвет, иначе - в серый
    if ids not in clicked:
        clicked.add(ids)
        x1, y1, x2, y2 = c.coords(ids)
        c.itemconfig(CURRENT, fill="yellow")
    else:
        clicked.remove(ids)
        c.itemconfig(CURRENT, fill="gray")
root = Tk() # Основное окно программы
root.title("Pythonicway Minesweep")
c = Canvas(root, width=GRID_SIZE * SQUARE_SIZE, height=GRID_SIZE * SQUARE_SIZE) # Задаем область на которой будем рисовать
c.pack()
 
# Следующий код отрисует решетку из клеточек серого цвета на игровом поле
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        c.create_rectangle(i * SQUARE_SIZE, j * SQUARE_SIZE,
                           i * SQUARE_SIZE + SQUARE_SIZE,
                           j * SQUARE_SIZE + SQUARE_SIZE, fill='gray')
 
c.bind("<Button-1>", click)
c.bind("<Button-3>", mark_mine)
mines = set(random.sample(range(1, GRID_SIZE**2+1), MINES_NUM))  # Генерируем мины в случайных позициях
clicked = set()  # Создаем сет для клеточек, по которым мы кликнули
 

root.mainloop() # Запускаем программу

