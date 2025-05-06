"""
----------------------------------------------------------------------------------------------------
THIS IS THE MAIN FILE FOR PROTPLOT PROJECT

The aim of this project is to create a universal way to deal with the '.pdb' extension
and to manage the protein files with pandas.
There are multiple functions regarding to the demonstration of the protein structure.


This file contains the functions given by the package. 
Be aware that this package was made for a University project in Hungary, PPKE ITK.

----------------------------------------------------------------------------------------------------


@authors: domedenes, viktoriaracz, maximilianpoku
"""

#-------------------------------------DEPENDENCIES--------------------------------------------------

#Importing the dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import urllib.request as urllib2
import io

from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go

import seaborn as sns
from matplotlib.colors import ListedColormap

#-------------------------------------FUNCTIONS-----------------------------------------------------

"""
The following part contains the developed functions. These functions just examples for the utilization of pandas df
versions of PDB files. If you use this package, feel free to be creative, and upgrade, modify these functions.


"""



#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------
#Function - read_pdb()

def read_pdb(pdb_code, chain = None):
    
    
    """ 
    Parameters
    ----------
    pdb_code : TYPE str
        The pdb entry ID under which a protein is annoted in the databank rcsb.org
        
    chain : TYPE str, optional
        The given chain identifier which should be returned. Important in alignements. The default is None, when all of the chains are returned.

    Returns
    -------
    out : Pandas df
        An easily managable form of the given protein structure file.
        
    NOTE THAT INTERNET CONNECTION IS NEEDED!

    """
    

    response = urllib2.urlopen(f'https://files.rcsb.org/download/{pdb_code}.pdb') #defining the url where the pdb file is located
    read_response = response.read()
    workable = io.BytesIO(read_response).readlines()
    what = [workable[i].decode('utf-8') for  i in range(len(workable))]
    
    

    temporary_outcome = list()
    for i in range(len(what)):
        temp = what[i]
        temp = temp[0:4]
        
        if temp == 'ATOM':
            
            temporary_outcome.append(what[i]) # if it is an atom then we load it
            
    
    #defining a dictionary based on the character places in the string
    data = {'atom_index':[temporary_outcome[i][6:11].replace(' ', '') for i in range(len(temporary_outcome))],
            'atom_type':[temporary_outcome[i][12:16].replace(' ', '')  for i in range(len(temporary_outcome))],
            'amino_type':[temporary_outcome[i][17:20].replace(' ', '') for i in range(len(temporary_outcome))],
            'chain_index':[temporary_outcome[i][21].replace(' ', '') for i in range(len(temporary_outcome))],
            'amino_index':[temporary_outcome[i][22:26].replace(' ', '') for i in range(len(temporary_outcome))],
            'x':[temporary_outcome[i][31:38].replace(' ', '') for i in range(len(temporary_outcome))],
            'y':[temporary_outcome[i][39:46].replace(' ', '') for i in range(len(temporary_outcome))],
            'z':[temporary_outcome[i][47:54].replace(' ', '') for i in range(len(temporary_outcome))],
            'b_factor':[temporary_outcome[i][61:67].replace(' ', '') for i in range(len(temporary_outcome))]
            }
    
    
    #defining the dataframe
    out = pd.DataFrame(data)
    
    #adjusting the desired format
    numeric_columns = ['atom_index', 'amino_index', 'x', 'y', 'z', 'b_factor']
    out[numeric_columns] = out[numeric_columns].astype('float64')
        
    if chain:
        out = out[out.chain_index == chain]
    
    else:
        print(f'No chain was defined, note that all posibble chains in the entry {pdb_code} is returned')
        
    return out

#example = protplot.read_pdb('6vxx', chain = 'A')
#example2 = protplot.read_pdb('6vxx')

#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------
#Function - plot_projection()

