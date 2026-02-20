import tkinter as tk

root = tk.Tk()
root.title("QR Code")
canvas = tk.Canvas(root, bg="white", highlightthickness=0)
canvas.pack()

MODULE = 20
QUIET = 4


def display(board):

    n = len(board)
    size = (n + 2 * QUIET) * MODULE

    canvas.config(width=size, height=size)
    canvas.delete("all")

    for y, row in enumerate(board):
        for x, value in enumerate(row):
            if value == 1:
                x1 = (x + QUIET) * MODULE
                y1 = (y + QUIET) * MODULE
                x2 = x1 + MODULE
                y2 = y1 + MODULE
                canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="")
    root.mainloop()
