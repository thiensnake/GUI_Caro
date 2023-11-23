from tkinter import *
import random
from tkinter import messagebox
import mysql.connector
from datetime import datetime

def create_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="caro"
    )

def save_winner_to_database(winner):
    conn = create_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ketqua (
                id INT AUTO_INCREMENT PRIMARY KEY,
                winner VARCHAR(255),
                date_time DATETIME
            );
        ''')

        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO ketqua (winner, date_time)
            VALUES (%s, %s);
        ''', (winner, current_datetime))

        conn.commit()
        messagebox.showinfo("Thông báo", "Người chơi Thắng cuộc đã được lưu vào cơ sở dữ liệu.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi lưu vào cơ sở dữ liệu: {str(e)}")
    finally:
        conn.close()

def switch_player():
    global player, computer_player
    player = "X" if player == "O" else "O"
    label.config(text=("Lượt " + player))
    computer_player = not computer_player
    if computer_player:
        computer_move()

def next_turn(row, column):
    global player, computer_player

    if buttons[row][column]['text'] == "" and check_winner() is False:
        buttons[row][column]['text'] = player

        if check_winner() is False:
            switch_player()

        elif check_winner() is True:
            label.config(text=(player + " Thắng "))
            save_winner_to_database(player)

        elif check_winner() == "Tie":
            label.config(text="Hòa!")

def check_winner():
    for row in range(3):
        if buttons[row][0]['text'] == buttons[row][1]['text'] == buttons[row][2]['text'] != "":
            highlight_winner_buttons(row, 0, row, 1, row, 2)
            return True

    for column in range(3):
        if buttons[0][column]['text'] == buttons[1][column]['text'] == buttons[2][column]['text'] != "":
            highlight_winner_buttons(0, column, 1, column, 2, column)
            return True

    if buttons[0][0]['text'] == buttons[1][1]['text'] == buttons[2][2]['text'] != "":
        highlight_winner_buttons(0, 0, 1, 1, 2, 2)
        return True

    elif buttons[0][2]['text'] == buttons[1][1]['text'] == buttons[2][0]['text'] != "":
        highlight_winner_buttons(0, 2, 1, 1, 2, 0)
        return True

    elif empty_spaces() is False:
        for row in range(3):
            for column in range(3):
                buttons[row][column].config(bg="yellow")
        return "Tie"

    else:
        return False

def highlight_winner_buttons(row1, col1, row2, col2, row3, col3):
    buttons[row1][col1].config(bg="green")
    buttons[row2][col2].config(bg="green")
    buttons[row3][col3].config(bg="green")

def empty_spaces():
    for row in range(3):
        for column in range(3):
            if buttons[row][column]['text'] == "":
                return True
    return False

def computer_move():
    empty_cells = [(row, col) for row in range(3) for col in range(3) if buttons[row][col]['text'] == ""]
    if empty_cells:
        row, col = random.choice(empty_cells)
        next_turn(row, col)

def new_game():
    global player, computer_player
    player = random.choice(players)
    label.config(text=("Lượt " + player))
    computer_player = True  # Đặt computer_player = True để máy đánh trước khi bắt đầu lượt chơi

    for row in range(3):
        for column in range(3):
            buttons[row][column].config(text="", bg="#F0F0F0")

    if computer_player:
        computer_move()

# Thiết lập giao diện
window = Tk()
window.title("Caro")

players = ["X", "O"]
player = random.choice(players)
computer_player = False  # Thêm biến computer_player để xác định lượt của máy

buttons = [[0, 0, 0],
           [0, 0, 0],
           [0, 0, 0]]

label = Label(text=("Lượt " + player), font=('arial', 40))
label.pack(side="top")

reset_button = Button(text="Restart", font=('Consolas', 20), command=new_game, bg="#4CAF50", fg="black")
reset_button.pack(side="top", pady=5)

frame = Frame(window)
frame.pack()

for row in range(3):
    for column in range(3):
        buttons[row][column] = Button(frame, text="", font=('consolas', 40), width=5, height=2,
            command=lambda row=row, column=column: next_turn(row, column))
        buttons[row][column].grid(row=row, column=column)

window.mainloop()                         