def plot_projection(protein_df, colorcode = 'default', atoms = 'all',
                    aminos = 'all', alpha = 1, marker = 'x', Title = None, figsave = None):
    """
    

    Parameters
    ----------
    protein_df : pandas df
        A pdb file loaded into a pandas dataframe.
        
    colorcode : dictionary, optional
        default : {'C' : 'black', 'N' : 'blue', 'O' : 'red', 'S' : 'yellow'}
        a dictionary containing the color for each main atom type
        
    atoms : str, optional
        which atoms to be plotted
        
    aminos : str, optional
        which AAs to be plotted
        
    alpha : 0-1 float, optional
        transpancy of the markes
        
    marker : str, optional
       types of the markers
       
    Title : str, optional
        title for the figure
    figsave : str, optional
        figname, if the export is desired

    Returns
    -------
    A matplotlib figure with 2D slices of a protein

    """
    
    
    plot_df = protein_df.copy() # no modification to be made
    
    if atoms != 'all':
        plot_df = plot_df[plot_df.atom_type.isin(atoms)] #filter for the given atoms
        
    if aminos != 'all':
        plot_df = plot_df[plot_df.amino_type.isin(aminos)] #filter for the given amino acids
        
    if colorcode == 'default':
        ccode = {'C' : 'black', 'N' : 'blue', 'O' : 'red', 'S' : 'yellow'} #dict for coloring
    else:
        ccode = colorcode.copy()
    
    #Defining the main type of the atoms for coloring
    defined_atoms = plot_df.atom_type.values
    defined_atoms = [element[0] for element in defined_atoms]
    plot_df['defined_atoms'] = defined_atoms
    datoms = np.unique(plot_df.defined_atoms)
    
    
    dpg = plot_df.groupby('defined_atoms')
    
    fig, axes = plt.subplots(nrows = 1, ncols = 3,figsize = (18,6)) #opening the figure
    for dat, plotter in dpg:
        
        axes[0].scatter(plotter.x.values[0], plotter.y.values[0], alpha = 1,
                        marker = marker, color = ccode[dat], label = dat) #just because the meaningful legend

        axes[0].scatter(plotter.x.values, plotter.y.values, alpha = alpha,
                        marker = marker, color = ccode[dat])
        axes[0].set_xlabel('X', fontsize = 14)
        axes[0].set_ylabel('Y', fontsize = 14)
        
        
        axes[1].scatter(plotter.x.values, plotter.z.values, alpha = alpha,
                        marker = marker, color = ccode[dat])
        axes[1].set_xlabel('X', fontsize = 14)
        axes[1].set_ylabel('Z', fontsize = 14)
        
        
        axes[2].scatter(plotter.z.values, plotter.y.values, alpha = alpha,
                        marker = marker, color = ccode[dat])
        axes[2].set_xlabel('Z', fontsize = 14)
        axes[2].set_ylabel('Y', fontsize = 14)
    
    
    
    fig.legend(fontsize = 16)
    
    if Title:
        fig.suptitle(Title, fontsize = 22)
    
    if figsave:
        plt.savefig(figsave, dpi = 200)
        
    plt.show()
    
#protplot.plot_projection(example, alpha = 0.55, aminos = ['CYS'], atoms = ['CA', 'SG'], 
#                Title = 'Test projection plot', figsave = 'test25.jpg')
    
 
    
#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------
# Function - plot_structure_3d()

