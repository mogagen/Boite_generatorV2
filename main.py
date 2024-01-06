#Boite generator
#Morgane Gen
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import filedialog
import custom_lib as fct
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from stl import mesh
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table,Paragraph,PageBreak
from reportlab.platypus import Image as rpImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from svglib.svglib import svg2rlg
import io
import cairosvg
import time

#-------------------------------------------------------------------------------------------------------
#Variables
#convertir de mm en inch (pour matplotlib)
mm=1/25.4
#scale stl in mm (default unit is cm)
scaling_factor=0.1
#longueur - length (mm)
lo = 370
#largeur - width (mm)
la = 330
#hauteur  - height (mm)
h = 65
#tableau dimensions
dimensions=[lo, la, h]
#format dimensions (dimensions internes ou externs) : True = externes, False = internes
#épaisseur bois - wood thickness (mm) (corps - body)
ep = 4
#épaisseur plexiglas - plexi thickness (mm) (couvercle - lid)
eplex = 4
#largeur approximative des créneaux mm
enc_def=20
enc_def=enc_def*mm
# Fixation
ep_fix = 2  # mm Height
side_larg = 10  # mm Width
side_long = 15  #mm Length
#colonnes et lignes
separ_check=False
columns=1
rows=1
#type de fermeture
fermeture_type=0
fermeture_forme=0
#options
langues_dispo={"English":"EN","Francais":"FR"}
langue="FR"
translations = fct.load_translations("dict_langues.json")
projet="projet"
save_path=""
#------------------------------------------------------------------------------------------------------
#main window
root = tk.Tk()
root.geometry('800x750+420+30')
root.title("Boite Generator")
root.resizable(False,False)
# Configure the column to expand
root.grid_columnconfigure(0, weight=1)
#Langues
lang=tk.Frame(root, borderwidth=1, relief="solid")
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
button = tk.Button(lang, text="OK", command=lambda:[lang_button_click(),lang.destroy(),param()])
button.pack()
#---------------------------------------------------------------------------------
#Paramètres des dimensions
def param() :
    # Parameters frame
    param = tk.Frame(root, borderwidth=1, relief="solid")
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
    param_ok_button= tk.Button(param, text="OK", command=lambda: [param_button_click(), dimensions_principales()])
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
def dimensions_principales() :
    dimens = tk.Frame(root, borderwidth=1, relief="solid")
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
    ok_button = tk.Button(dimens, text="OK", command=lambda: [dimens_ok_click(),recapitulatif()])
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
def recapitulatif() :
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
    recapitulatif_affiche()

def recapitulatif_affiche() :
    recap = ttk.Frame(root, borderwidth=1, relief="solid")
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
        for frame in root.winfo_children():
            if isinstance(frame, tk.Frame):
                frame.destroy()
            if isinstance(frame,ttk.Frame) :
                frame.destroy()
    next_txt=fct.get_text("next",translations,langue)
    next_button=tk.Button(text=next_txt,command=lambda:[plt.close(fig),destroy_all_frames(),next_button.destroy(),separation()])
    next_button.grid(row=4)

def separation() :
    separ = ttk.Frame(root, borderwidth=1, relief="solid")
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
            fermeture()
        #non valide
        else:
            warning=tk.Label(separ,text=try_again)
            warning.grid(row=row, column=0)
    #ok button
    ok_button=tk.Button(separ,text="OK",command=lambda: on_click())
    ok_button.grid(row=row+1)

def fermeture():
    fermeture = ttk.Frame(root, borderwidth=1, relief="solid")
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
    confirm_button = tk.Button(fermeture, text="OK", command=lambda:[choose_option(),choose_save_directory()])
    confirm_button.grid(row=rowf)
def choose_save_directory() :
    save_directory = ttk.Frame(root, borderwidth=1, relief="solid",)
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
            generate_files()
        else:
            # User canceled the dialog
            save_check=tk.Label(save_directory,text=save[2])
            save_check.pack()

    label = tk.Label(save_directory,text=save[0])
    label.pack()
    #button
    save_button=tk.Button(save_directory,text=save[1],command=lambda:[open_directory_dialog()])
    save_button.pack()
