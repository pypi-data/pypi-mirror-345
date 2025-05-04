import numpy as np
from artutils.color_utils import hex_to_lab, delta_e
from artutils.io_utils import load_and_resize_image
from skimage import color as skcolor

def deduplicate_colors(colors, threshold=5):
    labs = [hex_to_lab(c) for c in colors]
    deduped_colors = colors.copy()
    
    i = 0
    while i < len(labs):
        j = i + 1
        while j < len(labs):
            if delta_e(labs[i], labs[j]) < threshold:
                # Remove the second color if too similar
                deduped_colors.pop(j)
                labs.pop(j)
            else:
                j += 1
        i += 1
    
    return deduped_colors

def sort_palette_by_closeness(colors):
    if not colors:
        return []
    
    labs = [hex_to_lab(c) for c in colors]
    used = [False] * len(colors)
    
    sorted_colors = []
    current_idx = 0
    sorted_colors.append(colors[current_idx])
    used[current_idx] = True
    
    for _ in range(len(colors) - 1):
        min_dist = float('inf')
        next_idx = None
        
        for j in range(len(colors)):
            if not used[j]:
                dist = delta_e(labs[current_idx], labs[j])
                if dist < min_dist:
                    min_dist = dist
                    next_idx = j
        
        sorted_colors.append(colors[next_idx])
        used[next_idx] = True
        current_idx = next_idx
    
    return sorted_colors

def extract_palette_by_frequency_and_lab(image_path, resize_dim=(300, 300), min_pixel_count=150, delta_e_threshold=5, max_colors=None):

    image_rgb = load_and_resize_image(image_path, size=resize_dim)
    pixels = image_rgb.reshape(-1, 3)
    

    colors, counts = np.unique(pixels, axis=0, return_counts=True)

    sorted_indices = np.argsort(-counts)
    colors = colors[sorted_indices]
    counts = counts[sorted_indices]

    filtered_colors = [c for i, c in enumerate(colors) if counts[i] >= min_pixel_count]


    final_colors = []
    final_labs = []
    
    for rgb in filtered_colors:
        rgb_norm = np.array(rgb) / 255.0
        lab = skcolor.rgb2lab(rgb_norm.reshape(1, 1, 3))[0, 0]
        
        if not final_labs:
            final_colors.append(rgb)
            final_labs.append(lab)
        else:
            dists = np.linalg.norm(np.array(final_labs) - lab, axis=1)
            if np.all(dists > delta_e_threshold):
                final_colors.append(rgb)
                final_labs.append(lab)
        
        if max_colors and len(final_colors) >= max_colors:
            break

    hex_codes = ['#{:02x}{:02x}{:02x}'.format(*np.round(rgb).astype(int)) for rgb in final_colors]
    
    return hex_codes