def plot_structure_3d(
    protein_df1,
    protein_df2 = None,
    atoms1 = 'all', atoms2 = 'all',
    aminos1 = 'all', aminos2 = 'all',
    colorcode1 = 'default', colorcode2 = 'default',
    alpha1=1.0, alpha2=1.0,
    marker1='o', marker2='x',
    marker_size1=20, marker_size2=20,
    fig_size=(10, 10),
    Title=None, figsave=None
):
    """
    Static 3D scatter plot of one or two protein structures using matplotlib.

    Parameters
    ----------
    protein_df1, protein_df2 : pd.DataFrame
        DataFrames from `read_pdb()` for the proteins to be plotted.
    atoms1, atoms2 : list or 'all'
        List of atom types to include (e.g., ['CA']) or 'all'.
    aminos1, aminos2 : list or 'all'
        List of amino acids to include (e.g., ['CYS']) or 'all'.
    colorcode1, colorcode2 : dict, 'default', or 'b_factor'
        'default' = color by atom type,
        dict = manual color mapping,
        'b_factor' = gradient color by B-factor.
    alpha1, alpha2 : float
        Transparency of markers (0.0–1.0).
    marker1, marker2 : str
        Matplotlib marker symbols (e.g., 'o', '^').
    marker_size1, marker_size2 : float
        Size of the markers.
    fig_size : tuple
        Size of the figure in inches (width, height).
    Title : str
        Title of the plot.
    figsave : str or None
        If provided, path to save the figure (e.g., 'plot.png').

    Returns
    -------
    None
        Displays a 3D scatter plot of the protein structure(s).
    """

    def plot_single_structure(ax, df, atoms, aminos, colorcode, alpha, marker, marker_size, label_prefix):
        plot_df = df.copy()

        if atoms != 'all':
            plot_df = plot_df[plot_df.atom_type.isin(atoms)]

        if aminos != 'all':
            plot_df = plot_df[plot_df.amino_type.isin(aminos)]

        use_bfactor_gradient = (colorcode == 'b_factor')

        if use_bfactor_gradient:
            scatter = ax.scatter(
                plot_df.x.values,
                plot_df.y.values,
                plot_df.z.values,
                c=plot_df.b_factor.values,
                cmap='coolwarm',
                alpha=alpha,
                marker=marker,
                s=marker_size,
                label=f"{label_prefix}: B-factor"
            )
            plt.colorbar(scatter, ax=ax, label='B-factor')
        else:
            if colorcode == 'default':
                ccode = {'C': 'black', 'N': 'blue', 'O': 'red', 'S': 'yellow'}
            else:
                ccode = colorcode

            plot_df['defined_atoms'] = plot_df.atom_type.str[0]
            dpg = plot_df.groupby('defined_atoms')

            for dat, plotter in dpg:
                if dat in ccode:
                    ax.scatter(
                        plotter.x.values,
                        plotter.y.values,
                        plotter.z.values,
                        color=ccode[dat],
                        label=f"{label_prefix}: {dat}",
                        alpha=alpha,
                        marker=marker,
                        s=marker_size
                    )

    # Create plot
    fig = plt.figure(figsize=fig_size)
    ax = fig.add_subplot(111, projection='3d')

    plot_single_structure(ax, protein_df1, atoms1, aminos1, colorcode1, alpha1, marker1, marker_size1, 'P1')

    if protein_df2 is not None:
        plot_single_structure(ax, protein_df2, atoms2, aminos2, colorcode2, alpha2, marker2, marker_size2, 'P2')

    ax.set_xlabel('X', fontsize=14)
    ax.set_ylabel('Y', fontsize=14)
    ax.set_zlabel('Z', fontsize=14)

    if Title:
        ax.set_title(Title, fontsize=18)

    ax.legend(title='Atom Type')
    
    if figsave:
        plt.savefig(figsave, dpi=300)

    plt.tight_layout()
    plt.show()

#example usage:

# example2 = protplot.read_pdb('6vxx')
# example = protplot.read_pdb('7v7n')
# protplot.plot_structure_3d(example, example2, atoms1=['C'], atoms2=['C'], colorcode1={'C': 'green'}, colorcode2={'C': 'red'}, alpha1=0.9, alpha2=0.5, marker1='o', marker2='^',marker_size1=40, marker_size2=60)




#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------
#Function - plot_structure_3d()

# This function is an interactive version of the plot_structure_3d function using Plotly.