def generate_files() : #bouton qui ferme le GUI
    gen_files = tk.Frame(root)
    gen_files.grid(row=3, sticky="ew", padx=10, pady=10)
    txt=fct.get_text("generate",translations,langue)
    ok_button =tk.Button(gen_files,text=txt,command=lambda:root.quit())
    ok_button.pack()
#window loop
root.mainloop()
root.destroy()
#----------------------------------------------------------------------------------------------------------------------
#######################################################################################################################
#creer le nom de la boite
name_boite=str(int(lo))+"x"+str(int(la))+"x"+str(int(h))
namedir=save_path+"/"+projet+"_"+name_boite
if not os.path.exists(namedir):
    # If it doesn't exist, create the directory
    os.makedirs(namedir)
namedir2=str(namedir)
namedir=namedir+"/"+projet+"_"
#recapitulatif
title_recap=fct.get_text("dim",translations,langue)
title_recap+=fct.get_text("ep",translations,langue)
title_recap+=fct.get_text("sep",translations,langue)[0:2]
values_recap=dimensions
values_recap.append(columns)
values_recap.append(rows)
recap=[title_recap,values_recap]
#FIN DE L'ENTREE DES PARAMETRES
#----------------------------------------------------------------------------------
#############################
#GENERATION DES FICHIERS    #
#############################
#----------------------------------------------------------------------------------
#FERMETURES_0 - generation des stl
# Create the mesh objects
#creation de la piece - coin closed
if fermeture_type == 0 :
    z_coord=0
    closed0 = fct.create_equerre(0, 0, z_coord, side_long, side_larg, 5,ep_fix)
    z_coord+=ep_fix
    closed1 = fct.create_parallel_volume(ep, ep, ep_fix, side_larg + ep, side_long + ep, ep_fix)
    inter1=fct.fuse_mesh(closed0,closed1)
    z_coord+=eplex
    closed2 = fct.create_equerre(0, 0,z_coord,side_long, side_larg, eplex, ep_fix)
    inter2=fct.fuse_mesh(inter1,closed2)
    z_coord+=ep_fix
    closed3 = fct.create_parallel_volume(ep, ep, z_coord, side_larg + ep, side_long + ep, ep_fix)
    ferm_closed=fct.fuse_mesh(inter2,closed3)
    #Save stl
    scaled_closed = mesh.Mesh(ferm_closed.data.copy())  # Create a copy of the cube
    scaled_closed.data['vectors'] *= scaling_factor  # Scale down the vertices
    name_closed=namedir+"closing1"+name_boite+".stl"
    scaled_closed.save(name_closed)
    #coin_closed_2
    ferm_closed=fct.mirror_mesh(scaled_closed,axis="y")
    name_closed2=namedir+"closing4"+name_boite+".stl"
    ferm_closed.save(name_closed2)
    #....................................................................
    #coin open gauche (closed0+closed1+newpiece+closed3
    z_coord=eplex+ep_fix
    openl2=fct.create_parallel_volume(ep,0,z_coord,ep_fix,side_long+ep,eplex)
    inter2_1=fct.fuse_mesh(inter1,openl2)
    ferm_open_left=fct.fuse_mesh(inter2_1,closed3)
    #save stl
    scaled_openl=mesh.Mesh(ferm_open_left.data.copy())
    scaled_openl.data['vectors']*=scaling_factor
    name_open_left=namedir+"closing2"+name_boite+".stl"
    scaled_openl.save(name_open_left)
    #...............................................................................
    #coin open droite (mirror of open_left)
    ferm_open_right=fct.mirror_mesh(scaled_openl,axis="y")
    name_openr=namedir+"closing3"+name_boite+".stl"
    ferm_open_right.save(name_openr)

#------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#PIECES de la BOITE
#convertir en inch pour la suite
dim_temp = [round(element*mm,3) for element in dimensions]
dimensions=dim_temp.copy()
lo=dimensions[0]
la=dimensions[1]
h=dimensions[2]
ep=dimensions[3]
eplex=dimensions[4]
ep_fix = round(ep_fix*mm,3)
#colonnes et lignes
h_sep=h-ep #hauteur des séparations
# lo : distance x entre les separations
dist_x_rows=(lo-2*ep)/rows
#point milieu des encoches
x_h_enc_rows=[]
x_h_enc_rows.append(ep+dist_x_rows)
for i in range(1,rows-1) :
    x=x_h_enc_rows[-1]+dist_x_rows
    x_h_enc_rows.append(x)
