import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import pandas as pd
import os
from pathlib import Path

# Folder containing the images
folder_path = 'P://EDS-PhaSe/sample-data/MPB/FINAL_Crop_Data/'

# Define concentration ranges for each image
# You can modify these values for each image
concentration_ranges = {
    'eds-map-C.png': {'highest': 0.05, 'lowest': 0.03},
    'eds-map-Ni.png': {'highest': 14.27, 'lowest': 14.13},
    'eds-map-Cr.png': {'highest': 16.53, 'lowest': 16.31},
    'eds-map-Mn.png': {'highest': 1.68, 'lowest': 1.38},
    'eds-map-Mo.png': {'highest': 2.68, 'lowest': 2.36},
    'eds-map-O.png': {'highest': 1.31, 'lowest': 0.77},
    'eds-map-Fe.png': {'highest': 64.19, 'lowest': 63.77},
    'eds-map-Si.png': {'highest': 0.38, 'lowest': 0.26}
    # Add more images and their concentration ranges as needed
}

# Gaussian filter sigma values
sigma_values = [0, 0.5, 1]

# Create a directory for saving results if it doesn't exist
results_dir = 'processing_results'
os.makedirs(results_dir, exist_ok=True)

# Dictionary to store all processed data
all_processed_data = {sigma: {} for sigma in sigma_values}
original_maps = {}

# Function to get concentration range for an image
def get_concentration_range(image_file):
    if image_file in concentration_ranges:
        return concentration_ranges[image_file]
    else:
        print(f"Warning: No concentration range defined for {image_file}. Please enter the values:")
        highest = float(input(f"Enter highest concentration for {image_file}: "))
        lowest = float(input(f"Enter lowest concentration for {image_file}: "))
        concentration_ranges[image_file] = {'highest': highest, 'lowest': lowest}
        return {'highest': highest, 'lowest': lowest}

# Process each image in the folder
for image_file in os.listdir(folder_path):
    if image_file.endswith(('.png', '.jpg', '.jpeg', '.tif')):
        print(f"\nProcessing {image_file}...")
        
        # Get concentration range for this image
        conc_range = get_concentration_range(image_file)
        highest_concentration = conc_range['highest']
        lowest_concentration = conc_range['lowest']
        
        print(f"Using concentration range: {lowest_concentration} - {highest_concentration}")
        
        # Load and process image
        image_path = os.path.join(folder_path, image_file)
        sem_eds_img = Image.open(image_path).convert('L')
        sem_eds_np = np.array(sem_eds_img)
        
        # Normalize intensity values to [0, 1]
        normalized_intensity = (sem_eds_np - sem_eds_np.min()) / (sem_eds_np.max() - sem_eds_np.min())
        
        # Map intensity to concentration range
        composition_map = lowest_concentration + normalized_intensity * (highest_concentration - lowest_concentration)
        composition_map = np.clip(composition_map, lowest_concentration, highest_concentration)
        
        # Store original composition map
        original_maps[image_file] = composition_map
        
        # Apply Gaussian filtering for each sigma value
        for sigma in sigma_values:
            filtered_map = gaussian_filter(composition_map, sigma=sigma)
            filtered_map = np.clip(filtered_map, lowest_concentration, highest_concentration)
            all_processed_data[sigma][image_file] = filtered_map
            
        # Create visualization plot
        plt.figure(figsize=(20, 10))
        
        # Plot original image
        plt.subplot(2, 3, 1)
        img_original = plt.imshow(sem_eds_np, cmap='gray')
        plt.title(f'Original Image\n{image_file}')
        plt.colorbar(img_original)
        plt.axis('off')
        
        # Plot normalized intensity
        plt.subplot(2, 3, 2)
        img_normalized = plt.imshow(normalized_intensity, cmap='viridis')
        plt.title('Normalized Intensity')
        plt.colorbar(img_normalized)
        plt.axis('off')
        
        # Plot composition map
        plt.subplot(2, 3, 3)
        img_composition = plt.imshow(composition_map, cmap='viridis',
                                   vmin=lowest_concentration, vmax=highest_concentration)
        plt.title(f'Composition Map\n(Range: {lowest_concentration:.3f} - {highest_concentration:.3f})')
        plt.colorbar(img_composition)
        plt.axis('off')
        
        # Plot filtered maps
        for i, sigma in enumerate(sigma_values[:3]):  # Show first 3 filtered maps
            plt.subplot(2, 3, i + 4)
            img_filtered = plt.imshow(all_processed_data[sigma][image_file], cmap='viridis',
                                    vmin=lowest_concentration, vmax=highest_concentration)
            plt.title(f'Filtered (σ={sigma})')
            plt.colorbar(img_filtered)
            plt.axis('off')
        
        plt.tight_layout()
        # Save plot
        plt.savefig(os.path.join(results_dir, f'visualization_{Path(image_file).stem}.png'))
        plt.close()

# Save concentration ranges to a log file
with open(os.path.join(results_dir, 'concentration_ranges.txt'), 'w') as f:
    f.write("Concentration Ranges Used:\n")
    for image, ranges in concentration_ranges.items():
        f.write(f"{image}: {ranges['lowest']} - {ranges['highest']}\n")

# Save combined results in a single Excel file
print("\nSaving combined results...")
combined_excel_path = os.path.join(results_dir, 'all_composition_maps.xlsx')
with pd.ExcelWriter(combined_excel_path) as writer:
    # Save metadata sheet
    metadata_df = pd.DataFrame([
        {'Image': img, 'Lowest_Concentration': ranges['lowest'], 'Highest_Concentration': ranges['highest']}
        for img, ranges in concentration_ranges.items()
    ])
    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
    
    # Save original maps
    for image_file, comp_map in original_maps.items():
        sheet_name = f'Original_{Path(image_file).stem}'[:31]
        df = pd.DataFrame(
            comp_map,
            index=[f'Row_{i}' for i in range(comp_map.shape[0])],
            columns=[f'Col_{i}' for i in range(comp_map.shape[1])]
        )
        df.to_excel(writer, sheet_name=sheet_name)
    
    # Save filtered maps
    for sigma in sigma_values:
        for image_file, filtered_map in all_processed_data[sigma].items():
            sheet_name = f'Sigma_{str(sigma).replace(".", "_")}_{Path(image_file).stem}'[:31]
            df = pd.DataFrame(
                filtered_map,
                index=[f'Row_{i}' for i in range(filtered_map.shape[0])],
                columns=[f'Col_{i}' for i in range(filtered_map.shape[1])]
            )
            df.to_excel(writer, sheet_name=sheet_name)

# Save separate Excel files for each sigma value
print("Saving separate Excel files for each sigma value...")
for sigma in sigma_values:
    sigma_excel_path = os.path.join(results_dir, f'composition_maps_sigma_{str(sigma).replace(".", "_")}.xlsx')
    with pd.ExcelWriter(sigma_excel_path) as writer:
        # Save metadata sheet
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        for image_file, filtered_map in all_processed_data[sigma].items():
            sheet_name = f'{Path(image_file).stem}'[:31]
            df = pd.DataFrame(
                filtered_map,
                index=[f'Row_{i}' for i in range(filtered_map.shape[0])],
                columns=[f'Col_{i}' for i in range(filtered_map.shape[1])]
            )
            df.to_excel(writer, sheet_name=sheet_name)

print("\nProcessing complete! Results saved in the 'processing_results' directory:")
print(f"1. Combined results: {combined_excel_path}")
print(f"2. Separate sigma files in: {results_dir}")
print("3. Visualization plots for each image")
print("4. Concentration ranges log file")