def plot_structure_3d_interactive(
    protein_df1,
    protein_df2=None,
    atoms1='all', atoms2='all',
    aminos1='all', aminos2='all',
    colorcode1='default', colorcode2='default',
    alpha1=1.0, alpha2=1.0,
    marker1='circle', marker2='circle',
    marker_size1=5, marker_size2=5,
    fig_width=1000, fig_height=1000,
    Title=None, figsave=None
):
    """
    Interactive 3D scatter plot of one or two protein structures using Plotly.

    Parameters
    ----------
    protein_df1, protein_df2 : pd.DataFrame
        DataFrames from `read_pdb()` for the proteins to be plotted.
    atoms1, atoms2 : list or 'all'
        List of atom types to include (e.g., ['CA']) or 'all'.
    aminos1, aminos2 : list or 'all'
        List of amino acids to include (e.g., ['GLY']) or 'all'.
    colorcode1, colorcode2 : dict, 'default', or 'b_factor'
        'default' = atom type coloring,
        dict = manual color mapping,
        'b_factor' = color by B-factor gradient.
    alpha1, alpha2 : float
        Marker opacity (0.0 to 1.0).
    marker1, marker2 : str
        Plotly marker symbol (e.g., 'circle', 'square').
    marker_size1, marker_size2 : float
        Size of the marker spheres.
    fig_width, fig_height : int
        Size of the interactive plot in pixels.
    Title : str
        Optional title for the plot.
    figsave : str or None
        If provided, saves the plot as an interactive HTML file.

    Returns
    -------
    None
        Opens an interactive 3D protein visualization.
    """

    fig = go.Figure()

    def add_structure_to_plot(df, atoms, aminos, colorcode, alpha, marker, marker_size, label_prefix):
        plot_df = df.copy()

        if atoms != 'all':
            plot_df = plot_df[plot_df.atom_type.isin(atoms)]

        if aminos != 'all':
            plot_df = plot_df[plot_df.amino_type.isin(aminos)]

        use_bfactor_gradient = (colorcode == 'b_factor')
        if not use_bfactor_gradient:
            if colorcode == 'default':
                ccode = {'C': 'black', 'N': 'blue', 'O': 'red', 'S': 'yellow'}
            else:
                ccode = colorcode
            plot_df['defined_atoms'] = plot_df.atom_type.str[0]

        if use_bfactor_gradient:
            fig.add_trace(go.Scatter3d(
                x=plot_df.x,
                y=plot_df.y,
                z=plot_df.z,
                mode='markers',
                marker=dict(
                    size=marker_size,
                    color=plot_df.b_factor,
                    colorscale='RdBu_r',
                    colorbar=dict(title='B-factor'),
                    opacity=alpha,
                    symbol=marker
                ),
                name=f"{label_prefix}: B-factor"
            ))
        else:
            for atom_type in plot_df['defined_atoms'].unique():
                subset = plot_df[plot_df['defined_atoms'] == atom_type]
                fig.add_trace(go.Scatter3d(
                    x=subset.x,
                    y=subset.y,
                    z=subset.z,
                    mode='markers',
                    marker=dict(
                        size=marker_size,
                        color=ccode.get(atom_type, 'gray'),
                        opacity=alpha,
                        symbol=marker
                    ),
                    name=f"{label_prefix}: {atom_type}"
                ))

    # Add first structure
    add_structure_to_plot(protein_df1, atoms1, aminos1, colorcode1, alpha1, marker1, marker_size1, 'P1')

    # Optional second structure
    if protein_df2 is not None:
        add_structure_to_plot(protein_df2, atoms2, aminos2, colorcode2, alpha2, marker2, marker_size2, 'P2')

    fig.update_layout(
        title=Title or '3D Protein Structure(s)',
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z'
        ),
        legend_title='Atom Type',
        width=fig_width,
        height=fig_height
    )

    if figsave:
        fig.write_html(figsave)

    fig.show()
    
    print('If the object is not showing, then you should save it as a HTML object, and open it independently from your IDE')
    
#example usage:
# example2 = protplot.read_pdb('6vyb')
# example = protplot.read_pdb('7v7n')

# protplot.plot_structure_3d_interactive(example2, atoms1=['CA'], colorcode1='b_factor', marker_size1=4, alpha1=0.9, figsave = 'test.html')


#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------

#FUNCTIONS FOR RAMACHADRAN PLOT
def calculate_dihedral(p1, p2, p3, p4):
    """
    Calculate the dihedral angle (in degrees) between four 3D points.

    Parameters:
        p1, p2, p3, p4: np.ndarray
            3D coordinates of four consecutive atoms.

    Returns:
        float: Dihedral angle in degrees.
    """
    b0 = -1.0 * (p2 - p1)
    b1 = p3 - p2
    b2 = p4 - p3

    b1 /= np.linalg.norm(b1)
    v = b0 - np.dot(b0, b1) * b1
    w = b2 - np.dot(b2, b1) * b1

    x = np.dot(v, w)
    y = np.dot(np.cross(b1, v), w)
    return np.degrees(np.arctan2(y, x))

