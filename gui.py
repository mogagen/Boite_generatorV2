###########################################################################################
#Boite generator (Box generator)                                                          #
#Moga Gen - 07.01.2024                                                                    #
#last modified 07.01.2024                                                                 #
#GUI to collect parameters                                                                #
#Create a json file called current_values                                                 #
###########################################################################################
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import filedialog
import custom_lib as fct
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
#-------------------------------------------------------------------------------------------------------
#Variables
default_values=fct.load_json("./data/default_values.json")
translations = fct.load_json("data/dict_langues.json")
#longueur - length (mm)
lo = default_values["lo"]
#largeur - width (mm)
la = default_values["la"]
#hauteur  - height (mm)
h = default_values["h"]
#tableau dimensions
dimensions=[lo, la, h]
#format dimensions (dimensions internes ou externs) : True = externes, False = internes
#épaisseur bois - wood thickness (mm) (corps - body)
ep = default_values["ep"]
#épaisseur plexiglas - plexi thickness (mm) (couvercle - lid)
eplex = default_values["eplex"]
#colonnes et lignes
separ_check=default_values["separ_check"]
columns=default_values["columns"]
rows=default_values["rows"]
#type de fermeture
fermeture_type=default_values["fermeture_type"]
fermeture_forme=default_values["fermeture_forme"]
#options
langues_dispo=default_values["langues_dispo"]
langue=default_values["langue"]
projet=default_values["projet"]
#------------------------------------------------------------------------------------------------------
def start_gui():
    # main window
    root = tk.Tk()
    root.geometry('800x750+420+30')
    root.title("Boite Generator")
    root.resizable(False, False)
    # Configure the column to expand
    root.grid_columnconfigure(0, weight=1)
    app = MyGUI(root)
    root.mainloop()
