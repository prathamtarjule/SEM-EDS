
# README: SEM-EDS Image Processing and Analysis Script

## Overview
This Python script processes SEM-EDS (Scanning Electron Microscopy - Energy Dispersive Spectroscopy) images to analyze and visualize elemental composition maps. The script:
1. Normalizes pixel intensity values to a [0, 1] range.
2. Maps normalized intensity to user-defined or predefined concentration ranges for each element.
3. Applies Gaussian filters to smoothen the composition maps, using specified sigma values.
4. Generates visualizations for the original and processed data.
5. Saves processed data and visualizations to files for further analysis.

---

## Requirements

### Prerequisites
1. **Python**: Install Python (>= 3.7).
2. **Required Libraries**:
   - `numpy`
   - `Pillow`
   - `matplotlib`
   - `scipy`
   - `pandas`
   - `os` (standard library)
   - `pathlib` (standard library)

Install any missing libraries using:
```bash
pip install numpy pillow matplotlib scipy pandas
```

---

## How to Run the Script

1. **Set Up Input Folder**:
   - Place your SEM-EDS images in the folder defined in the `folder_path` variable. For example:
     ```python
     folder_path = 'P://EDS-PhaSe/sample-data/MPB/FINAL_Crop_Data/'
     ```
   - Supported file formats: `.png`, `.jpg`, `.jpeg`, `.tif`.

2. **Define or Modify Concentration Ranges**:
   - Open the script and update the `concentration_ranges` dictionary with the concentration ranges for your images:
     ```python
     concentration_ranges = {
         'eds-map-C.png': {'highest': 0.05, 'lowest': 0.03},
         'eds-map-Ni.png': {'highest': 14.27, 'lowest': 14.13},
         ...
     }
     ```
   - If a range is not defined, the script will prompt you to input it during runtime.

3. **Run the Script**:
   - Execute the script in your Python environment:
     ```bash
     python extract_data.py
     ```
   - The script processes each image and saves the results in the output directory.

4. **View Results**:
   - Processed data (visualizations and Excel files) will be saved in the `processing_results` folder in the same directory as the script.

---

## Detailed Steps Performed by the Script

### Step 1: Image Loading
- Reads each image file in the `folder_path` directory that matches the supported formats.
- Converts the image to grayscale using `Pillow`:
  ```python
  sem_eds_img = Image.open(image_path).convert('L')
  ```

### Step 2: Intensity Normalization
- Normalizes the pixel intensity values to a [0, 1] range:
  ```python
  normalized_intensity = (sem_eds_np - sem_eds_np.min()) / (sem_eds_np.max() - sem_eds_np.min())
  ```

### Step 3: Concentration Mapping
- Maps the normalized intensity to a concentration range defined for the image:
  ```python
  composition_map = lowest_concentration + normalized_intensity * (highest_concentration - lowest_concentration)
  ```
- Ensures the values are within the specified concentration range using:
  ```python
  composition_map = np.clip(composition_map, lowest_concentration, highest_concentration)
  ```

### Step 4: Gaussian Filtering
- Applies Gaussian filters with specified sigma values (e.g., `sigma = 0, 0.5, 1`):
  ```python
  filtered_map = gaussian_filter(composition_map, sigma=sigma)
  ```
- Saves each filtered map separately.

### Step 5: Visualization
- Generates a visualization for each image, including:
  - Original Image
  - Normalized Intensity Map
  - Composition Map
  - Filtered Maps for all sigma values
- Saves the plots as PNG files in the output folder.

### Step 6: Data Export
- Exports the processed data into Excel files:
  - **Combined Excel File**: Contains original maps and all filtered maps.
  - **Separate Excel Files**: One for each sigma value.
  ```python
  combined_excel_path = 'processing_results/all_composition_maps.xlsx'
  ```

### Step 7: Log File
- Saves a log of the concentration ranges used for each image:
  ```python
  concentration_ranges.txt
  ```

---

## Output Files

1. **Visualization Plots**:
   - Saved as PNG files in the `processing_results/` folder.
   - Includes:
     - Original Image
     - Normalized Intensity Map
     - Composition Map
     - Filtered Maps

2. **Excel Files**:
   - **Combined Excel File**:
     - `processing_results/all_composition_maps.xlsx`
     - Contains all processed data (original and filtered maps) and metadata.
   - **Separate Sigma Files**:
     - Files named `composition_maps_sigma_<sigma>.xlsx` for each sigma value.

3. **Log File**:
   - `processing_results/concentration_ranges.txt`
   - Lists the concentration ranges used for each image.

---

## Example Run
For an image `eds-map-C.png` with concentration range 0.03–0.05:
1. The script loads and normalizes the image intensity.
2. Maps intensity to the range 0.03–0.05.
3. Applies Gaussian filters with `sigma = 0, 0.5, 1`.
4. Saves the original and filtered maps to:
   - Visualization plot: `processing_results/visualization_eds-map-C.png`
   - Combined Excel file: `processing_results/all_composition_maps.xlsx`
   - Log file: `processing_results/concentration_ranges.txt`

---

## Customization

### Modify Concentration Ranges
- Update the `concentration_ranges` dictionary in the script for your dataset.

### Change Sigma Values
- Update the `sigma_values` list to include the desired filter strengths:
  ```python
  sigma_values = [0, 0.5, 1, 2]  # Example
  ```

### Adjust Output Folder
- Change the output folder by modifying the `results_dir` variable:
  ```python
  results_dir = 'path_to_your_output_folder'
  ```

---

## Troubleshooting

1. **Missing Libraries**:
   - Install missing libraries using pip:
     ```bash
     pip install <library_name>
     ```

2. **Undefined Concentration Ranges**:
   - Add ranges to the `concentration_ranges` dictionary before running.

3. **Large Datasets**:
   - For large images, processing might take longer. Reduce the number of sigma values or downscale the images if needed.

---

