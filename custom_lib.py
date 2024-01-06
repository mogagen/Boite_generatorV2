#librairie de fonctions usuelles

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np
from stl import mesh


# Languages

def load_translations(filename):
    """
    Load translations from a JSON file.
    Args:
    - filename (str): The name of the JSON file to load.
    Returns:
    - translations (dict): Translations loaded from the file.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            translations = json.load(file)
            return translations
    except FileNotFoundError:
        print(f"Le fichier de traductions '{filename}' n'a pas été trouvé.")
        return {}
    except json.JSONDecodeError:
        print(f"Erreur de décodage JSON dans '{filename}'. Assurez-vous qu'il est bien formaté.")
        return {}

def get_text(key, translations, language):
    """
    Access translation text based on a key, language, and translations dictionary.
    Args:
    - key (str): The key for the translation text.
    - translations (dict): The translations dictionary.
    - language (str): The language for which to retrieve the translation.
    Returns:
    - text (str): The translated text for the given key and language.
    """
    if language in translations and key in translations[language]:
        return translations[language][key]
    else:
        return f"Texte introuvable pour la clé '{key}' en langue '{language}'"
#-------------------------------------------------------------------------------------------------
# Calculations for drawings

def calc_encoche(ltot, ep, enc_def):
    """
    Calculate the dimensions of notches (encoche) to achieve uniform size.
    Args:
    - ltot (float): Total length of the side.
    - ep (float): Thickness.
    - enc_def (float): Default size of the notch.
    Returns:
    - [nb, enc] (list): Number of notches and adjusted notch length.
    """
    nb = round((ltot - 2 * ep) / enc_def)
    if (nb % 2) == 0:
        nb += 1
    if nb < 3:
        nb = 3
    enc = round((ltot - 2 * ep) / nb, 3)
    return [nb, enc]

# Drawings

def rect_avec_cote(width, height, ax):
    """
    Draw a rectangle with dimensions and arrows indicating width and height.
    Args:
    - width (float): Width of the rectangle.
    - height (float): Height of the rectangle.
    - ax (matplotlib.axes._axes.Axes): Matplotlib axes object.
    Returns:
    - None
    """
    w = 1
    h = w * (height / width)
    rectangle = patches.Rectangle((0, 0), w, h, edgecolor='r', facecolor='none')
    ax.add_patch(rectangle)
    ax.set_xlim(-0.3, w + 0.1)
    ax.set_ylim(-0.3, h + 0.1)
    x_start = 0
    y = -0.1
    x_end = w
    y_start = 0
    x = -0.1
    y_end = h
    ax.annotate('', xy=(x_start, y), xytext=(x_end, y), arrowprops=dict(arrowstyle='|-|', lw=1, color='black'))
    ax.annotate('', xy=(x, y_start), xytext=(x, y_end), arrowprops=dict(arrowstyle='|-|', lw=1, color='black'))
    dimension_label = f'{width} mm'
    x_label = (x_start + x_end) / 2
    y_label = y + 0.02
    ax.text(x_label, y_label, dimension_label, fontsize=10, color='black', ha='center')
    dimension_label1 = f'{height} mm'
    y1_label = (y_start + y_end) / 2
    x1_label = x - 0.07
    ax.text(x1_label, y1_label, dimension_label1, fontsize=10, color='black', va='center', rotation=90)

def draw_path(vertices):
    """
    Create a PathPatch from a list of vertices.
    Args:
    - vertices (list): List of (x, y) vertices.
    Returns:
    - path_patch (matplotlib.patches.PathPatch): Matplotlib PathPatch object.
    """
    codes = [Path.MOVETO]
    for i in range(0, len(vertices) - 2):
        codes.append(Path.LINETO)
    codes.append(Path.CLOSEPOLY)
    custom_path = Path(vertices, codes)
    path_patch = patches.PathPatch(custom_path, facecolor='none', edgecolor='red', linewidth=1)
    return path_patch

def create_figure(patch, w, h):
    """
    Create a Matplotlib figure with a PathPatch.
    Args:
    - patch (matplotlib.patches.PathPatch): Matplotlib PathPatch object.
    - w (float): Width of the figure.
    - h (float): Height of the figure.
    Returns:
    - None
    """
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor('none')
    ax.add_patch(patch)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)

def configure_path_export(w, h):
    """
    Configure path export settings for Matplotlib.
    Args:
    - w (float): Width of the exported image.
    - h (float): Height of the exported image.
    Returns:
    - None
    """
    plt.axis('off')
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.gcf().set_size_inches(w, h)
    
def configure_path_pdf(name,w, h):
    # Get the current Axes object
    ax = plt.gca()  # This gets the Axes object, which includes x-axis and y-axis
    # Set the x-axis and y-axis limits
    ax.set_xlim(-0.1, w + 0.1) 
    ax.set_ylim(-0.1, h + 0.1) 
    ax.text((w/3),(3*h/4),name,fontsize=20,ha="left",va="center")
    plt.axis('off')
    plt.margins(0.5, 0.5)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)

#---------------------------------------------------------------------------------------------
#STL functions

def create_parallel_vertices(x, y, z, width, length, height):
    """
    Create the vertices list for a cube given its dimensions and the coordinates of the rear top right corner.
    Args:
    - x (float): x-coordinate of the rear top right corner.
    - y (float): y-coordinate of the rear top right corner.
    - z (float): z-coordinate of the rear top right corner.
    - width (float): Width of the cube (parallel to the y-axis).
    - length (float): Length of the cube (parallel to the x-axis).
    - height (float): Height of the cube (parallel to the z-axis).
    Returns:
    - vertices (np.ndarray): Array containing the vertices of the cube.
    """
    # Calculate the coordinates of the other corners based on the rear top right corner (x, y, z)
    front_bottom_left = [x - length, y - width, z]
    front_bottom_right = [x, y - width, z]
    front_top_right = [x, y, z]
    front_top_left = [x - length, y, z]
    rear_bottom_left = [x - length, y - width, z - height]
    rear_bottom_right = [x, y - width, z - height]
    rear_top_right = [x, y, z - height]
    rear_top_left = [x - length, y, z - height]

    # Define the vertices of the cube
    vertices = np.array([
        front_bottom_left,
        front_bottom_right,
        front_top_right,
        front_top_left,
        rear_bottom_left,
        rear_bottom_right,
        rear_top_right,
        rear_top_left
    ])

    return vertices

def create_parallel_faces():
    """
    Create the faces list for a parallelepiped (rectangular prism) with triangular faces given its vertices.
    """
    faces = np.array([[0, 2, 3], [0, 2, 1],
                      [1, 2, 6], [1, 6, 5],
                      [4, 6, 5], [4, 6, 7],
                      [0, 4, 7], [0, 3, 7],
                      [3, 7, 6], [3, 6, 2],
                      [0, 4, 5], [0, 5, 1]])
    return faces

def fuse_mesh(mesh1, mesh2):
    """
    Fuse (combine) two mesh objects into a single mesh.
    Args:
    - mesh1 (mesh.Mesh): The first mesh to be fused.
    - mesh2 (mesh.Mesh): The second mesh to be fused.
    Returns:
    - fused_mesh (mesh.Mesh): Fused mesh object.
    """
    fused_vertices = np.concatenate((mesh1.vectors, mesh2.vectors), axis=0)
    # Create a single mesh object for the fused geometry
    fused_mesh = mesh.Mesh(np.zeros(len(fused_vertices), dtype=mesh.Mesh.dtype))
    fused_mesh.vectors = fused_vertices
    return fused_mesh

def create_equerre(x, y, z, length, width, height, epais):
    """
    Create an "équerre" (L-shaped structure) mesh.
    Args:
    - x (float): X-coordinate of the rear top right corner.
    - y (float): Y-coordinate of the rear top right corner.
    - z (float): Z-coordinate of the rear top right corner.
    - length (float): Length of the "équerre."
    - width (float): Width of the "équerre."
    - height (float): Height of the "équerre."
    - epais (float): Thickness of the "équerre."
    Returns:
    - equerre (mesh.Mesh): Mesh representing the "équerre."
    """
    side_width = create_parallel_volume(x, y, z, width, epais, height)
    side_length = create_parallel_volume(x - epais, y, z, epais, length - epais, height)
    equerre = fuse_mesh(side_width, side_length)
    return equerre

def create_parallel_volume(x, y, z, width, length, height):
    """
    Create a parallelepiped (box-like structure) mesh.
    Args:
    - x (float): X-coordinate of the rear top right corner.
    - y (float): Y-coordinate of the rear top right corner.
    - z (float): Z-coordinate of the rear top right corner.
    - width (float): Width of the parallelepiped.
    - length (float): Length of the parallelepiped.
    - height (float): Height of the parallelepiped.
    Returns:
    - parallelepiped (mesh.Mesh): Mesh representing the parallelepiped.
    """
    # Create the vertices and faces
    vertices = create_parallel_vertices(x, y, z, width, length, height)
    faces = create_parallel_faces()
    # Create the mesh
    parallelepiped = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j, vertex in enumerate(face):
            parallelepiped.vectors[i][j] = vertices[vertex]
    return parallelepiped
    
def mirror_mesh(original_mesh, axis='x'):
    """
    Create a mirrored copy of a mesh along the specified axis of symmetry.
    Args:
    - original_mesh (mesh.Mesh): The original mesh to be mirrored.
    - axis (str): The axis of symmetry ('x', 'y', or 'z').
    Returns:
    - mirrored_mesh (mesh.Mesh): Mirrored mesh object.
    """
    # Create a copy of the original mesh
    mirrored_mesh = mesh.Mesh(original_mesh.data.copy())
    # Determine the axis of symmetry and negate the corresponding coordinates
    if axis == 'x':
        mirrored_mesh.vectors[:, :, 0] = -mirrored_mesh.vectors[:, :, 0]
    elif axis == 'y':
        mirrored_mesh.vectors[:, :, 1] = -mirrored_mesh.vectors[:, :, 1]
    elif axis == 'z':
        mirrored_mesh.vectors[:, :, 2] = -mirrored_mesh.vectors[:, :, 2]
    else:
        raise ValueError("Invalid axis. Please use 'x', 'y', or 'z'.")
    return mirrored_mesh

#--------------------------------------------------------------------------------------