def extract_phi_psi(df):
    """
    Extract phi and psi angles from a DataFrame of atomic coordinates.

    Parameters:
        df: pandas.DataFrame
            Must contain columns: ['atom_type', 'amino_index', 'x', 'y', 'z'].

    Returns:
        np.ndarray: Array of (phi, psi) tuples.
    """
    df = df[df['atom_type'].isin(['N', 'CA', 'C'])].copy()
    df = df.sort_values(by=['amino_index', 'atom_type'])

    # Build residue-wise coordinate dictionary
    residues = {}
    for res_id, group in df.groupby('amino_index'):
        atom_coords = {row['atom_type']: np.array([row['x'], row['y'], row['z']])
                       for _, row in group.iterrows()}
        if {'N', 'CA', 'C'}.issubset(atom_coords):
            residues[res_id] = atom_coords

    # Compute φ/ψ angles
    sorted_keys = sorted(residues.keys())
    angles = []

    for i in range(1, len(sorted_keys) - 1):
        prev_res = residues[sorted_keys[i - 1]]
        this_res = residues[sorted_keys[i]]
        next_res = residues[sorted_keys[i + 1]]

        try:
            phi = calculate_dihedral(prev_res['C'], this_res['N'], this_res['CA'], this_res['C'])
            psi = calculate_dihedral(this_res['N'], this_res['CA'], this_res['C'], next_res['N'])
            angles.append((phi, psi))
        except:
            continue

    return np.array(angles)

def plot_ramachandran(angles, cmap = 'Blues', scat_color = 'blue'):
    """
    Plots a Ramachandran plot with 2-level density contours and region labels.

    Parameters:
        angles (np.ndarray): Array of (phi, psi) angle pairs.
    """
    if len(angles) == 0:
        print("No valid φ/ψ angles to plot.")
        return

    phi, psi = angles[:, 0], angles[:, 1]

    plt.figure(figsize=(8, 8))

    levels = [.01, .1, .2, .3, .5, .7, .9, 1]

    # Filled KDE
    sns.kdeplot(
        x=phi,
        y=psi,
        fill=True,
        cmap=cmap,
        bw_adjust=0.7,
        levels=levels,
        thresh=1
    )

    #Contour lines
    sns.kdeplot(
        x=phi,
        y=psi,
        color='gray',
        bw_adjust=0.7,
        levels=levels,
        linewidths=1
    )
    
    plt.scatter(phi, psi, marker = '.', color = scat_color, alpha = 0.15)
    
    # Structural region labels
    plt.text(-40, -40, 'α Helix', fontsize=14, color='black', fontweight = 'bold')
    plt.text(-100, 100, 'β Sheet', fontsize=14, color='black', fontweight = 'bold')
    plt.text(50, 5, 'Left-handed α Helix', fontsize=14, color='black', fontweight = 'bold')

    plt.xlabel('Phi (φ)', fontsize=14)
    plt.ylabel('Psi (ψ)', fontsize=14)
    plt.title('Ramachandran Plot ', fontsize=18)
    plt.xlim(-180, 180)
    plt.ylim(-180, 180)
    plt.grid(True, color = 'lightgrey')
    plt.axhline(0, color='black', linestyle='-', linewidth = 2)
    plt.axvline(0, color='black', linestyle='-', linewidth = 2)
    plt.show()


# example = read_pdb('7v7n')
# torsion = extract_phi_psi(example)
# plot_ramachandran(torsion)


#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------     
#------------------------------------------------------------------------------------------------------


