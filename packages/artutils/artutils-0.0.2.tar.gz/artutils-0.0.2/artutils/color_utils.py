import colorsys, numpy as np
from skimage import color as skcolor

def hex_to_rgb_normalized(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return (r, g, b)

def rgb_normalized_to_hex(rgb_normalized):
    r = int(round(rgb_normalized[0] * 255))
    g = int(round(rgb_normalized[1] * 255))
    b = int(round(rgb_normalized[2] * 255))
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def hex_to_lab(h):
    rgb = np.array(hex_to_rgb_normalized(h)).reshape(1, 1, 3)
    lab = skcolor.rgb2lab(rgb)
    return lab[0, 0]

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
    
def delta_e(l1,l2):
    return np.linalg.norm(l1 - l2)

def interpolate_hsl_gradient(color1_hex, color2_hex, steps=10):
    
    rgb1 = hex_to_rgb_normalized(color1_hex)
    rgb2 = hex_to_rgb_normalized(color2_hex)
    
    h1, l1, s1 = colorsys.rgb_to_hls(*rgb1)
    h2, l2, s2 = colorsys.rgb_to_hls(*rgb2)
    
    if abs(h2 - h1) > 0.5:
        if h1 > h2:
            h2 += 1
        else:
            h1 += 1

    h_step = (h2 - h1) / (steps - 1)
    l_step = (l2 - l1) / (steps - 1)
    s_step = (s2 - s1) / (steps - 1)
    
    gradient = []
    
    for i in range(steps):
        h = (h1 + i * h_step) % 1.0
        l = l1 + i * l_step
        s = s1 + i * s_step
        
        rgb = colorsys.hls_to_rgb(h, l, s)
        hex_color = rgb_normalized_to_hex(rgb)
        gradient.append(hex_color)
    
    return gradient

def generate_full_hsl_gradient(palette, steps_per_transition=50, duplicate_threshold=5):
    """Expand palette by interpolating smooth HSL gradients between adjacent colors."""
    
    full_gradient = []
    n = len(palette)
    
    for i in range(n):
        color_start = palette[i]
        color_end = palette[(i + 1) % n]  # wrap around for full circle
        gradient = interpolate_hsl_gradient(color_start, color_end, steps=steps_per_transition)
        full_gradient.extend(gradient[:-1])  # skip last color to avoid duplication

    full_gradient = deduplicate_colors(full_gradient, duplicate_threshold)
    return full_gradient

    
def generate_opposite_palette(hex_palette):
    opposite_palette = []
    for hex_color in hex_palette:
        r, g, b = hex_to_rgb_normalized(hex_color)
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        h_opp = (h + 0.5) % 1.0
        r_opp, g_opp, b_opp = colorsys.hls_to_rgb(h_opp, l, s)
        hex_opp = rgb_normalized_to_hex((r_opp, g_opp, b_opp))
        opposite_palette.append(hex_opp)
    return opposite_palette

def get_hex_codes_from_centers(centers):
    """Convert cluster centers to hex codes."""
    hex_codes = []
    for rgb in np.round(centers).astype(int):
        hex_code = '#{:02x}{:02x}{:02x}'.format(*rgb)
        hex_codes.append(hex_code)
    return hex_codes


def get_hex_codes_from_gmm_means(gmm_means):
    """Convert GMM means to hex codes."""
    hex_codes = []
    for rgb in np.round(gmm_means).astype(int):
        hex_code = '#{:02x}{:02x}{:02x}'.format(*rgb)
        hex_codes.append(hex_code)
    return hex_codes