class MyGUI :
    def __init__(self,root):
        self.root = root
        self.langue_choice()

    def langue_choice(self) :
        #Langues
        lang=tk.Frame(self.root, borderwidth=1, relief="solid")
        lang.pack(padx=10, pady=10, fill="x", expand=True)
        # Create a label
        label = tk.Label(lang, text="Langage:")
        label.pack()
        # Create a Combobox for language selection with keys from langues_dispo
        lang_dropdown = ttk.Combobox(lang, values=list(langues_dispo.keys()))
        lang_dropdown.set(list(langues_dispo.keys())[0])
        lang_dropdown.pack()
        def lang_button_click():
            selected_language = lang_dropdown.get()
            global langue
            langue = langues_dispo[selected_language]
        # Create an "OK" button
        button = tk.Button(lang, text="OK", command=lambda:[lang_button_click(),lang.destroy(),self.param()])
        button.pack()
    #---------------------------------------------------------------------------------
    #Paramètres des dimensions
    def param(self) :
        # Parameters frame
        param = tk.Frame(self.root, borderwidth=1, relief="solid")
        param.grid(row=0, column=0,sticky="ew", padx=10, pady=10)
        # retrieve language lines
        dim=fct.get_text("dim",translations,langue)
        options_list=fct.get_text("int_ext",translations,langue)
        format_txt=fct.get_text("format",translations,langue)
        epais = fct.get_text("ep", translations, langue)
        epais_title = fct.get_text("material", translations, langue)
        proj_title=fct.get_text("projet",translations,langue)
        #Project_name
        proj_name_label=tk.Label(param,text=proj_title)
        proj_name_label.grid(row=0)
        proj_name_var=tk.StringVar()
        proj_name_wid=tk.Entry(param,textvariable=proj_name_var)
        proj_name_wid.grid(row=1)

        #DIMENSIONS PARAMETERS
        format_label=tk.Label(param,text=format_txt)
        format_label.grid(row=2)
        # Create labels and Combobox widgets
        dropdown_widgets = []
        for i in range(3):
            dim_label = ttk.Label(param, text=dim[i],style="Text.TLabel")
            dim_label.grid(row=3, column=i, padx=5, pady=5,sticky="w")

            param_dropdown = ttk.Combobox(param, values=options_list)
            param_dropdown.set(options_list[0])
            param_dropdown.grid(row=4, column=i, padx=5, pady=5)

            dropdown_widgets.append(param_dropdown)
        #THICKNESS VALUES
        #thickness widgets
        float_widgets = []
        epais_title_label=tk.Label(param,text=epais_title)
        epais_title_label.grid(row=5,column=0,sticky="w")
        for j in range(2):
            ep_label = tk.Label(param, text=epais[j])
            ep_label.grid(row=6, column=j, padx=5, pady=5, sticky="w")

            ep_input = ttk.Entry(param)  # Use Entry for float input
            ep_input.insert(0, str(ep))  # Set initial value
            ep_input.grid(row=7, column=j, padx=5, pady=5)

            float_widgets.append(ep_input)
        #OK BUTTON
        param_ok_button= tk.Button(param, text="OK", command=lambda: [param_button_click(), self.dimensions_principales()])
        param_ok_button.grid(row=8)

        def toggle_widget_state():
        # Iterate through all widgets in the 'param' frame
            for widget in param.winfo_children() :
                if isinstance(widget, ttk.Entry):
                    widget["state"] = "readonly"
                if isinstance(widget, ttk.Combobox):
                    widget["state"] = "disabled"

        def param_button_click():
            form = []
            for dropdown in dropdown_widgets:
                if "int" in dropdown.get():
                    form.append(False)
                else:
                    form.append(True)
            global ep, eplex
            ep = float(float_widgets[0].get())
            eplex = float(float_widgets[1].get())
            global format_dim
            format_dim = [form, [ep + ep, ep + ep, ep + eplex]]
            #project name
            global projet
            projet=proj_name_var.get()
            #replace ok button by a checkmark
            param_ok_button.destroy()
            checkmark_label = tk.Label(param, text="✓", font=("Arial", 16), fg="green")
            checkmark_label.grid(row=6,padx=10, pady=10)
            # Toggle widget state after processing
            toggle_widget_state()
    #---------------------------------------------------------------------------------------------
    #Dimensions
    input_values=[]
    def dimensions_principales(self) :
        dimens = tk.Frame(self.root, borderwidth=1, relief="solid")
        dimens.grid(row=1, column=0,sticky="ew", padx=10, pady=10)
        dimens_title=tk.Label(dimens,text=fct.get_text("dimens",translations,langue))
        dimens_title.grid(row=0)
        ext_label = tk.Label(dimens, text="ext")
        ext_label.grid(row=1, column=1)
        int_label = tk.Label(dimens, text="int")
        int_label.grid(row=1, column=2)

        # Create an empty list to hold the input values
        dim = fct.get_text("dim", translations, langue)
        # Create an empty list to hold the widgets
        input_list=[]
        for i, condition in enumerate(format_dim[0]):#True : ext, False : int
            #variables
            dimensions_input_value= tk.DoubleVar()
            #widgets
            dimension_label = tk.Label(dimens, text=dim[i])
            dimension_label.grid(row=i+2,column=0)
            dimensions_input = tk.Entry(dimens, textvariable=dimensions_input_value)
            #set values and add to gridlist
            if condition: #ext=input
                dimensions_input_value.set(dimensions[i]) #ext
                dimensions_output = tk.Label(dimens, text="-")
                dimensions_input.grid(row=i+2, column=1)
                dimensions_output.grid(row=i+2,column=2)
            else :#int=input
                dimensions_output = tk.Label(dimens, text="-")
                dimensions_output.grid(row=i+2, column=1)
                dimensions_input_value.set(dimensions[i] - format_dim[1][i])#int
                dimensions_input.grid(row=i+2, column=2)
            input_list.append(dimensions_input)
        # Create the "OK" button
        ok_button = tk.Button(dimens, text="OK", command=lambda: [dimens_ok_click(),self.recapitulatif()])
        ok_button.grid(row=len(format_dim[0]) + 2, column=0, columnspan=3)

        # ok button functions
        def toggle_widget():
            for widget in dimens.winfo_children():
                if isinstance(widget, tk.Entry):
                    widget["state"] = "readonly"

        def dimens_ok_click():
            global input_values
            input_values = []
            for dimensions_input_value in input_list:
                input_value = dimensions_input_value.get()
                input_values.append(input_value)
            ok_button.destroy()
            toggle_widget()
            checkmark_label = tk.Label(dimens, text="✓", font=("Arial", 16), fg="green")
            checkmark_label.grid(row=6, padx=10, pady=10)
    #---------------------------------------------------------------------------------------
    def recapitulatif(self) :
        # input_values
        # format_dim
        global dimensions
        dimensions=[]
        global lo,la,h,ep,eplex
        # replace the default values
        for i,condition in enumerate(format_dim[0]) :
            if condition : #dimensions externes
                dim_ext=float(input_values[i])
                dimensions.append(dim_ext)
            else : #dimensions internes
                dim_ext=float(input_values[i])+float(format_dim[1][i])
                dimensions.append(dim_ext)
        dimensions.append(float(ep))
        dimensions.append(float(eplex))
        #on met les valeurs dans les variables
        lo=dimensions[0]
        la=dimensions[1]
        h=dimensions[2]
        ep=dimensions[3]
        eplex=dimensions[4]
        self.recapitulatif_affiche()

    def recapitulatif_affiche(self) :
        recap = ttk.Frame(self.root, borderwidth=1, relief="solid")
        recap.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        recap_title = tk.Label(recap, text=fct.get_text("recap", translations, langue))
        recap_title.grid(row=0)
        noms=fct.get_text("dim",translations,langue)+fct.get_text("ep",translations,langue)
        for i,value in enumerate(dimensions) :
            label=tk.Label(recap,text=noms[i])
            label.grid(row=1,column=i)
            value_wid=tk.Label(recap,text=str(value))
            value_wid.grid(row=2,column=i)
        # Configure columns to have equal weight
        for i in range(len(dimensions)):
            recap.grid_columnconfigure(i, weight=1)
        #matplotlib : rectangle avec cotes
        fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(8, 2))
        # Désactiver les axes et le cadre de l'axe
        for i in range(0, 3):
            axes[i].axis('off')
            axes[i].set_frame_on(False)
        fct.rect_avec_cote(lo, la, axes[0])
        fct.rect_avec_cote(lo, h, axes[1])
        fct.rect_avec_cote(la, h, axes[2])
        #canvas pour la figure
        canvas = FigureCanvasTkAgg(fig, master=recap)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=3,columnspan=5)
        #next button --> kills root
        def destroy_all_frames():
            for frame in self.root.winfo_children():
                if isinstance(frame, tk.Frame):
                    frame.destroy()
                if isinstance(frame,ttk.Frame) :
                    frame.destroy()
        next_txt=fct.get_text("next",translations,langue)
        next_button=tk.Button(text=next_txt,command=lambda:[plt.close(fig),destroy_all_frames(),next_button.destroy(),self.separation()])
        next_button.grid(row=4)

    def separation(self) :
        separ = ttk.Frame(self.root, borderwidth=1, relief="solid")
        separ.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        row=0 #row in frame
        #titre
        separ_title = tk.Label(separ, text="Separations")
        separ_title.grid(row=row)
        row+=1
        #notes sur les colonnes et lignes
        sep_tran=fct.get_text("sep",translations,langue)
        try_again=fct.get_text("try",translations,langue)
        note=tk.Label(separ,text=sep_tran[2])
        note.grid(row=row,columnspan=2)
        row+=1
        # variables
        col_input_value = tk.DoubleVar()
        row_input_value =tk.DoubleVar()
        # label
        col_label = tk.Label(separ, text=sep_tran[0])
        col_label.grid(row=row, column=0)
        row_label = tk.Label(separ,text=sep_tran[1])
        row_label.grid(row=row,column=1)
        row+=1
        #widgets
        col_input = ttk.Entry(separ, textvariable=col_input_value)
        col_input.grid(row=row,column=0)
        row_input= ttk.Entry(separ,textvariable=row_input_value)
        row_input.grid(row=row,column=1)
        row+=1

        def on_click():
            #check if values are floats
            float_check=True
            global columns,rows
            try :
                columns=int(col_input.get())
                try : rows=int(row_input.get())
                except :
                    float_check=False
            except ValueError :
                float_check=False
            #valide :
            if float_check :
                checkmark_label = tk.Label(separ, text="✓", font=("Arial", 16), fg="green")
                checkmark_label.grid(row=row+1, padx=10, pady=10)
                ok_button.destroy()
                # Toggle widget state after processing
                for wid in separ.winfo_children():
                    if isinstance(wid, ttk.Entry):
                        wid["state"] = "readonly"
                    elif wid.winfo_name() == "warning":
                        wid.destroy()
                self.fermeture()
            #non valide
            else:
                warning=tk.Label(separ,text=try_again)
                warning.grid(row=row, column=0)
        #ok button
        ok_button=tk.Button(separ,text="OK",command=lambda: on_click())
        ok_button.grid(row=row+1)

    def fermeture(self):
        fermeture = ttk.Frame(self.root, borderwidth=1, relief="solid")
        fermeture.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        rowf=0
        title = tk.Label(fermeture,text=fct.get_text("lid",translations,langue))
        title.grid(row=rowf)
        rowf+=1
        # Create a frame to hold the images and radio buttons
        ferm_forme_frame = ttk.Frame(fermeture)
        ferm_forme_frame.grid(row=rowf)
        rowf+=1
        def choose_option():
            global fermeture_forme,fermeture_type
            fermeture_forme = option.get()
            fermeture_type = option2.get()
            # replace ok button by a checkmark
            confirm_button.destroy()
            checkmark_label = tk.Label(fermeture, text="✓", font=("Arial", 16), fg="green")
            checkmark_label.grid(row=rowf, padx=10, pady=10)
            for wid in ferm_type_frame.winfo_children():
                if isinstance(wid, ttk.Radiobutton):
                    wid.state(["disabled"])
            for wid in ferm_forme_frame.winfo_children() :
                if isinstance(wid, ttk.Radiobutton) :
                    wid.state(["disabled"])
        #--------
        #choisir la forme de la poignée
        fermeture_images=[]
        for i in range(0,4) :
            file_name="./images/type_fermeture"+str(i)+".jpg"
            im=Image.open(file_name)
            im=im.resize((70,70))
            im=ImageTk.PhotoImage(im)
            fermeture_images.append(im)
        # Display the images using labels
        label_list=[]
        for i, image in enumerate(fermeture_images) :
            label = tk.Label(ferm_forme_frame, image=image)
            label.photo=fermeture_images[i]
            label.grid(row=0,column=i,padx=20)
            label_list.append(label)
        # Create a variable to hold the selected option
        option = tk.IntVar()
        ferm_forme=fct.get_text("ferm_forme",translations,langue)
        # Create radio buttons for each option
        for i, text in enumerate(ferm_forme) :
            rb= ttk.Radiobutton(ferm_forme_frame,text=text,variable=option, value=i)
            rb.grid(row=1,column=i)
        #-------
        #choix de la fermeture
        # Create a frame to hold the images and radio buttons
        ferm_type_frame = ttk.Frame(fermeture)
        ferm_type_frame.grid(row=rowf)
        rowf += 1
        fermeture_images0 = []
        for i in range(0, 2):
            file_name = "./images/fermeture_style" + str(i) + ".jpg"
            im0 = Image.open(file_name)
            width=int(round(200*(5/4),0))
            im0 = im0.resize((width, 200))
            im0 = ImageTk.PhotoImage(im0)
            fermeture_images0.append(im0)
        # Display the images using labels
        label_list = []
        for i, image in enumerate(fermeture_images0):
            label = tk.Label(ferm_type_frame, image=image)
            label.photo = fermeture_images0[i]
            label.grid(row=0, column=i, padx=20,pady=20)
            label_list.append(label)
        # Create a variable to hold the selected option
        option2 = tk.IntVar()
        # Create radio buttons for each option
        ferm_type = fct.get_text("ferm_type", translations, langue)
        for i, text in enumerate(ferm_type):
            rb = ttk.Radiobutton(ferm_type_frame, text=text,variable=option2, value=i)
            rb.grid(row=1, column=i)
        # Create a "OK" button inside the "fermeture" frame
        confirm_button = tk.Button(fermeture, text="OK", command=lambda:[choose_option(),self.choose_save_directory()])
        confirm_button.grid(row=rowf)
    def choose_save_directory(self) :
        save_directory = ttk.Frame(self.root, borderwidth=1, relief="solid",)
        save_directory.grid(row=2,sticky="ew", padx=10, pady=10)
        save = fct.get_text("save", translations, langue)
        def open_directory_dialog():
            global save_path
            save_path = filedialog.askdirectory()
            # Check if the user selected a directory or canceled the dialog
            if save_path:
                # User selected a directory, you can use 'save_path' for saving files there
                print("Selected directory:", save_path)
                save_check = tk.Label(save_directory,text=save_path)
                save_check.pack()
                save_button.destroy()
                checkmark_label = tk.Label(save_directory, text="✓", font=("Arial", 16), fg="green")
                checkmark_label.pack()
                self.generate_files()
            else:
                # User canceled the dialog
                save_check=tk.Label(save_directory,text=save[2])
                save_check.pack()

        label = tk.Label(save_directory,text=save[0])
        label.pack()
        #button
        save_button=tk.Button(save_directory,text=save[1],command=lambda:[open_directory_dialog()])
        save_button.pack()
    def generate_files(self) : #bouton qui ferme le GUI
        gen_files = tk.Frame(self.root)
        gen_files.grid(row=3, sticky="ew", padx=10, pady=10)
        txt=fct.get_text("generate",translations,langue)
        ok_button =tk.Button(gen_files,text=txt,command=lambda:self.generate_parameters())
        ok_button.pack()

    def generate_parameters(self):
        # creer le nom de la boite
        name_boite = str(int(lo)) + "x" + str(int(la)) + "x" + str(int(h))
        namedir = save_path + "/" + projet + "_" + name_boite
        if not os.path.exists(namedir):
            # If it doesn't exist, create the directory
            os.makedirs(namedir)
        namedir2 = str(namedir)
        namedir = namedir + "/" + projet + "_"
        # recapitulatif
        title_recap = fct.get_text("dim", translations, langue)
        title_recap += fct.get_text("ep", translations, langue)
        title_recap += fct.get_text("sep", translations, langue)[0:2]
        values_recap = dimensions
        values_recap.append(columns)
        values_recap.append(rows)
        recap = [title_recap, values_recap]
        #create a json with data collected
        data = {
            "langue" : langue,
            "projet" : projet,
            "dimensions" : dimensions,
            "columns" : columns,
            "rows" : rows,
            "name_boite" : name_boite,
            "namedir" : namedir,
            "namedir2" : namedir2,
            "recap":recap,
            "fermeture_type": fermeture_type,
            "fermeture_forme":fermeture_forme
        }
        #temp json file storing the values for this instance
        file="./data/current_values.json"
        #open json file for writing
        with open(file,"w") as json_file :
            json.dump(data,json_file,indent=4)
        self.root.destroy()