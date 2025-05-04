import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from artutils.palette_tools import sort_palette_by_closeness

def plot_swatch(pal, save_path=None):
    fig, ax = plt.subplots(figsize=(len(pal), 2))
    for i, c in enumerate(pal):
        ax.add_patch(patches.Rectangle((i, 0), 1, 1, color=c))
    ax.set_xlim(0, len(pal))
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_wheel(pal, inner=0.5, width=0.5, figsize=(8, 8), save_path=None):
    pal = sort_palette_by_closeness(pal)
    n = len(pal)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)

    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    for angle, c in zip(angles, pal):
        ax.bar(angle, width, 2 * np.pi / n, bottom=inner, color=c, linewidth=0)

    ax.axis('off')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
