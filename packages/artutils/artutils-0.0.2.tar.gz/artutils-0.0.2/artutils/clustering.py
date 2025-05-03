import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from kneed import KneeLocator
from artutils.io_utils import load_and_resize_image
from artutils.palette_tools import deduplicate_colors, sort_palette_by_closeness
from artutils.color_utils import interpolate_hsl_gradient, rgb_normalized_to_hex, generate_full_hsl_gradient

# k‑means helpers

def fit_kmeans(pixels, max_k=11, use_elbow=False):

    if use_elbow:
        inertias = []
        k_values = range(1, max_k + 1)
        
        for k in k_values:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
            kmeans.fit(pixels)
            inertias.append(kmeans.inertia_)
        
        knee = KneeLocator(k_values, inertias, curve='convex', direction='decreasing').knee
        k = knee
    else:
        k = max_k
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
    kmeans.fit(pixels)
    return kmeans

def kmeans_centers_to_hex(centers):
    hex_codes = []
    for rgb in np.round(centers).astype(int):
        hex_code = '#{:02x}{:02x}{:02x}'.format(*rgb)
        hex_codes.append(hex_code)
    return hex_codes

# GMM helpers + soft gradient

def fit_gmm(pixels,max_k=20,use_bic=False):
    if use_bic:
        bics = []
        k_range = range(1, max_k + 1)
        
        for k in k_range:
            gmm = GaussianMixture(n_components=k, random_state=42)
            gmm.fit(pixels)
            bics.append(gmm.bic(pixels))
        
        best_k = k_range[bics.index(min(bics))]
    else:
        best_k = max_k
    
    gmm = GaussianMixture(n_components=best_k, random_state=42)
    gmm.fit(pixels)
    return gmm


def gmm_means_to_hex(means):
    hex_codes = []
    for rgb in np.round(gmm_means).astype(int):
        hex_code = '#{:02x}{:02x}{:02x}'.format(*rgb)
        hex_codes.append(hex_code)
    return hex_codes

def fit_gmm_to_colors(rgb_pixels, n_components=5):

    gmm = GaussianMixture(n_components=n_components, covariance_type='full', random_state=42)
    gmm.fit(rgb_pixels)
    
    centroids = gmm.means_  # shape (n_components, 3)
    soft_probs = gmm.predict_proba(rgb_pixels)  # shape (num_pixels, n_components)
    
    return centroids, soft_probs

def soft_blend_pixel(centroids, soft_probs):
    """Blend RGB centroids according to soft probabilities for a single pixel."""
    blended_rgb = np.average(centroids, axis=0, weights=soft_probs)
    return blended_rgb
    
def gmm_soft_gradient(image_path,n_components=5, sample_size=5000, steps_per_transition=30, deduplication_threshold=5):


    image_rgb = load_and_resize_image(image_path, size=(100, 100))
    pixels = image_rgb.reshape(-1, 3)

    if len(pixels) > sample_size:
        idx = np.random.choice(len(pixels), size=sample_size, replace=False)
        pixels = pixels[idx]
    

    centroids, soft_probs = fit_gmm_to_colors(pixels, n_components)
  
    blended_colors_rgb = []
    for pixel_probs in soft_probs:
        blended_rgb = soft_blend_pixel(centroids, pixel_probs)
        blended_colors_rgb.append(blended_rgb)

    blended_colors_hex = [rgb_normalized_to_hex(rgb / 255) for rgb in blended_colors_rgb]
    

    deduped_colors = deduplicate_colors(blended_colors_hex, threshold=deduplication_threshold)
    

    sorted_colors = sort_palette_by_closeness(deduped_colors)
    
    full_gradient = generate_full_hsl_gradient(sorted_colors, steps_per_transition=steps_per_transition)
    return full_gradient