#la distance x entre séparations
dist_x_col= (la - 2 * ep) / columns
#point milieu des encoches
#columns-1, calculate milieu de l'encoche
x_h_enc_col=[]
x_h_enc_col.append(la - (ep + dist_x_col))
for i in range(1,columns-1) :
    x= x_h_enc_col[-1] - dist_x_col
    x_h_enc_col.append(x)
#dimensions fermeture type 0
side_larg =round(side_larg*mm,3)
side_long = round(side_long*mm,3)
#................................................................................
#listes de points
#BASE
'''
    Base de la boite  - box base
    dimensions lo x la, avec encoches env enc_def x ep
'''
#coins de la base
bot_left=(0,0)
top_left=(0,la)
top_right=(lo,la)
bot_right=(lo,0)
#Base - COTES LONGUEUR (lo)
#calculer les encoches
tab_enc_lo=fct.calc_encoche(lo,ep,enc_def)
nb_enc=tab_enc_lo[0]
enc=tab_enc_lo[1]
enc_h=round(ep,3)
#coordonnees sur la longueur bas
lo_bas=[]
#point de départ
lo_bas.append((0,enc_h))
#2e et 3e point
px0=ep+enc
py0=enc_h
py1=0
lo_bas.append((px0,py0))
lo_bas.append((px0,py1))
nb_enc-=1
#points suivants par couple de points (px0,py0) et (px0,py1)
for i in range(0,nb_enc-1):
    px0=px0+enc
    if py0==enc_h :
        py0=0
        py1=enc_h
    else :
        py0=enc_h
        py1=0
    lo_bas.append((px0,py0))
    lo_bas.append((px0,py1))
#point final
px0=px0+(enc+ep)
lo_bas.append((px0,enc_h))
#coordonnes sur la longueur haut (symétrie de lo_bas)
lo_haut=[]
#coordonnee y de depart (x sont les mêmes que pour lo_bas)
try0=round(top_right[1],3)
#symetrie (la ligne part par contre depuis top_right)
for p in reversed(lo_bas):
    px=p[0]
    if p[1]==enc_h:
        py=try0-enc_h
    else :
        py=try0
    lo_haut.append((px,py))
#sortie : lo_bas, lo_haut
#...........................
#Base - COTES LARGEURS (la)
#calculer les encoches
tab_enc_la=fct.calc_encoche(la,ep,enc_def)
nb_enc=tab_enc_la[0]
enc=tab_enc_la[1]
#coordonnees large gauche (départ depuis top_left)
la_left=[]
#point départ depuis top_left
px0=0
py0=top_left[1]-ep
py1=py0-enc
nb_enc-=1
la_left.append((px0,py1))
#points suivants par couple de points (px0,py0) et (px0,py1)
for i in range(0,nb_enc):
    if px0==0 :
        px0=enc_h
    else :
        px0=0
    py0=py0-enc
    py1=py1-enc
    la_left.append((px0,py0))
    la_left.append((px0,py1))
#coordonees large droite (symetrie de la_left)
la_right=[]
#coordonnee x de depart (y sont les mêmes que pour la_left)
brx=bot_right[0]
#symetrie (la ligne part par contre depuis top_right)
for p in reversed(la_left):
    py=p[1]
    if p[0]==enc_h:
        px=brx-enc_h
    else :
        px=brx
    la_right.append((px,py))
#sortie : la_right et la_left
#BASE vertices :
base_vertices=lo_bas+la_right+lo_haut+la_left
#..........................................................
#COTES_LONGUEUR
'''
    Cotes longueurs (cotés de la boite qui correspond au coté lo de la base)
    lo x h, avec encoches env enc_def x ep
'''
#quatres coins
bot_left=(0,0)
bot_right=(lo,0)
top_left=(0,h)
top_rigt=(lo,h)
#cotes_lo - BAS
    #bas de la pièce #symétrie de lo_haut
lo_bas2=[]
bly=bot_left[1]
for p in reversed(lo_haut):
    px=p[0]
    py=p[1]-la+enc_h
    lo_bas2.append((px,py))
