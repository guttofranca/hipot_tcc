import threading
import time
import tkinter
from threading import Thread
from tkinter import *

# necessário para codificar imagens usadas na aplicaçao
import base64

# módulo com métodos que serão usado para controle do hipor
from hipot_ import hipot


class Funcs:

    def start_test_dut (self,event):

        def start_test_dut_in():

            if (event.widget.get().upper()[0:3] == "F24" or event.widget.get().upper()[0:3] == "F42") and len(
                    event.widget.get()) == 13:

                self.entry_log_dut1.delete(1.0, "end")
                self.entry_log_dut1.insert(1.0, "Testing....")
                self.entry_log_dut1.configure(bg="YELLOW", fg="BLACK")

                dut1 = hipot()
                dut1.start_stop_tests(dut1.START_TEST)
                dut1.get_result()

                self.entry_log_dut1.delete(1.0, "end")
                self.entry_log_dut1.insert(1.0, f"Serial: {event.widget.get().upper()}\n{dut1.return_results()}")

                if dut1.result_status == "FAIL":
                    self.entry_log_dut1.configure(bg="RED", fg="WHITE")

                else:
                    self.entry_log_dut1.configure(bg="GREEN", fg="WHITE")

                    # apagar serial do campo de serial
                self.entry_serial_dut1.delete(0, "end")
            else:
                self.entry_log_dut1.delete(1.0, "end")
                self.entry_log_dut1.insert(1.0, f"SERIAL INVÁLIDO!!!\nSERIAL PREFIX:{event.widget.get().upper()[0:3]}"
                                                f"\nSERIAL SIZE:{len(event.widget.get())}")
                self.entry_log_dut1.configure(bg="YELLOW", fg="BLACK")

        threading.Thread(target=start_test_dut_in()).start()

class Application(Funcs):

    def __init__(self):
        # janela principal
        self.main_window = Tk()

        # configuraçãoes da janela principal
        self.main_window_cfg()

        self.menu_principal()

        self.frame_dut1()

        self.main_window.mainloop()

    # método que irá configurar a tela principal da aplicação
    # configuraçãoes da janela principal
    def main_window_cfg(self):
        self.main_window.title("HIPOT TESTER")

        # tela cheia sem os botões acessíveis
        # self.main_window.attributes("-fullscreen",True)

        # tela cheia com os botões acessíveis
        self.main_window.state("zoomed")

        # não permite o dimensionamento e ainda desabilita
        # o botão maximizar/restaurar
        self.main_window.resizable(False, False)

        self.main_window.config(bg="#BEBEBE")

    def menu_principal(self):
        menu_bar = Menu(self.main_window)

        self.main_window.config(menu=menu_bar)

        def quit(): pass  # self.main_window.destroy()

        filemenu1 = Menu(menu_bar)
        filemenu2 = Menu(menu_bar)

        menu_bar.add_cascade(label="Opções", menu=filemenu1)
        menu_bar.add_cascade(label="Sobre", menu=filemenu2)

        filemenu1.add_command(label="Sair", command=quit)
        filemenu1.add_command(label="Configurações", command=quit)
        filemenu2.add_command(label="Sobre o programa...", command=quit)

    def frame_dut1(self):
        self.frame_dut1 = Frame(self.main_window, bd=4, bg='#dfe3ee',
                                highlightbackground='#759fe6', highlightthickness=3)
        self.frame_dut1.place(relx=0.0035, rely=0.01, relwidth=0.25, relheight=0.48)

        ## Criação da label e entrada do codigo
        self.lb_dut1 = Label(self.frame_dut1, text="DUT1", font=('verdana', 16, 'bold'), bg='#dfe3ee')
        self.lb_dut1.place(relx=0.33, rely=0.02)
        self.lb_serial_dut1 = Label(self.frame_dut1, text="SERIAL", bg='#dfe3ee')
        self.lb_serial_dut1.place(relx=0.02, rely=0.17)

        self.entry_dut1_var = tkinter.StringVar()
        self.entry_serial_dut1 = Entry(self.frame_dut1, font=('verdana', 16, 'bold'), textvariable=self.entry_dut1_var)
        self.entry_serial_dut1.place(relx=0.02, rely=0.23, relwidth=0.7)
        self.entry_serial_dut1.bind("<Return>", self.start_test_dut)

        self.lb_log_dut1 = Label(self.frame_dut1, text="LOG", bg='#dfe3ee')
        self.lb_log_dut1.place(relx=0.02, rely=0.34)
        self.entry_log_dut1 = Text(self.frame_dut1, font=('verdana', 16, 'bold'))
        self.entry_log_dut1.grid(column=1, row=7)
        self.entry_log_dut1.place(relx=0.02, rely=0.40, relwidth=0.95, relheight=0.57)


if __name__ == "__main__":
    Application()
