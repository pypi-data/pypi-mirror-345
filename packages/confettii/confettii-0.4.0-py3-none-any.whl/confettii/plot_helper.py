import math
import matplotlib.pyplot as plt

def grid_plot_list_imgs(images,col_labels=None,row_labels=None,ncols=3,fig_size=4):

    n_images = len(images)
    ncols = ncols
    nrows = math.ceil(n_images / ncols)

    # Column labels
    if not col_labels:
        col_labels = [f'Col {i+1}' for i in range(ncols)]
    # Row labels
    if not row_labels:
        row_labels = [f'Row {i+1}' for i in range(nrows)]

    fig, axes = plt.subplots(nrows, ncols, figsize=(fig_size*ncols,  fig_size*nrows))

    for i, ax in enumerate(axes.flat):
        if i < n_images:
            ax.imshow(images[i], cmap='gray')
        ax.axis('off')
            # Add column labels at top row

        if i < ncols:
            ax.set_title(col_labels[i], fontsize=14)

        # Add row labels at first column
        if i % ncols == 0:
            ax.set_ylabel(row_labels[i // ncols], fontsize=14, rotation=0, labelpad=40, va='center')


    plt.tight_layout()
    plt.show()