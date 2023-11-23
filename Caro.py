from tkinter import *
import random
from tkinter import messagebox
import mysql.connector
from datetime import datetime
from tkinter import colorchooser

def next_turn(row, column):
    global player

    if buttons[row][column]['text'] == "" and check_winner() is False:
        buttons[row][column]['text'] = player
        buttons[row][column]['fg'] = player_colors.get(player, "black")

        if check_winner() is False:
            player = players[1] if player == players[0] else players[0]
            label.config(text=("Lượt " + player))

        elif check_winner() is True:
            label.config(text=(player + " Thắng "))
            save_winner_to_database(player)
            update_history_menu()

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
    buttons[row1][col1].config(bg="#00FF00")
    buttons[row2][col2].config(bg="#00FF00")
    buttons[row3][col3].config(bg="#00FF00")  # green

def empty_spaces():
    for row in range(3):
        for column in range(3):
            if buttons[row][column]['text'] == "":
                return True
    return False

def new_game():
    global player
    player = random.choice(players)
    label.config(text=("Lượt " + player))

    for row in range(3):
        for column in range(3):
            buttons[row][column].config(text="", bg="#F0F0F0")

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

def create_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="caro"
    )

def choose_x_color():
    color = colorchooser.askcolor()[1]
    player_colors["X"] = color
    update_button_colors()

def choose_o_color():
    color = colorchooser.askcolor()[1]
    player_colors["O"] = color
    update_button_colors()

def update_button_colors():
    for row in range(3):
        for column in range(3):
            buttons[row][column].config(fg=player_colors.get(buttons[row][column]['text'], "black"))

def update_history_menu():
    history_menu.delete(0, END)
    history = get_history_from_database()
    for entry in history:
        history_menu.add_command(label=entry, command=lambda e=entry: show_history_details(e))

def get_history_from_database():
    conn = create_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT winner, date_time FROM ketqua ORDER BY date_time DESC")
    history = [f"{record[0]} - {record[1]}" for record in cursor.fetchall()]
    conn.close()
    return history

def show_history_details(entry):
    messagebox.showinfo("Chi tiết", f"Lịch sử: {entry}")

window = Tk()
window.title("Caro")

players = ["X", "O"]
player = random.choice(players)

player_colors = {"X": "red", "O": "blue"}

buttons = [[0, 0, 0],
           [0, 0, 0],
           [0, 0, 0]]

label = Label(text="Lượt " + player, font=('arial', 40))
label.pack(side="top")

# Menu bar
menu_bar = Menu(window)
window.config(menu=menu_bar)

# Colors menu
colors_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Colors", menu=colors_menu)
colors_menu.add_command(label="Choose X Color", command=choose_x_color) #Chọn màu sắc 
colors_menu.add_command(label="Choose O Color", command=choose_o_color)

# History menu
history_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="History", menu=history_menu)

reset_button = Button(text="Restart", font=('Consolas', 20), command=new_game, bg="#4CAF50", fg="black")
reset_button.pack(side="top", pady=5)

frame = Frame(window)
frame.pack()

for row in range(3):
    for column in range(3):
        buttons[row][column] = Button(frame, text="", font=('consolas', 40), width=5, height=2,
                                      command=lambda row=row, column=column: next_turn(row, column),
                                      fg=player_colors.get(player, "black"))
        buttons[row][column].grid(row=row, column=column)

update_history_menu()

window.mainloop()
