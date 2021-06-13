import os
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from tkinter.messagebox import askyesno

from .TextAnalyser import TextAnalyser
from .TextView import TextView
from .File import FileSocket


class App(Tk):
    def _build_menu(self) -> Menu:
        menu = Menu(self)

        menuFile = Menu(menu, tearoff=0)
        menuFile.add_command(label="Nouveau fichier [Ctrl+N]", command=self.new_file)
        menuFile.add_command(label="Ouvrir un fichier [Ctrl+O]", command=self.open_file)
        menuFile.add_command(label="Sauvegarder [Ctrl+S]", command=self.save_file)
        menuFile.add_separator()
        menuFile.add_command(label="Transpiler [Ctrl+T]", command=self.transpile)
        menuFile.add_separator()
        menuFile.add_command(label="Exit", command=self.quit)
        menu.add_cascade(label="File", menu=menuFile)

        # menuEdit = Menu(menu, tearoff=0)
        # menuEdit.add_command(label="Undo", command=self.doSomething)
        # menuEdit.add_separator()
        # menuEdit.add_command(label="Copy", command=self.doSomething)
        # menuEdit.add_command(label="Cut", command=self.doSomething)
        # menuEdit.add_command(label="Paste", command=self.doSomething)
        # menu.add_cascade(label="Edit", menu=menuEdit)
        #
        # menuHelp = Menu(menu, tearoff=0)
        # menuHelp.add_command(label="About", command=self.doAbout)
        # menu.add_cascade(label="Help", menu=menuHelp)

        self.config(menu=menu)

        return menu

    def __init__(self, characters, tokenizer, lemmatizer, transpiler, style, input_file = None):
        super().__init__()
        self.geometry("800x600")
        self.title("BNC Editer - v1.0")

        self.view = TextView(self, style=style)
        self.view.pack(side=TOP, fill=BOTH, expand=True)

        self.analyser = TextAnalyser(
            characters=characters,
            tokenizer=tokenizer,
            lemmatizer=lemmatizer,
            transpiler=transpiler,
            view=self.view
        )

        self.view.bind('<Any-KeyRelease>', self.analyse, add=True)

        self.menu = self._build_menu()

        self.file_socket = FileSocket()

        self.bind_all('<Control-n>', lambda e: self.new_file())
        self.bind_all('<Control-o>', lambda e: self.open_file())
        self.bind_all('<Control-s>', lambda e: self.save_file())

        self.bind_all('<Control-q>', lambda e: self.quit())

        if input_file:
            self.file_socket.bind(input_file)
            content = self.file_socket.load()
            self.view.text = content
            self.analyse()

    def analyse(self, _evt=None):
        result = self.analyser.analyse()
        spans = list(result.spans)
        self.view.apply_styles(spans)

    def set_title(self):
        if self.file_socket.is_empty:
            suffix = ""
        else:
            suffix = f" - {self.file_socket.file.path}"
        self.title("BNC Editer - v1.0" + suffix)

    def close_current_file(self):
        self.ask_save_current_file()
        if not self.file_socket.is_empty:
            self.file_socket.unbind()
        del self.view.text

    def ask_save_current_file(self):
        if not self.file_socket.is_empty:
            save = askyesno(
                title="Un fichier est déjà ouvert !",
                message="Voulez-vous sauvegarder les modifications en cours ?"
            )
            if save:
                self.save_file()

    def transpile(self):
        """Allow to transpile the current .bnf file into a python package"""
        dirpath = askdirectory(
            initialdir=os.curdir
        )
        if not dirpath:
            return

        self.analyser.transpile()

    def new_file(self):
        self.close_current_file()

        self.set_title()
        print('successfuly inited !')

    def open_file(self):
        self.close_current_file()
        filepath = askopenfilename(
            defaultextension='.bnf',
            filetypes=[('Backus Naur Form (*.bnf)', '*.bnf')],
            initialdir=os.curdir
        )
        self.file_socket.bind(filepath)
        content = self.file_socket.load()
        self.view.text = content
        self.analyse()

        self.set_title()
        print('successfuly loaded !')

    def save_file(self):
        if self.file_socket.is_empty:
            filepath = asksaveasfilename(
                defaultextension='.bnf',
                filetypes=[('Backus Naur Custom (*.bnf)', '*.bnf')],
                initialdir=os.curdir
            )
            if not filepath:
                return
            self.file_socket.bind(filepath)

        if self.file_socket.is_empty:
            print('nothing to save !')
            return

        content = self.view.text
        self.file_socket.save(content)

        self.set_title()
        print('successfuly saved !')
