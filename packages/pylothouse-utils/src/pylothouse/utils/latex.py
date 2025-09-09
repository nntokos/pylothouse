import os
import subprocess
import matplotlib.pyplot as plt

def latex_table_to_png(input, width=8, height=4, font_size=16, dpi=100):
    latex_expression = (input)
    
    print(latex_expression)
    fig = plt.figure(figsize=(width, height), dpi=dpi)
    # plt.rcParams['text.usetex'] = True
    plt.rcParams['text.latex.preamble'] = r'\usepackage{tabularx} \usepackage{booktabs} \usepackage{multirow} \usepackage{amsmath} \usepackage{mathptmx}'
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Times New Roman"],  # You can specify other serif fonts like "Times", "Palatino", etc.
        'text.latex.preamble': r'\usepackage{tabularx} \usepackage{booktabs} \usepackage{multirow} \usepackage{amsmath} \usepackage{mathptmx}',
        "font.size": font_size,
        "font.weight": 'bold',
    })
    text = fig.text(
        x=0.5,  # x-coordinate to place the text
        y=0.5,  # y-coordinate to place the text
        s=latex_expression,
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=16,
        bbox=dict(facecolor='white', edgecolor='none', pad=10)  # Add padding around the text
    )

    # Adjust the figure layout to fit the text
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    plt.savefig('latex_table.png', bbox_inches='tight', pad_inches=0.1)
    plt.show()
