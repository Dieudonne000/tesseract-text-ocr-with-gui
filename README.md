# Tesseract OCR Scanner

A professional, minimalistic GUI application for optical character recognition (OCR) using PyTesseract. This application provides an intuitive interface for extracting text from images with support for live camera input, region of interest (ROI) selection, and real-time text overlay visualization.

## Features

- **Image Loading**: Load images from file (PNG, JPG, JPEG, BMP, TIFF, GIF)
- **Live Camera Input**: Real-time camera preview with frame capture capability
- **Region of Interest (ROI) Selection**: Select specific areas of an image for OCR processing
- **Text Extraction**: Extract text from images using Tesseract OCR engine
- **Text Overlay**: Visualize detected text with bounding boxes overlaid on the image
- **Image Processing**: Automatic preprocessing including grayscale conversion, thresholding, and inversion
- **OCR Statistics**: Display confidence scores and detection statistics
- **Minimalistic Design**: Clean, professional black and white interface

## Requirements

### Software Dependencies

- Python 3.7 or higher
- Tesseract OCR engine

### Python Packages

- PyQt5 >= 5.15.0
- opencv-python >= 4.5.0
- pytesseract >= 0.3.10
- Pillow >= 9.0.0
- numpy >= 1.21.0

## Installation

### 1. Install Tesseract OCR

#### Windows
1. Download Tesseract installer from [UB Mannheim's GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and follow the setup wizard
3. Note the installation path (default: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
4. Optionally, add Tesseract to your system PATH

#### macOS
```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install PyQt5 opencv-python pytesseract Pillow numpy
```

## Usage

### Running the Application

```bash
python tesseract_gui.py
```

### Using the Application

1. **Load an Image**
   - Click the "Load Image" button
   - Select an image file from your computer
   - The image will be displayed in the main viewing area

2. **Use Camera Input**
   - Click "Start Camera" to begin live camera preview
   - Position your document or text in front of the camera
   - Click "Capture Frame" to capture the current frame for OCR processing

3. **Select Region of Interest (ROI)**
   - Click "Select ROI" button
   - Click and drag on the image to select the area you want to process
   - Click "Cancel ROI" to cancel selection
   - Only the selected region will be processed when running OCR

4. **Run OCR**
   - Click the "Run OCR" button to extract text from the image (or selected ROI)
   - Extracted text will appear in the "Extracted Text" panel on the right
   - OCR statistics (word count, confidence scores) will be displayed below

5. **View Text Overlay**
   - After running OCR, click "Toggle Text Overlay" to see bounding boxes around detected text
   - The overlay shows detected words with their bounding boxes

6. **Image Processing**
   - Use "Toggle Invert" to invert image colors (useful for dark text on light backgrounds)
   - The application automatically preprocesses images for optimal OCR results

7. **Clear**
   - Click "Clear" to reset the application and start over

## Project Structure

```
tesseract-with-gui/
├── tesseract_gui.py      # Main application file
├── tesseractocr.py        # Original OCR script (reference)
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── img1.png              # Sample image (if provided)
```

## Technical Details

### Image Preprocessing

The application automatically preprocesses images for better OCR accuracy:
- Converts images to grayscale
- Detects background color (white/black)
- Applies automatic thresholding using Otsu's method
- Inverts images when necessary for optimal text recognition

### OCR Engine

The application uses Tesseract OCR engine, which supports:
- Multiple languages (configure Tesseract language packs as needed)
- Various image formats
- Automatic text orientation detection
- Confidence scoring for detected text

## Troubleshooting

### Tesseract Not Found

If you encounter an error about Tesseract not being found:

1. **Windows**: Ensure Tesseract is installed and update the path in `tesseract_gui.py` if needed:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

2. **Linux/macOS**: Ensure Tesseract is in your system PATH, or update the path in the code

### Camera Not Working

- Ensure your camera is connected and not being used by another application
- Check camera permissions in your system settings
- Try a different camera index (modify `cv2.VideoCapture(0)` to use a different camera)

### Poor OCR Results

- Ensure good lighting and image quality
- Use ROI selection to focus on specific text areas
- Try the "Toggle Invert" option for different image types
- Ensure text is clear and not too small or blurry

## License

This project is provided as-is for educational and personal use.

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [OpenCV](https://opencv.org/) - Image processing

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Contact

For questions or issues, please open an issue on the project repository.