#sortie : lo_bas
#cote_lo - HAUT
#rows-1, calculate milieu de l'encoche
if rows > 1 :
    lo_haut2 =[]
    py0=h
    py1=(h_sep/2)+ep
    #x_mid = dist_x_rows, x_h_enc_rows
    for x_mid in reversed(x_h_enc_rows) :
        px0 = x_mid + (ep / 2)
        px1 = x_mid - (ep / 2)
        enc_vertices = [(px0,py0),(px0,py1),(px1,py1),(px1,py0)]
        lo_haut2 += enc_vertices
#cote_lo : COTES HAUTEURS
#calculer les encoches
tab_enc_h=fct.calc_encoche(h,ep/2,enc_def)
nb_enc=tab_enc_h[0]
enc=tab_enc_h[1]
#coté droit de la hauteur sur le côté long
h_lo_left=[]
#cotés gauche(de haut en bas)
#coin de départ
px0=top_left[0]
py0=top_left[1]
if fermeture_type == 0 :
    #encoches pour la fermeture
    add_ferm_lo=[]
    tcx=px0+ep+side_long
    add_ferm_lo.append((tcx,py0))#0
    fpy1=py0-ep_fix
    add_ferm_lo.append((tcx,fpy1))#1
    add_ferm_lo.append((px0,fpy1))#2
    fpy2=fpy1-eplex
    add_ferm_lo.append((px0,fpy2))#3
    add_ferm_lo.append((tcx,fpy2))#4
    fpy3=fpy2-ep_fix
    add_ferm_lo.append((tcx,fpy3))
    add_ferm_lo.append((px0,fpy3))
#première encoche
h_lo_left.append((px0,py0))
py1=round(py0-enc,3)
h_lo_left.append((px0,py1))
nb_enc-=1
#points suivants par couple de points (px0,py0) et (px0,py1)
for i in range(0,nb_enc):
    if px0==0 :
        px0=enc_h
    else :
        px0=0
    py0=round(py0-enc,3)
    py1=round(py1-enc,3)
    h_lo_left.append((px0,py0))
    h_lo_left.append((px0,py1))
h_lo_left[-1]=bot_left
#côté gauche (de haut en bas)
h_lo_right=[]
brx=bot_right[0]
#symétrie de h_lo_right
for p in reversed(h_lo_left):
    py=p[1]
    px=brx-p[0]
    h_lo_right.append((px,py))
if fermeture_type == 0 :
    add_ferm_lo_right = []
    for p in reversed(add_ferm_lo) :
        py=p[1]
        px=brx-p[0]
        add_ferm_lo_right.append((px,py))
#sortie : h_lo_right,h_lo_left
#COTE_LO : vertices
if fermeture_type == 0 :
    cote_lo_vertices=lo_bas2+h_lo_right[:-1]+add_ferm_lo_right
    if rows>1 :
        cote_lo_vertices+=lo_haut2
    cote_lo_vertices+=add_ferm_lo+h_lo_left[1:]
if fermeture_type == 1 :
    cote_lo_vertices=lo_bas2+h_lo_right
    if rows>1 :
        cote_lo_vertices+=lo_haut2
    cote_lo_vertices+=h_lo_left
print(cote_lo_vertices)
#..............................................
#COTES LARGEURS
'''
    Cotes largeurs (cotés de la boite qui correspond au coté la de la base)
    la x h, avec encoches env enc_def x ep
'''
#quatres coins
bot_left=(0,0)
bot_right=(la,0)
top_left=(0,h)
top_rigt=(la,h)
#cotés largeur - BAS de la piece
#bas de la pièce
nb_enc=tab_enc_la[0]
enc=tab_enc_la[1]
la_bas2=[]
#point de départ
la_bas2.append((enc_h,enc_h))
#2e point et 3e
px0=enc_h+enc
py0=enc_h
py1=0
la_bas2.append((px0,py0))
la_bas2.append((px0,py1))
nb_enc-=1
#paire de point suivant
for i in range(0,nb_enc-1) :
    px0=px0+enc
    if py0 == enc_h :
        py0=0
        py1 = enc_h
    else :
        py0=enc_h
        py1=0
    la_bas2.append((px0,py0))
    la_bas2.append((px0,py1))
