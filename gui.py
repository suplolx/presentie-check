from tkinter import *

from presentie_app import get_presentie_data


class PresentieGUI:
    
    def __init__(self, master):
        self.master = master
        master.title = "Presentie App"
        master.geometry('750x350')
        # Deelnemer
        self.deelnemer_text = StringVar()
        self.deelnemer_label = Label(self.master, text="Naam Deelnemer", font=('bold', 14), pady=20)
        self.deelnemer_entry = Entry(self.master, textvariable=self.deelnemer_text)
        # Week nummer
        self.week_text = StringVar()
        self.week_label = Label(self.master, text="Aantal weken", font=('bold', 14), pady=10)
        self.week_entry = Entry(self.master, textvariable=self.week_text)
        # Output box
        self.presentie_lijst = Listbox(self.master, height=15, width=90, font=('bold', 10))
        # Button
        self.add_btn = Button(self.master, text="Zoeken", width=12, command=self.zoek_deelnemer)
        # Layout
        self.deelnemer_label.grid(row=0, column=0, sticky=W)
        self.deelnemer_entry.grid(row=0, column=1)
        self.week_label.grid(row=0, column=2, sticky=E)
        self.week_entry.grid(row=0, column=3)
        self.presentie_lijst.grid(row=2, column=0, columnspan=4, rowspan=6, pady=10, padx=10)
        self.add_btn.grid(row=0, column=4, pady=20)

    def zoek_deelnemer(self):
        self.presentie_lijst.insert(END, "Een moment geduld a.u.b...")
        deelnemer = self.deelnemer_text.get()
        week_nummer = self.week_text.get()
        data = get_presentie_data(deelnemer, week_nummer)
        self.presentie_lijst.delete(0, END)
        for row in data:
            self.presentie_lijst.insert(END, f"{row['week_nummer']}    |    Score: {row['aanwezig_p']}    |    Aanwezig: {row['aanwezig']}    |    Afwezig/Afgemeld: {row['afwezig']}/{row['afgemeld']}")


if __name__ == "__main__":
    root = Tk()
    gui = PresentieGUI(root)
    root.mainloop()
