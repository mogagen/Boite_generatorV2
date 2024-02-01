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
from PIL import Image as PILImage
from PIL import ImageTk
from tkinter import filedialog
import custom_lib as fct
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
#-------------------------------------------------------------------------------------------------------
#Variables
default_values=fct.load_json("./data/default_values.json")
translations = fct.load_json("./data/dict_langues.json")
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
separ_check_col=default_values["separ_check"]
separ_check_row=default_values["separ_check"]
columns=default_values["columns"]
rows=default_values["rows"]
#glissière
slide_check=False
tasseau_check=False
#type de fermeture
fermeture_type=default_values["fermeture_type"]
fermeture_forme=default_values["fermeture_forme"]
couv_ras=False
#format des dimensions
dim_form_lo_la=True #False=lo et la total, True = largeur col et row
dim_form_h=True #True= h externe, False=h_interne
#options
langues_dispo=default_values["langues_dispo"]
langue=default_values["langue"]
projet=default_values["projet"]
#windows dimensions
width=1500
height=750
centered=0
#------------------------------------------------------------------------------------------------------
def start_gui():
    # main window
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    global width,height,centered
    if screen_width<width:
        width=screen_width
    else :
        centered=int((screen_width-width)/2)
    if screen_height<height :
        height=screen_height-40
    root.geometry('1000x750+420+40')
    root.geometry(f"{width}x{height}+{centered}+40")
    root.title("Boite Generator")
    root.resizable(False, False)
    # Configure the column to expand
    root.grid_columnconfigure(0, weight=1)
    MyGUI(root)
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
        button = tk.Button(lang, text="OK", command=lambda:[lang_button_click(),lang.destroy(),self.project_name()])
        button.pack()
    def project_name(self):
        def click() :
            global projet
            projet =proj_name_var.get()
            ok_button.destroy()
            proj_name_wid["state"] = "readonly"
            checkmark_label = tk.Label(self.root,text="✓", font=("Arial", 16), fg="green")
            checkmark_label.pack()

        #Project_name
        proj_title = fct.get_text("projet", translations, langue)
        proj_name_label=tk.Label(self.root,text=proj_title)
        proj_name_label.pack()
        proj_name_var=tk.StringVar()
        proj_name_wid=tk.Entry(self.root,textvariable=proj_name_var)
        proj_name_wid.pack()
        #ok_button
        ok_button=tk.Button(self.root,text="OK",command=lambda:[click(),self.parameters_choice_lay0()])
        ok_button.pack()
    #next/previous button
    def parameters_navigation(self,current_layer):
        nav_frame=tk.Frame(self.root,relief="solid",highlightbackground="grey",highlightcolor="grey", highlightthickness=1)
        nav_frame.pack(expand=True,fill="x",padx=10)
        #get translations
        nav=fct.get_text("next",translations,langue)
        #Previous button
        def previous_click():
            selected_layer=current_layer-1
            self.get_layer(selected_layer)
        def next_click() :
            selected_layer=current_layer+1
            if selected_layer <=5 :
                self.get_layer(selected_layer)
            else :
                pass
        previous_button=tk.Button(nav_frame,text=nav[1],command=lambda:[previous_click()])
        previous_button.grid(column=0,row=0,sticky="w")
        if current_layer<=1 :
            previous_button.config(state="disabled")
        next_button=tk.Button(nav_frame,text=nav[0],command=lambda:[next_click()])
        if current_layer<5 :
            next_button.grid(column=1,row=0,sticky="e")
        else :
            pass
            #to implement  : the next step (entrez les valeurs)

    #start layer
    def get_layer(self,layer):
        if layer== 1 :
            self.layer1()
        elif layer ==1.5 :
            self.layer1_5()
        elif layer ==2 :
            self.layer2()
        elif layer ==3 :
            self.layer3()
        elif layer == 4 :
            self.layer4()
        elif layer == 5 :
            self.layer5()
        else :
            print("no layer"+str(layer))
    #---------------------------------------------------------------------------------
    #Selections des paramètres
    def parameters_choice_lay0(self):
        param_choice=tk.Frame(self.root,borderwidth=1,relief="solid")
        param_choice.pack(padx=10,pady=10)
        choice_label=tk.Label(param_choice,text=fct.get_text("intro",translations,langue))
        choice_label.pack()
        # demander le type de fermeture
        self.layer1()
        #layer1_5 : si vis à ras: si il ça ne doit pas dépasser
        #layer2 :avec ou sans séparations +
        #layer3 : avec ou sans glissière
        #layer4 : forme de la poignée pour le couvercle
        #layer5 : donner les dimensions extérieures/internes de la boite ou donner la largeur des colonnes et des lignes
    #précédent/suivant
    #couche 1  :  type de fermeture pour la boite (glissière, vissé (noyé/pas noyé), posé)
    def layer1(self):
        layer1_frame=ttk.Frame(self.root,borderwidth=1,relief="solid")
        layer1_frame.pack()
        row=0
        #Title : type de fermeture
        text=fct.get_text("options",translations,langue)[0]
        lay1_title=tk.Label(layer1_frame,text=text,name="lay1_title")
        lay1_title.grid(row=row,column=0)
        row+=1
        options=fct.get_text("ferm_type",translations,langue)
        #fonctions des boutons de la couche
        #boutons "détails", affiche des détails de construction dans une fenêtre à part
        def click_details(type) : #type = type de fermeture
            details=tk.Toplevel()
            details.geometry('600x400+420+75')
            details.title("Details")
            im_path="./images/32_fermeture_type"+str(type)+"_details_"+langue+".jpg"
            im = PILImage.open(im_path)
            im = im.resize((552,368))  # Resize the image with ratio 3:2
            pho = ImageTk.PhotoImage(im)
            label = tk.Label(details, image=pho)
            label.image = pho # Store the reference to prevent garbage collection
            label.pack()
            details.mainloop()
        #bouton ok : enregistrer l'option
        def click1():
            global fermeture_type
            fermeture_type=selected_option.get()
            #clear images and options
            for widget in layer1_frame.winfo_children() :
                if widget.winfo_name() != "lay1_title":
                    widget.destroy()
            layer1_frame.config(relief="flat")
            #montrer l'option sélectionnée
            selected=tk.Label(layer1_frame,text=fct.get_text("selected",translations,langue)+options[fermeture_type])
            selected.grid(row=1,column=0)
            #self.parameters_navigation(1)
            if fermeture_type==2 : #si l'option vissé-noyé est sélectionné
                self.layer1_5()
            else : #pour les autres options
                self.layer2()
        #choix du type de fermeture
        selected_option=tk.IntVar()
        images = []
        for i in range(0,len(options)):#afficher les images pour les options
            image_path="./images/54_fermeture_type"+str(i)+".JPG"
            image = PILImage.open(image_path)
            global width #largeur de l'écran
            #largeur des images par defaut
            width_image = 350
            #plus petit si l'écran est petit
            if width < 2100:
                width_image = int((width - 100) / 4)
            #ajuster la hauteur (ratio 5:4)
            height_image = int((width_image / 5) * 4)
            image = image.resize((width_image,height_image))
            photo = ImageTk.PhotoImage(image)
            images.append(photo)
            label=tk.Label(layer1_frame,image=images[i])
            label.image=images[i]
            label.grid(row=row,column=i)
        row+=1
        for i,option in enumerate(options) :#radiobutton pour le choix de la forme de fermeture
            radio_button = ttk.Radiobutton(layer1_frame, text=option, variable=selected_option, value=i)
            radio_button.grid(row=row,column=i)
        row+=1
        #details : ajouter un bouton "détails" qui ouvre une fenêtre avec des infos supplémentaire
        button_detail2=tk.Button(layer1_frame,text="Details",command=lambda:[click_details(2)])
        button_detail2.grid(row=row,column=2)
        button_detail3=tk.Button(layer1_frame,text="Details",command=lambda:[click_details(3)])
        button_detail3.grid(row=row,column=3)
        row+=1
        #OK button
        ok_button=tk.Button(layer1_frame,text="OK",command=lambda:[click1()])
        ok_button.grid(row=row,column=0,columnspan=layer1_frame.grid_size()[0])
    #couche 1.5 : si l'option vissé-noyée est choisie, choisir comment est noyée la vis (couvercle à ras ou piece3d à ras)
    def layer1_5(self):
        layer1_5_frame=tk.Frame(self.root,borderwidth=1,relief="solid")
        layer1_5_frame.pack(padx=10, pady=10, expand=True)
        #okbutton fonction
        def click15(frame):
            global couv_ras
            couv_ras=ras.get()
            #désafficher les images et options
            frame.destroy()
            #afficher l'option sélectionnée
            layer1_5_frame=tk.Frame(self.root)
            layer1_5_frame.pack()
            if couv_ras :
                text="Option 1"
            else :
                text="Option 2"
            selected=tk.Label(layer1_5_frame,text=text)
            selected.grid(row=0,column=1)
            #passer à la couche 2 (options de séparations)
            self.layer2()
        #image labels :  afficher les options
        im0=PILImage.open("./images/916_fermeture_type3_det0.JPG")
        im0 = im0.resize((225,400))
        ph0 = ImageTk.PhotoImage(im0)
        label0 = tk.Label(layer1_5_frame, image=ph0)
        label0.image = ph0
        label0.grid(row=0, column=0)
        im0 = PILImage.open("./images/916_fermeture_type3_det1.JPG")
        im0 = im0.resize((225, 400))
        ph0 = ImageTk.PhotoImage(im0)
        label0 = tk.Label(layer1_5_frame, image=ph0)
        label0.image = ph0
        label0.grid(row=0, column=1)
        #radiobuttons : widget de choix
        ras=tk.BooleanVar()
        rb0=ttk.Radiobutton(layer1_5_frame,text="Option 1",variable=ras,value=True)
        rb0.grid(row=1,column=0)
        rb1=ttk.Radiobutton(layer1_5_frame,text="Option 2",variable=ras,value=False)
        rb1.grid(row=1,column=1)
        #ok_buttons
        ok_button=tk.Button(layer1_5_frame,text="OK",command=lambda:[click15(layer1_5_frame)])
        ok_button.grid(row=2,column=0,columnspan=layer1_5_frame.grid_size()[0])

    #Couche 2 :
    def layer2(self):
        layer2_frame=tk.Frame(self.root,borderwidth=1,relief="solid")
        layer2_frame.pack()
        row=0
        #Y a t-til des séparations ou non ?
        question=tk.Label(layer2_frame,text=fct.get_text("options",translations,langue)[1])
        question.grid(row=row,column=0,columnspan=4)
        row+=1
        note=tk.Label(layer2_frame,text=fct.get_text("sep",translations,langue)[2])
        note.grid(row=row,column=0,columnspan=4)
        row+=1
        #labels :  lignes et colonnes
        col_label=tk.Label(layer2_frame,text=fct.get_text("sep",translations,langue)[3])
        col_label.grid(row=row,column=0)
        row_label=tk.Label(layer2_frame,text=fct.get_text("sep",translations,langue)[4])
        row_label.grid(row=row,column=2)
        row+=1
        #variables boolean - y-a-t-il des colonnes et/ou des lignes?
        check_col=tk.BooleanVar()
        check_row=tk.BooleanVar()
        without=fct.get_text("without",translations,langue)
        #radiobutton : avec/sans colonne
        col_rb0=ttk.Radiobutton(layer2_frame,text=without[1],variable=check_col,value=True)
        col_rb0.grid(row=row,column=0)
        col_rb1=ttk.Radiobutton(layer2_frame,text=without[0],variable=check_col,value=False)
        col_rb1.grid(row=row,column=1)
        #radiobutton : avec/sans ligne
        row_rb0 = ttk.Radiobutton(layer2_frame, text=without[1], variable=check_row, value=True)
        row_rb0.grid(row=row, column=2)
        row_rb1 = ttk.Radiobutton(layer2_frame, text=without[0], variable=check_row, value=False)
        row_rb1.grid(row=row, column=3)
        row+=1
        #on click
        def click2(frame):
            global separ_check_col,separ_check_row
            separ_check_col=check_col.get()
            separ_check_row=check_row.get()
            #clear frame
            frame.destroy()
            #afficher les choix
            layer2_frame=tk.Frame(self.root)
            layer2_frame.pack()
            col_label = tk.Label(layer2_frame, text=fct.get_text("sep", translations, langue)[3]+" : "+without[int(separ_check_col)])
            col_label.grid(row=0, column=0)
            row_label = tk.Label(layer2_frame, text=fct.get_text("sep", translations, langue)[4]+" : "+without[int(separ_check_row)])
            row_label.grid(row=0, column=1)
        #okbutton
        ok_button=tk.Button(layer2_frame,text="OK",command=lambda :[click2(layer2_frame),self.layer3()])
        ok_button.grid(row=row,column=0,columnspan=layer2_frame.grid_size()[0])

    #couche 3 : choix du posage
    def layer3(self):
        layer3_frame=tk.Frame(self.root,borderwidth=1,relief="solid")
        layer3_frame.pack()
        row=0
        title=tk.Label(layer3_frame,text=fct.get_text("options",translations,langue)[2])
        title.grid(row=row,column=0)
        row+=1
        #translation
        without=fct.get_text("without",translations,langue)
        #import images and resize
        gliss_sans0=PILImage.open("./images/54_glissiere0.JPG")
        gliss_sans0 = gliss_sans0.resize((350, 280))
        gliss_sans = ImageTk.PhotoImage(gliss_sans0)
        gliss_sans_label = tk.Label(layer3_frame, image=gliss_sans)
        gliss_sans_label.image = gliss_sans
        gliss_avec0=PILImage.open("./images/54_glissiere1.JPG")
        gliss_avec0 =gliss_avec0.resize((350,280))
        gliss_avec =ImageTk.PhotoImage(gliss_avec0)
        gliss_avec_label =tk.Label(layer3_frame,image=gliss_avec)
        gliss_avec_label.image=gliss_avec
        tasseau_avec0=PILImage.open("./images/54_glissiere2.JPG")
        tasseau_avec0=tasseau_avec0.resize((350,280))
        tasseau_avec=ImageTk.PhotoImage(tasseau_avec0)
        tasseau_avec_label=tk.Label(layer3_frame,image=tasseau_avec)
        tasseau_avec_label.image=tasseau_avec
        #variables pour les radiobuttons
        slide=tk.IntVar()
        #radiobutton : créer les widgets
        rb_sans = ttk.Radiobutton(layer3_frame, text=without[0], variable=slide, value=0)
        rb_avec = ttk.Radiobutton(layer3_frame, text=without[1], variable=slide, value=1)
        rb_tass_avec = ttk.Radiobutton(layer3_frame, text=without[1], variable=slide, value=2)
        #variables utilisées
        global fermeture_type,separ_check_row, separ_check_col
        #selon le type de fermeture sélectionné, afficher les options
        if fermeture_type == 0 : #couvercle glissé
            #avec/sans glissière : slide_check
            gliss_avec_label.grid(row=row,column=0)
            gliss_sans_label.grid(row=row,column=1)
            row+=1
            rb_avec.grid(row=row,column=0)
            rb_sans.grid(row=row,column=1)

        elif fermeture_type == 1 : #couvercle posé
            # si il y a des separations
            # avec/sans glissièe ou tasseau
            if separ_check_col and separ_check_row :
                gliss_avec_label.grid(row=row, column=0)
                gliss_sans_label.grid(row=row, column=1)
                tasseau_avec_label.grid(row=row, column=2)
                row += 1
                rb_avec.grid(row=row, column=0)
                rb_sans.grid(row=row, column=1)
                rb_tass_avec.grid(row=row, column=2)
            # si il n'y a pas de séparations
            # avec glissière ou avec tasseau
            else:
                gliss_avec_label.grid(row=row, column=0)
                tasseau_avec_label.grid(row=row, column=1)
                row += 1
                rb_avec.grid(row=row, column=0)
                rb_tass_avec.grid(row=row, column=1)

        elif fermeture_type == 2 or fermeture_type == 3 : #couvercle vissé
            #tasseau obligatoire
            tasseau_avec_label.grid(row=row,column=0)
        row+=1
        #click button
        def click3() :
            check=slide.get()
            global slide_check,tasseau_check
            if check ==0 : #la glissière a été choisie, pas de tasseau possible
                slide_check=True
                tasseau_check=False
            if check==1 : #pas de glissière, ni tasseau
                slide_check=False
                tasseau_check=False
            if check ==2:#tasseau choisi
                slide_check=False
                tasseau_check=True
            layer3_frame.destroy()
            checkmark_label = tk.Label(self.root, text="✓", font=("Arial", 16), fg="green")
            checkmark_label.pack()
        #ok_button
        ok_button=tk.Button(layer3_frame,text="OK",command=lambda:[click3(),self.layer4()])
        ok_button.grid(row=row,column=0,columnspan=layer3_frame.grid_size()[0])

    #couche 4 : choix de la forme de la poignée
    def layer4(self):
        layer4_frame = tk.Frame(self.root, borderwidth=1, relief="solid")
        layer4_frame.pack()
        row = 0
        lay4_title = tk.Label(layer4_frame, text=fct.get_text("options", translations, langue)[3],name="lay4_title")
        lay4_title.grid(row=row, column=0)
        row+= 1
        #get translations
        ferm_forme=fct.get_text("ferm_forme",translations,langue)
       #afficher les images pour les options
        images=[]
        for i in range(0,len(ferm_forme)):
            image_path = "./images/11_fermeture_forme" + str(i) + ".JPG"
            image = PILImage.open(image_path)
            global width  # largeur de l'écran
            # largeur des images par defaut
            width_image = 110
            # ajuster la hauteur (ratio 1:1)
            image = image.resize((width_image, width_image))
            photo = ImageTk.PhotoImage(image)
            images.append(photo)
            label = tk.Label(layer4_frame, image=images[i])
            label.image = images[i]
            label.grid(row=row, column=i,padx=5)
        row+=1
        #radiobuttons pour le choix de la forme de la poignée du couvercle
        forme=tk.IntVar()
        for i,forme_name in enumerate(ferm_forme) :
            rb_forme=ttk.Radiobutton(layer4_frame,text=forme_name,variable=forme,value=i)
            rb_forme.grid(row=row,column=i)
        row+=1
        #okbutton
        #ok_button on click
        def click4() :
            global fermeture_forme
            fermeture_forme=forme.get()
            for widget in layer4_frame.winfo_children() :
                if widget.winfo_name() != "lay4_title" :
                    widget.destroy()
            selected=fct.get_text("selected",translations,langue)
            selected_option=tk.Label(layer4_frame,text=selected+ferm_forme[fermeture_forme])
            selected_option.grid(row=1,column=0)
        ok_button=tk.Button(layer4_frame,text="OK",command=lambda:[click4(),self.layer5()])
        ok_button.grid(row=row,column=0,columnspan=layer4_frame.grid_size()[0])

    #couche 5 : format des dimensions (est-ce que l'on donne les dimensions
    def layer5(self) :
        """
        if not hasattr(self, 'layer5_frame'):
            self.layer5_frame = tk.Frame(self.root, borderwidth=1, relief="solid", name="layer5_frame")
            self.layer5_frame.pack()
        else:
            for widget in self.layer5_frame.winfo_children():
                widget.destroy()
        """
        layer5_frame=tk.Frame(self.root,borderwidth=1,relief="solid")
        layer5_frame.pack()
        row=0
        lay5_title = tk.Label(layer5_frame, text=fct.get_text("options", translations, langue)[4], name="lay5_title")
        lay5_title.grid(row=row,column=0,columnspan=3)
        row+=1
        #options de la longueur et de la largeur
        dim_format=tk.BooleanVar()
        dim_options=fct.get_text("dim_options",translations,langue)
        rb_option0=ttk.Radiobutton(layer5_frame,variable=dim_format,value=False)
        rb_option0.grid(row=row,column=0,sticky="e")
        rb0_label = tk.Label(layer5_frame, text=dim_options[0],name="0")
        rb0_label.grid(row=row,column=1,sticky="w",columnspan=2)
        row+=1
        rb_option1=ttk.Radiobutton(layer5_frame,variable=dim_format,value=True)
        rb_option1.grid(row=row,column=0,sticky="e")
        rb1_label=tk.Label(layer5_frame,text=dim_options[1],name="1")
        rb1_label.grid(row=row,column=1,columnspan=2,sticky="w")
        row+=1
        #option de la hauteur
        #label
        h_label=tk.Label(layer5_frame,text=fct.get_text("format",translations,langue))
        h_label.grid(row=row,column=1,sticky="e")
        #combobox choix
        h_text=fct.get_text("int_ext",translations,langue)
        dim_h_dropdown=ttk.Combobox(layer5_frame,values=h_text)
        dim_h_dropdown.set(h_text[0])
        dim_h_dropdown.grid(row=row,column=2,sticky="w")
        row+=1
        #ok_button
        #fonction du bouton
        def click5() :
            global dim_form_lo_la,dim_form_h
            dim_form_lo_la=dim_format.get()
            not_selected = str(int(not dim_form_lo_la))
            #
            temp=dim_h_dropdown.get()
            if "int" in temp : #temp is a string
                dim_form_h=False
            #supprimer l'option non sélectionnée et freeze le dropdown
            for widget in layer5_frame.winfo_children() :
                #enlever les radiobuttons
                if isinstance(widget, ttk.Radiobutton):
                    widget.destroy()
                # détruire le label de l'option non sélectionnée (name des rabiobutton "1" ou "0")

                elif widget.winfo_name()== not_selected :
                    widget.destroy()
                #désactiver la combobox
                elif isinstance(widget, ttk.Combobox) :
                    widget["state"] = "disabled"
                elif isinstance(widget,tk.Button):
                    widget.destroy()
            self.param()
        #bouton
        ok_button=tk.Button(layer5_frame,text="OK",command=lambda:[click5()])
        ok_button.grid(row=row,column=0,columnspan=layer5_frame.grid_size()[0])
    #---------------------------------------------------------------------------------
    #
    def end_param(self) :
       # tk.Button(self.root,text="valider")
        pass
    #---------------------------------------------------------------------------------
    #Paramètres des dimensions
    def param(self) :
        # Parameters frame
        param = tk.Frame(self.root, borderwidth=1, relief="solid")
        param.pack()
        # retrieve language lines
        epais = fct.get_text("ep", translations, langue)
        epais_title = fct.get_text("material", translations, langue)
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
        param_ok_button= tk.Button(param, text="OK", command=lambda: [param_button_click()])
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
            global ep, eplex
            ep = float(float_widgets[0].get())
            eplex = float(float_widgets[1].get())
            global format_dim
            format_dim = [form, [ep + ep, ep + ep, ep + eplex]]
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
            im=PILImage.open(file_name)
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
            im0 = PILImage.open(file_name)
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
            "recap":recap,
            "fermeture_type": fermeture_type,
            "fermeture_forme":fermeture_forme
        }
        #vis=0 pour pas de vis, 1 vis invisible,2 pour dépasse
        #couv_ras=false default couvercle à ras, true offset pour le couvercle
        #sep_check=false/true (glissière)
        #glissiere(slide)=false/true
        #temp json file storing the values for this instance
        file="./data/current_values.json"
        #open json file for writing
        with open(file,"w") as json_file :
            json.dump(data,json_file,indent=4)
        self.root.destroy()