#dernier point
px=la-enc_h
py=enc_h
la_bas2.append((px,py))
#sortie : la_bas2
#cotés largeur - HAUTEURS
nb_enc=tab_enc_h[0]
enc=tab_enc_h[1]
#coté droit de la hauteur sur le côté long
h_la_left_int=[]#symétrie de h_lo_left
#cotés gauche(de haut en bas)
for p in h_lo_left :
    if p[0]==enc_h :
        px=0
    else :
        px=enc_h
    h_la_left_int.append((px,p[1]))
brx=bot_right[0]
if fermeture_type == 0 :
    #ajouter les encoches pour les fermetures
    add_ferm_closed = []
    add_ferm_open = []
    #top corner original
    tco=h_la_left_int[0]
    #top corner new -closed
    tcnx=tco[0]+side_larg
    add_ferm_closed.append((tcnx, tco[1]))#1
    py1=tco[1]-ep_fix
    add_ferm_closed.append((tcnx, py1))#2
    add_ferm_closed.append((tco[0], py1))#3
    py2=py1-eplex
    add_ferm_closed.append((tco[0], py2))#4
    add_ferm_closed.append((tcnx, py2))#5
    py3=py2-ep_fix
    add_ferm_closed.append((tcnx, py3))#6
    add_ferm_closed.append((tco[0], py3))#7
    h_la_left_closed= add_ferm_closed + h_la_left_int[1:]
    #top corner new - open
    tcnox=tco[0]+side_larg
    tcnoy=tco[1]-eplex-ep_fix
    add_ferm_open.append((tcnox,tcnoy))#0
    py1=tcnoy-ep_fix
    add_ferm_open.append((tcnox,py1))#1
    add_ferm_open.append((tco[0],py1))#2
    h_la_left_open=add_ferm_open+h_la_left_int[1:]
    #cote droite de bas en haut, symetrie de h_la_left
    h_la_right_closed=[]
    h_la_right_open=[]
    #symétrie de h_lo_right
    for p in reversed(h_la_left_closed):
        py=p[1]
        px=brx-p[0]
        h_la_right_closed.append((px, py))
    h_la_right_closed.pop(0)
    for p in reversed(h_la_left_open):
        py=p[1]
        px=brx-p[0]
        h_la_right_open.append((px, py))
if fermeture_type ==1 :
    h_la_right_int=[]
    for p in reversed(h_la_left_int) :
        py=p[1]
        px=brx-p[0]
        h_la_right_int.append((px,py))
#sortie : h_la_left,h_la_right
#create vertices list
#cote largeur
if fermeture_type == 0 :
    cote_la_closed_vertices= la_bas2 + h_la_right_closed + h_la_left_closed
    cote_la_open_vertices=la_bas2+h_la_right_open[1:]+h_la_left_open
if fermeture_type == 1 :
    cote_la_vertices = la_bas2+h_la_right_int+h_la_left_int
#................................................................................
#SEPARATIONS
ferm_ep=0 #epaisseur de l'encoche en haut de la pièce
if fermeture_type == 0 :
    ferm_ep=eplex+ep_fix
if fermeture_type == 1 :
    ferm_ep = eplex
h_sep=h-ep #hauteur des pieces
sep_cote=[(ep,h_sep-ferm_ep),(ep,h_sep),(0,h_sep),(0,h_sep/2),(ep,h_sep/2),(ep,0)]
h_enc=(h_sep-ferm_ep)/2 #hauteur des encoches
#SEPARATIONS _LONGUEURS - encoches : nb_lignes-1
#vertices
#coté de la pièces
sep_lo_left=sep_cote.copy()
sep_lo_right=[]
for p in reversed(sep_lo_left) :
    px=lo-p[0]
    py=p[1]
    sep_lo_right.append((px,py))
#bas de la pièce
sep_lo_bas=[]
#rows-1, calculate milieu de l'encoche
for x_mid in x_h_enc_rows :
    px0=x_mid-(ep/2)
    px1=x_mid+(ep/2)
    enc_vertices=[(px0,0),(px0,h_enc),(px1,h_enc),(px1,0)]
    sep_lo_bas+=enc_vertices
