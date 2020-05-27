import tkinter as tk
from tkinter import simpledialog
from random import sample
from time import sleep, perf_counter

debug=False

class Game():
    def __init__(self,
                 mode='easy',
                 height=None,
                 width=None,
                 num_mines=None,
                 board=None):
        num_mines_dict = {'easy': (9, 9, 10), 'medium': (16, 16, 40), 'hard': (16, 30, 99)}
        if mode== 'custom':
            self.height = height
            self.width = width
            self.num_mines = num_mines
        else:
            self.difficulty = mode
            self.height = num_mines_dict[mode][0]
            self.width = num_mines_dict[mode][1]
            self.num_mines = num_mines_dict[mode][2]
        self.mode=mode
        self.highscores=self.read_highscores()
        self.board=board
        self.pics=dict()
        self.load_pics()
        self.reset()

    def reset(self):
        for tile in self.board.winfo_children():
            tile.destroy()
        self.lost=False
        self.started=False
        self.start_time=None
        self.time=tk.Label(self.board,text=f"{0:0.2f}")
        self.time.grid(row=0, column=self.width-3, columnspan=3)
        self.update_stopwatch()
        self.status = tk.Label(self.board, text='new game')
        self.status.grid(row=0, column=0, columnspan=self.width - 3)
        self.expanded=[[False] * self.width for _ in range(self.height)]
        self.flagged=[[False] * self.width for _ in range(self.height)]
        self.mines=[[False]*self.width for _ in range(self.height)]
        self.spawn_mines()
        self.tiles=[[None]*self.width for _ in range(self.height)]
        self.init_tiles()

    def load_pics(self):
        pic_names = [str(i) for i in range(9)]+['flag','mine','plain','wrong']
        for pic_name in pic_names:
            rel_path=f'assets\\images\\tile_{pic_name}.gif'
            self.pics[pic_name]=tk.PhotoImage(file=rel_path).zoom(2,2)

    def spawn_mines(self):
        global debug
        locs=list(range(self.width*self.height))
        mine_locs=sample(locs,self.num_mines)
        for mine in mine_locs:
            self.mines[mine//self.width][mine%self.width]=True
        if debug:
            for row in self.mines:
                print(row)

    def init_tiles(self):
        for i in range(self.height):
            for j in range(self.width):
                tile=tk.Button(self.board,image=self.pics['plain'])
                #left click to expand tile
                tile.bind('<Button-1>',lambda event, i=i, j=j: self.expand(i,j))
                #right click to toggle flag on unexpanded tile
                tile.bind('<Button-3>',lambda event, i=i, j=j: self.toggle_flag(i,j))
                tile.grid(row=i+1,column=j)
                self.tiles[i][j]=tile

    def update_stopwatch(self):
        if self.started:
            duration = perf_counter() - self.start_time
            self.time.configure(text=f"{duration:0.2f}")
        self.board.after(10, self.update_stopwatch)

    def timer(self, action):
        if action == 'start' and not self.started:
            self.started = True
            self.start_time = perf_counter()
        elif action == 'end':
            self.started = False
            if not self.lost:
                self.update_scoreboard(perf_counter() - self.start_time)

    def read_highscores(self):
        try:
            with open(f'assets\\scores\\{self.mode}_scores.txt', 'r') as f:
                data = f.readlines()
            highscores=[]
            for score in data:
                name, time = score.split()
                highscores.append((name,float(time)))
            return highscores
        except:
            pass

    def prompt_name(self):
        return simpledialog.askstring(title='Congrats!',prompt='What is your name?')

    def update_scoreboard(self,new_time):
        if self.mode!='custom':
            if len(self.highscores)<10 or new_time<self.highscores[-1][1]:
                new_name = self.prompt_name()
                if len(self.highscores)==10:
                    self.highscores=self.highscores[:-1]
                self.highscores.append((new_name,new_time))
                self.highscores.sort(key=lambda x: x[1])
                try:
                    with open(f'assets\\scores\\{self.mode}_scores.txt', 'w') as f:
                        data = '\n'.join(' '.join(str(e) for e in score) for score in self.highscores)
                        f.write(data)
                except:
                    if debug:
                        print('update scoreboard failed')

    def checkwin(self):
        if self.height * self.width == sum(sum(row) for row in self.flagged) \
                + sum(sum(row) for row in self.expanded):
            self.timer('end')
            self.status.config(text="game won!")

    def game_over(self):
        self.lost = True
        self.status.config(text="game over.")
        self.timer('end')
        for r in range(self.height):
            for c in range(self.width):
                # show mines
                if self.mines[r][c]:
                    self.tiles[r][c].configure(image=self.pics['mine'])
                # show false flags
                elif self.flagged[r][c]:
                    self.tiles[r][c].configure(image=self.pics['wrong'])

    def expand(self,i,j):
        global debug
        if not self.lost:
            self.timer('start')
            #first, if a mine is clicked
            if self.mines[i][j]:
                self.game_over()
            #otherwise, expand all connected tiles using dfs
            else:
                frontier = [(i,j)]
                while frontier:
                    r,c=frontier.pop()
                    self.expanded[r][c]=True
                    if debug:
                        print(r,c)
                    adj_mines = 0
                    # count adjacent mines to label the expanded tile
                    valid=lambda x,y: 0 <= x < self.height and 0 <= y < self.width
                    for x in (r - 1, r, r + 1):
                        for y in (c - 1, c, c + 1):
                            if valid(x, y) and self.mines[x][y]:
                                adj_mines += 1
                    self.tiles[r][c].configure(image=self.pics[str(adj_mines)])
                    #if current tile does not have adjacent mines
                    if not adj_mines:
                        #find all neighboring tiles to expand into
                        for x,y in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
                            if valid(x,y)\
                              and not self.expanded[x][y]\
                              and not self.mines[x][y]:
                                frontier.append((x,y))
                self.checkwin()

    def toggle_flag(self,i,j):
        #make sure the tile is not expanded
        if not self.lost and not self.expanded[i][j]:
            self.timer('start')
            self.flagged[i][j]=not self.flagged[i][j]
            img=self.pics['flag'] if self.flagged[i][j] else self.pics['plain']
            self.tiles[i][j].configure(image=img)
            self.checkwin()
