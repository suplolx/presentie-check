from tkinter import *

from presentie_app import presentie, client_auth
from secret import folder_id


# Create window
app = Tk()


def get_presentie_data(input_naam, weeks):
    if int(weeks) > 10:
        print("Sorry, het maximale aantal weken is 10.")
        sys.exit(0)
    # Initialise sheets app
    service = client_auth('drive', "v3")

    # Creating a query for selecting the right folder in Google Drive
    query=f"'{folder_id}' in parents"

    response = service.files().list(q=query,
                                    spaces='drive',
                                    fields='files(id, name, parents)').execute()

    # Retrieving all files in the folder and sorting them by week number
    files = response.get("files", [])
    files_sorted = sorted(files, key=lambda i: i['name'], reverse=True)


    data_list = list()

    # Looping through files searching for given name and week range
    for file in files_sorted[0:int(weeks)]:
        # Excluding template file from data
        if file["name"] != "Presentie Lijst Template":
            presentie_data = presentie(input_naam, file['id'])
            data_list.append(
                {
                    "week_nummer": file['name'], 
                    "aanwezig": presentie_data[1],
                    "afwezig": presentie_data[2],
                    "afgemeld": presentie_data[3],
                    "aanwezig_p": presentie_data[4]
                }
            )
            print(f"{file['name']} succesvol opgehaald..")
    return data_list


def zoek_deelnemer():
    presentie_lijst.insert(END, "Een moment geduld a.u.b...")
    deelnemer = deelnemer_text.get()
    week_nummer = week_text.get()
    data = get_presentie_data(deelnemer, week_nummer)
    presentie_lijst.delete(0, END)
    for row in data:
        presentie_lijst.insert(END, f"{row['week_nummer']}    |    Score: {row['aanwezig_p']}    |    Aanwezig: {row['aanwezig']}    |    Afwezig/Afgemeld: {row['afwezig']}/{row['afgemeld']}")

# Deelnemer
deelnemer_text = StringVar()
deelnemer_label = Label(app, text="Naam Deelnemer", font=('bold', 14), pady=20)
deelnemer_label.grid(row=0, column=0, sticky=W)
deelnemer_entry = Entry(app, textvariable=deelnemer_text)
deelnemer_entry.grid(row=0, column=1)

# Week nummer
week_text = StringVar()
week_label = Label(app, text="Week nummer", font=('bold', 14), pady=10)
week_label.grid(row=0, column=2, sticky=E)
week_entry = Entry(app, textvariable=week_text)
week_entry.grid(row=0, column=3)

# Output lijst
presentie_lijst = Listbox(app, height=15, width=90, font=('bold', 10))
presentie_lijst.grid(row=2, column=0, columnspan=4, rowspan=6, pady=10, padx=10)

# Scrollbar
scrollbar = Scrollbar(app)
scrollbar.grid(row=2, column=4)
presentie_lijst.configure(yscrollcommand=scrollbar.set)
scrollbar.configure(command=presentie_lijst.yview)

# Buttons
add_btn = Button(app, text="Zoeken", width=12, command=zoek_deelnemer)
add_btn.grid(row=0, column=4, pady=20)


app.title("Presentie")
app.geometry('750x350')

app.mainloop()