sep_lo_vertices=sep_lo_left+sep_lo_bas+sep_lo_right+[sep_lo_left[0]]
#...........................................................................
#SEPARATIONS LARGEURS - encoches : columns-1
#cotés
sep_la_left=sep_cote.copy()
sep_la_right=[]
for p in reversed(sep_la_left) :
    px=la-p[0]
    py=p[1]
    sep_la_right.append((px,py))
#haut de la piece
sep_la_haut=[]
py0=h_sep-ferm_ep
py1=py0-h_enc
for x_mid in x_h_enc_col :
    px0=x_mid+(ep/2)
    px1=x_mid-(ep/2)
    enc_vertices=[(px0,py0),(px0,py1),(px1,py1),(px1,py0)]
    sep_la_haut+=enc_vertices
#vertices
sep_la_vertices=sep_la_left+sep_la_right+sep_la_haut+[sep_la_left[0]]
#...........................................................................
#entrees : base_vertices, cote_lo_vertices,cote_la_vertices
pieces=fct.get_text("pieces",translations,langue)
#GENERATE with MATPLOTLIB FIG
# Create a buffer  to store the images to add to pdf
buffer_list=[]
#BASE
#draw path using vertices list
base_patch=fct.draw_path(base_vertices)
# Create a Matplotlib figure and axis
fct.create_figure(base_patch,lo,la)
fct.configure_path_export(lo,la)
# Export the figure to an SVG file
name_svg=namedir+pieces[0]+"_"+name_boite+".svg"
plt.savefig(name_svg, format="svg")
#pdf
base_patch.set_linewidth(3)
fct.configure_path_pdf(pieces[0],lo,la)
buffer=io.BytesIO()
plt.savefig(buffer,format='png')
buffer_list.append([buffer,lo])
#COTE_LO
cote_lo_patch=fct.draw_path(cote_lo_vertices)
# Create a Matplotlib figure and axis
fct.create_figure(cote_lo_patch,lo,h)
fct.configure_path_export(lo,h)
# Export the figure to an SVG file
name_svg=namedir+pieces[1]+"_"+name_boite+".svg"
plt.savefig(name_svg, format="svg")
#pdf
cote_lo_patch.set_linewidth(3)
fct.configure_path_pdf(pieces[1],lo,h)
buffer2=io.BytesIO()
plt.savefig(buffer2,format='png')
buffer_list.append([buffer2,lo])
if fermeture_type == 0 :
    #COTE_LA_CLOSED
    cote_la_patch_c=fct.draw_path(cote_la_closed_vertices)
    # Create a Matplotlib figure and axis
    fct.create_figure(cote_la_patch_c,la,h)
    fct.configure_path_export(la,h)
    # Export the figure to an SVG file
    name_svg=namedir+pieces[2]+"_"+"_"+name_boite+".svg"
    plt.savefig(name_svg, format="svg")
    #pdf
    cote_la_patch_c.set_linewidth(3)
    fct.configure_path_pdf(pieces[2],la, h)
    buffer4 = io.BytesIO()
    plt.savefig(buffer4, format='png')
    buffer_list.append([buffer4,la])
    #COTE_LA_OPEN
    cote_la_patch_o=fct.draw_path(cote_la_open_vertices)
    # Create a Matplotlib figure and axis
    fct.create_figure(cote_la_patch_o,la,h-(eplex+ep_fix))
    fct.configure_path_export(la,h-(eplex+ep_fix))
    # Export the figure to an SVG file
    name_svg=namedir+pieces[3]+"_"+"_"+name_boite+".svg"
    plt.savefig(name_svg, format="svg")
    #pdf
    cote_la_patch_o.set_linewidth(3)
    fct.configure_path_pdf(pieces[3],la,h-(eplex+ep_fix))
    buffer3=io.BytesIO()
    plt.savefig(buffer3, format='png')
    buffer_list.append([buffer3,la])