def Protein_alignment(df1, df2, chains = 'Combo_matrix'):
    '''
    

    Parameters
    ----------
    df1 : pandas dataframe
        PDB file loaded into a pandas dataframe
        
    df2 : pandas dataframe
        PDB file loaded into a pandas dataframe
        
    chains : list or str 'Combo_matrix', optional
        A list of which protein chain from df1 should be compared to df2
        Note that there is a merging step, according to the amino index

    Returns RMSD value and optinonal heatmap
    -------
        

    '''

    

    def center_coords(coords):
        centroid = coords.mean(axis=0)
        return coords - centroid, centroid

    def calculate_rmsd(coords1, coords2_aligned):
        return np.sqrt(np.mean(np.sum((coords1 - coords2_aligned) ** 2, axis=1)))
    
    if chains == 'Combo_matrix':
        
        c1, c2 = np.unique(df1.chain_index), np.unique(df2.chain_index)
        
        for_plot = []
        for cc1 in c1:
            for cc2 in c2:
                
                # Filter to Cα atoms only
                df1_ca = df1[(df1.atom_type == "CA") & (df1.chain_index == cc1)]
                df2_ca = df2[(df2.atom_type == "CA") & (df2.chain_index == cc2)]
            
                df_ca_merged = pd.merge(df1_ca, df2_ca, on = 'amino_index', suffixes = ['_1', '_2'])
                
                if len(df_ca_merged) == 0 :
                    print(f'Please check data, given chains {cc1} and {cc2} have no common amino index')
                    
                
                # Extract coordinates
                coords1 = df_ca_merged[["x_1", "y_1", "z_1"]].to_numpy()
                coords2 = df_ca_merged[["x_2", "y_2", "z_2"]].to_numpy()
            
                # Center both
                coords1_centered, centroid1 = center_coords(coords1)
                coords2_centered, centroid2 = center_coords(coords2)
            
                # Compute covariance matrix and SVD
                H = np.dot(coords1_centered.T, coords2_centered)
                U, S, Vt = np.linalg.svd(H)
                R = np.dot(Vt.T, U.T)
            
                # Correct for reflection
                if np.linalg.det(R) < 0:
                    Vt[-1, :] *= -1
                    R = np.dot(Vt.T, U.T)
            
                # Align coords2 to coords1
                aligned_coords2 = np.dot(coords2_centered, R) + centroid1
                rmsd = calculate_rmsd(coords1, aligned_coords2)
                
                for_plot.append([cc1, cc2, rmsd])
        
        for_plot = pd.DataFrame(for_plot, columns = ['c1', 'c2', 'rmsd'])
        heatmap_data = for_plot.pivot(index='c1', columns='c2', values='rmsd')


        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap='Blues')
        
        plt.title("Heatmap of RMSD between chains", fontsize = 16)
        plt.xlabel("Protein 2", fontsize = 14)
        plt.ylabel("Protein 1", fontsize = 14)
        plt.show()
                
    
    elif isinstance(chains, list) and len(chains) == 2:
        # Filter to Cα atoms only
        df1_ca = df1[(df1.atom_type == "CA") & (df1.chain_index == chains[0])]
        df2_ca = df2[(df2.atom_type == "CA") & (df2.chain_index == chains[1])]
                    
    
        df_ca_merged = pd.merge(df1_ca, df2_ca, on = 'amino_index', suffixes = ['_1', '_2'])
        
        if len(df_ca_merged) == 0 :
            print('Please check data, given chains have no common amino index')
            return 'Abort'
        
        # Extract coordinates
        coords1 = df_ca_merged[["x_1", "y_1", "z_1"]].to_numpy()
        coords2 = df_ca_merged[["x_2", "y_2", "z_2"]].to_numpy()
    
        # Center both
        coords1_centered, centroid1 = center_coords(coords1)
        coords2_centered, centroid2 = center_coords(coords2)
    
        # Compute covariance matrix and SVD
        H = np.dot(coords1_centered.T, coords2_centered)
        U, S, Vt = np.linalg.svd(H)
        R = np.dot(Vt.T, U.T)
    
        # Correct for reflection
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = np.dot(Vt.T, U.T)
    
        # Align coords2 to coords1
        aligned_coords2 = np.dot(coords2_centered, R) + centroid1
        rmsd = calculate_rmsd(coords1, aligned_coords2)
        
        print(f"RMSD after alignment (CA atoms): {rmsd:.3f} Å")

    else:
        print('Please define chains correctly')
    
        
# e1, e2 = protplot.read_pdb('7lym'), read_pdb('7lyn')
# protplot.Protein_alignment(e1, e2, chains = 'Combo_matrix')



    
