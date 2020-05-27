#to publish on windows 10, enter terminal and enter this directory and type:
#pyinstaller -F --icon=assets\images\icon.ico --add-data "assets;assets" main.py
import tkinter as tk
from tkinter import messagebox #not imported directly
from game import Game


class Wrapper():
    def __init__(self,mode='easy'):
        self.mode=mode

        self.root=tk.Tk()
        self.root.title('minesweeper')
        self.root.iconbitmap(default='assets\\images\\icon.ico')

        self.board=tk.Frame(self.root)
        self.board.pack(side=tk.BOTTOM)

        self.game=Game(board=self.board)

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        mode_select=tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='mode', menu=mode_select)
        modes = ['easy', 'medium', 'hard', 'custom']
        for gamemode in modes:
            mode_select.add_command(label=gamemode, command=lambda mode=gamemode:self.select_mode(mode))

        menubar.add_command(label='reset',command=self.reset_game)

        menubar.add_command(label='high scores', command=self.display_scoreboard)

        menubar.add_command(label='about',command=self.about_game)

        self.root.mainloop()

    def display_scoreboard(self):
        if self.mode=='custom':
            messagebox.showerror(title='not applicable',message='no scoreboard for custom mode')
        else:
            scoreboard = tk.Toplevel(self.root,width=800)
            scoreboard.geometry("%dx%d%+d%+d" % (400, 300, 0, 0))
            scoreboard.title(f'{self.mode} mode - high scores')
            with open(f'assets\\scores\\{self.mode}_scores.txt','r') as f:
                data=f.readlines()
                if not data:
                    placeholder=tk.Label(scoreboard,text="level not solved yet. be the first to solve it.")
                    placeholder.pack()
                for i,record in enumerate(data):
                    name, time = record.split()
                    score=tk.Label(scoreboard,text=f'No. {i+1}. {name} {float(time):0.4f}')
                    score.pack()

    def about_game(self):
        about = tk.Toplevel(self.root)
        about.geometry("%dx%d%+d%+d" % (200, 30, 0, 0))
        about.title('about')
        about_text=tk.Label(about,text="made by mikey2520 on 5.24.2020")
        about_text.pack()

    def params_invalid(self,height, width, num_mines):
        return height * width < num_mines \
               or height<=0 or width<=0 or num_mines<0

    def submit_settings(self,height, width, num_mines, settings):
        height, width, num_mines=map(tk.IntVar.get,[height,width,num_mines])
        if self.params_invalid(height,width,num_mines):
            messagebox.showerror(title="bad parameters",message="please enter valid parameters for the customized game.")
        else:
            self.game=Game(mode='custom', board=self.board, height=height, width=width, num_mines=num_mines)
            settings.destroy()

    def create_entry_with_name(self,window, name, entry_var):
        label = tk.Label(window, text=name)
        entry = tk.Entry(window, textvariable=entry_var)
        label.pack()
        entry.pack()

    def customize_game(self):
        settings = tk.Toplevel(self.root)
        settings.title('customize self.game')
        names = ['height', 'width', 'number of mines']
        height, width, num_mines = tk.IntVar(value=10), tk.IntVar(value=10), tk.IntVar(value=30)
        for name, entry_var in zip(names, [height, width, num_mines]):
            self.create_entry_with_name(settings, name, entry_var)
        submit = tk.Button(settings, text='submit')
        submit.bind('<Button-1>', \
                    lambda event, height=height, width=width, num_mines=num_mines, settings=settings: \
                        self.submit_settings(height, width, num_mines, settings))
        submit.pack()

    def select_mode(self,mode):
        self.mode=mode
        if self.mode== 'custom':
            self.customize_game()
        else:
            self.game=Game(mode=self.mode, board=self.board)

    def reset_game(self):
        self.game.reset()


if __name__=='__main__':
    wrapper=Wrapper()