if fermeture_type == 1 :
    #COTE_LA
    cote_la_patch=fct.draw_path(cote_la_vertices)
    # Create a Matplotlib figure and axis
    fct.create_figure(cote_la_patch, la, h)
    fct.configure_path_export(la, h)
    # Export the figure to an SVG file
    name_svg = namedir + pieces[4] + "_" + "_" + name_boite + ".svg"
    plt.savefig(name_svg, format="svg")
    #pdf
    cote_la_patch.set_linewidth(3)
    fct.configure_path_pdf(pieces[4],la, h)
    buffer5=io.BytesIO()
    plt.savefig(buffer5, format='png')
    buffer_list.append([buffer5,la])
#SEPARATIONS_LO
# Create a Matplotlib figure and axis
sep_lo_patch=fct.draw_path(sep_lo_vertices)
fct.create_figure(sep_lo_patch,lo,h_sep)
fct.configure_path_export(lo,h_sep)
# Export the figure to an SVG file
name_svg = namedir + pieces[6] + "_" + "_" + name_boite + ".svg"
plt.savefig(name_svg, format="svg")
#pdf
sep_lo_patch.set_linewidth(3)
fct.configure_path_pdf(pieces[6],lo,h_sep)
buffer6=io.BytesIO()
plt.savefig(buffer6,format='png')
buffer_list.append([buffer6,lo])
#SEPARATION_LA
# Create a Matplotlib figure and axis
sep_la_patch=fct.draw_path(sep_la_vertices)
fct.create_figure(sep_la_patch,la,h_sep)
fct.configure_path_export(la,h_sep)
# Export the figure to an SVG file
name_svg = namedir + pieces[7] + "_" + "_" + name_boite + ".svg"
plt.savefig(name_svg, format="svg")
#pdf
sep_la_patch.set_linewidth(3)
fct.configure_path_pdf(pieces[7],la,h_sep)
buffer7=io.BytesIO()
plt.savefig(buffer7,format='png')
buffer_list.append([buffer7,la])
#......................................................................
#LID-COUVERCLE
width=la-(2*ep)
if fermeture_type == 0 :
    length=lo-ep
if fermeture_type == 1 :
    length=lo-(2*ep)
outside_path = patches.Rectangle((0, 0), length, width, linewidth=1, edgecolor='b', facecolor='none')
#add forme d'ouverture
if fermeture_forme != 3 : #3=sans
    if fermeture_forme == 0 : #demi-cercle
        radius = round(10*mm,3)
        # Create a Path representing the half-circle
        theta = np.linspace(0, np.pi, 100)  # Range of angles for half-circle (0 to π radians)
        x = ep+(radius * np.sin(theta))
        y = (width/2)+(radius * np.cos(theta))
        # Create a PathPatch
        path = Path(np.column_stack((x, y)))
        # Add the straight vertical line
        path.vertices = np.concatenate((path.vertices, [[ep,(width/2)-radius], [ep,(width/2)+radius]]))
        handle_patch = patches.PathPatch(path,edgecolor='r',facecolor='none',lw=1)
    if fermeture_forme == 1 : #ruban
        ribbon_width=round(20*mm,3)
        slit=round(4*mm,3)
        handle_patch=patches.Rectangle((ep,(width/2)-(ribbon_width/2)),slit,ribbon_width,linewidth=1,edgecolor='r',facecolor="none")
    if fermeture_forme == 2 : #trou
        radius_hole = round(2*mm,3)
        handle_patch = patches.Circle((ep+(radius_hole/2),width/2),radius_hole,linewidth=1,edgecolor='r',facecolor='none')
fig, ax = plt.subplots(figsize=(length, width))
fig.patch.set_facecolor('none')
ax.add_patch(outside_path)
if fermeture_forme !=3 :
    ax.add_patch(handle_patch)
ax.set_aspect('equal', adjustable='box')
ax.set_xlim(0, length)
ax.set_ylim(0, width)
fct.configure_path_export(length,width)
# Export the figure to an SVG file
name_svg = namedir + pieces[5] + "_" + "_" + name_boite + ".svg"
plt.savefig(name_svg, format="svg")
#pdf
outside_path.set_linewidth(3)
if fermeture_forme != 3 :
    handle_patch.set_linewidth(3)
fct.configure_path_pdf(pieces[5],length,width)
buffer8=io.BytesIO()
plt.savefig(buffer8, format='png')
buffer_list.append([buffer8,length])
#-------------------------------------------------------------------------------------------------------------------------
######################
#PDF recapitulatif   #
######################
nb=fct.get_text("nb",translations,langue)
if fermeture_type == 0 :
    pieces_choisies=pieces[0:4]+pieces[5:]
    nb_pieces=["1x","2x","1x","1x",str(columns-1)+"x",str(rows-1)+"x"]
if fermeture_type == 1 :
    pieces_choisies=pieces[0:1]+pieces[4:]
    nb_pieces=["1x","2x","2x","1x",str(columns-1)+"x",str(rows-1)+"x"]
list_pieces=[pieces_choisies,nb_pieces]
# Create a PDF document with A4 page size
pdf_filename = namedir + "RECAP_" + "_" + name_boite + ".pdf"
document = SimpleDocTemplate(pdf_filename, pagesize=A4,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
#STYLES
#table style
table_style = [
    ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add black grid lines
    ('BACKGROUND', (0, 0), (-1, -1), colors.white),  # Remove any background color
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center-align text
]
# Define a custom style for the title
maintitle_style = getSampleStyleSheet()['Title']
maintitle_style.alignment = 1  # Center-align the title
maintitle_style.fontSize = 20  # Set the font size to 20pt
maintitle_style.spaceAfter = 10  # Adjust the value as needed
# Define a custom style for the title
title_style = getSampleStyleSheet()['Heading1']
title_style.alignment = 1  # Center-align the title
title_style.fontSize = 15  # Set the font size to 20pt
title_style.spaceBefore = 10  # Adjust the value as needed
title2_style = getSampleStyleSheet()['Heading2']
title2_style.alignment = 1  # Center-align the title
title2_style.fontSize = 12  # Set the font size to 20pt
title2_style.spaceBefore=3
#col width
col_width = 3*cm
#CREATE ELEMENTS
element_list=[]
# main title paragraph
main_title_text = projet+" - "+name_boite+" - Recap"
main_title_paragraph = Paragraph(main_title_text, maintitle_style)
element_list.append(main_title_paragraph)
#recap title
recap_title_text=fct.get_text("dimens",translations,langue)
recap_title_paragraph=Paragraph(recap_title_text,title_style)
element_list.append(recap_title_paragraph)
#recap table
recap_table = Table(recap)
recap_table.setStyle(table_style)
element_list.append(recap_table)
#nombres de pièces title
parts_title_text=fct.get_text("list_part",translations,langue)
parts_title_paragraph=Paragraph(parts_title_text,title_style)
element_list.append(parts_title_paragraph)
nb_pieces_title=fct.get_text("nb",translations,langue)
nb_pieces_paragraph=Paragraph(nb_pieces_title,title2_style)
element_list.append(nb_pieces_paragraph)
#nombres de pièces table
pieces_table=Table([list_pieces[0][0:5],list_pieces[1][0:5]])
pieces_table.setStyle(table_style)
element_list.append(pieces_table)
pieces_table2=Table([list_pieces[0][5:],list_pieces[1][4:]])
pieces_table2.setStyle(table_style)
element_list.append(pieces_table2)
#Notes


#
element_list.append(PageBreak())
image_text="Images"
image_paragraph=Paragraph(image_text,title_style)
element_list.append(image_paragraph)
#parts
## Initialize the maximum image height that can fit on the page
max_image_height_on_page=A4[1]-4*cm
image_width=500
dimmax = max(la, lo)
current_height=0
# Iterate through the buffer list and add each image to the list of elements
for buff in buffer_list :
    buff[0].seek(0)
    # Load the image using Pillow to get its dimensions
    image = Image.open(io.BytesIO(buff[0].read()))
    original_width, original_height = image.size
    #
    width=int(image_width*(buff[1]/dimmax))
    height=int(original_height*(width/original_width))
    #
    buff[0].seek(0)
    image_data = buff[0].read()
    image = rpImage(io.BytesIO(image_data), width=width, height=height)
    # Add the Image element to the list of elements
    if (current_height+height) > max_image_height_on_page :
        # Add a page break if necessary
        element_list.append(PageBreak())
        current_height = 0  # Reset the current height
    # Add the image to the element list
    element_list.append(image)
    current_height += height
# Build and save the PDF document
document.build(element_list)


