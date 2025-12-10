import sys
import cv2
import pytesseract
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QMessageBox, QSlider, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QColor
from PIL import Image, ImageDraw, ImageFont


class CameraThread(QThread):
    """Thread for capturing camera frames"""
    frame_ready = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.camera = None
        self.running = False
        
    def start_camera(self):
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            return False
        self.running = True
        self.start()
        return True
        
    def stop_camera(self):
        self.running = False
        if self.camera:
            self.camera.release()
        self.wait()
        
    def run(self):
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                self.frame_ready.emit(frame)
            self.msleep(30)  # ~30 FPS


class OCRScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tesseract OCR Scanner")
        self.setGeometry(100, 100, 1500, 950)
        
        # Image and processing variables
        self.current_image = None
        self.processed_image = None
        self.roi_start = None
        self.roi_end = None
        self.roi_selected = False
        self.drawing_roi = False
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.update_camera_frame)
        
        # OCR results
        self.ocr_data = []
        
        # Initialize UI
        self.init_ui()
        
        # Set Tesseract path (Windows default)
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        except:
            pass  # Will use system PATH if not found
        
    def init_ui(self):
        # Apply minimalistic light theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QWidget {
                background-color: #ffffff;
                color: #212121;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QDialog {
                background-color: #ffffff;
                color: #212121;
            }
            QDialog QLabel {
                color: #212121;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                color: #212121;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: 500;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border: 1px solid #757575;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
                border: 1px solid #616161;
            }
            QPushButton:disabled {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                color: #9e9e9e;
            }
            QLabel {
                color: #212121;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                padding: 12px;
                color: #212121;
                selection-background-color: #424242;
                selection-color: #ffffff;
            }
            QTextEdit:focus {
                border: 1px solid #424242;
            }
            QGroupBox {
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                margin-top: 15px;
                padding-top: 15px;
                font-size: 11pt;
                font-weight: 600;
                color: #212121;
                background-color: #fafafa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                background-color: #fafafa;
            }
            QMessageBox {
                background-color: #ffffff !important;
                color: #212121 !important;
            }
            QMessageBox QLabel {
                color: #212121 !important;
                background-color: #ffffff !important;
            }
            QMessageBox QPushButton {
                background-color: #ffffff !important;
                border: 1px solid #bdbdbd !important;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
                color: #212121 !important;
            }
            QMessageBox QPushButton:hover {
                background-color: #f5f5f5 !important;
                border: 1px solid #757575 !important;
                color: #212121 !important;
            }
            QFileDialog {
                background-color: #ffffff;
                color: #212121;
            }
            QFileDialog QLabel {
                color: #212121;
            }
            QFileDialog QLineEdit {
                background-color: #ffffff;
                border: 1px solid #bdbdbd;
                color: #212121;
            }
            QFileDialog QListView {
                background-color: #ffffff;
                color: #212121;
            }
            QFileDialog QTreeView {
                background-color: #ffffff;
                color: #212121;
            }
            QFileDialog QComboBox {
                background-color: #ffffff;
                border: 1px solid #bdbdbd;
                color: #212121;
            }
            QFileDialog QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #212121;
                selection-background-color: #e0e0e0;
                selection-color: #212121;
            }
            QFileDialog QPushButton {
                background-color: #ffffff;
                border: 1px solid #bdbdbd;
                color: #212121;
            }
            QFileDialog QPushButton:hover {
                background-color: #f5f5f5;
                border: 1px solid #757575;
                color: #212121;
            }
            QToolTip {
                background-color: #ffffff;
                border: 1px solid #bdbdbd;
                color: #212121;
                padding: 4px;
            }
            QScrollBar:vertical {
                background-color: #f5f5f5;
                width: 12px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #bdbdbd;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #9e9e9e;
            }
            QScrollBar:horizontal {
                background-color: #f5f5f5;
                height: 12px;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background-color: #bdbdbd;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #9e9e9e;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
                border: none;
            }
        """)
        
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #ffffff;")
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Image display and controls
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # Image display area with minimalistic styling
        self.image_label = QLabel()
        self.image_label.setMinimumSize(800, 600)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("No image loaded\n\nClick 'Load Image' or 'Start Camera' to begin")
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                background-color: #fafafa;
                color: #757575;
                font-size: 12pt;
                padding: 20px;
            }
        """)
        self.image_label.mousePressEvent = self.image_mouse_press
        self.image_label.mouseMoveEvent = self.image_mouse_move
        self.image_label.mouseReleaseEvent = self.image_mouse_release
        
        # Control buttons with modern styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.load_btn = QPushButton("Load Image")
        self.load_btn.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_btn)
        
        self.camera_btn = QPushButton("Start Camera")
        self.camera_btn.clicked.connect(self.toggle_camera)
        button_layout.addWidget(self.camera_btn)
        
        self.capture_btn = QPushButton("Capture Frame")
        self.capture_btn.clicked.connect(self.capture_frame)
        self.capture_btn.setEnabled(False)
        button_layout.addWidget(self.capture_btn)
        
        self.roi_btn = QPushButton("Select ROI")
        self.roi_btn.clicked.connect(self.toggle_roi_selection)
        button_layout.addWidget(self.roi_btn)
        
        self.ocr_btn = QPushButton("Run OCR")
        self.ocr_btn.clicked.connect(self.run_ocr)
        self.ocr_btn.setStyleSheet("""
            QPushButton {
                background-color: #212121;
                border: 1px solid #212121;
                color: #ffffff;
                font-size: 11pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #424242;
                border: 1px solid #424242;
            }
            QPushButton:pressed {
                background-color: #000000;
                border: 1px solid #000000;
            }
        """)
        button_layout.addWidget(self.ocr_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)
        
        # Image processing controls with minimalistic styling
        processing_group = QGroupBox("Image Processing")
        processing_layout = QVBoxLayout()
        processing_layout.setSpacing(10)
        processing_layout.setContentsMargins(15, 25, 15, 15)
        
        self.invert_btn = QPushButton("Toggle Invert")
        self.invert_btn.clicked.connect(self.toggle_invert)
        processing_layout.addWidget(self.invert_btn)
        
        self.overlay_btn = QPushButton("Toggle Text Overlay")
        self.overlay_btn.clicked.connect(self.toggle_overlay)
        processing_layout.addWidget(self.overlay_btn)
        
        processing_group.setLayout(processing_layout)
        
        left_panel.addWidget(self.image_label)
        left_panel.addLayout(button_layout)
        left_panel.addWidget(processing_group)
        
        # Right panel - Text display with minimalistic styling
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        text_label = QLabel("Extracted Text")
        text_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        text_label.setStyleSheet("""
            QLabel {
                color: #212121;
                padding: 5px;
                background: transparent;
            }
        """)
        right_panel.addWidget(text_label)
        
        self.text_display = QTextEdit()
        self.text_display.setFont(QFont("Consolas", 10))
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                padding: 12px;
                color: #212121;
                font-size: 10pt;
                line-height: 1.6;
            }
            QTextEdit:focus {
                border: 1px solid #424242;
            }
        """)
        right_panel.addWidget(self.text_display)
        
        # OCR Details with minimalistic styling
        details_label = QLabel("OCR Statistics")
        details_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        details_label.setStyleSheet("""
            QLabel {
                color: #212121;
                padding: 5px;
                background: transparent;
            }
        """)
        right_panel.addWidget(details_label)
        
        self.details_display = QTextEdit()
        self.details_display.setFont(QFont("Consolas", 9))
        self.details_display.setReadOnly(True)
        self.details_display.setMaximumHeight(200)
        self.details_display.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                padding: 12px;
                color: #212121;
                font-size: 9pt;
            }
            QTextEdit:focus {
                border: 1px solid #424242;
            }
        """)
        right_panel.addWidget(self.details_display)
        
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)
        
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.gif)"
        )
        if file_path:
            self.current_image = cv2.imread(file_path)
            if self.current_image is not None:
                self.processed_image = self.current_image.copy()
                self.display_image(self.current_image)
                self.roi_selected = False
                self.roi_start = None
                self.roi_end = None
            else:
                QMessageBox.warning(self, "Error", "Failed to load image")
    
    def toggle_camera(self):
        if not self.camera_thread.running:
            if self.camera_thread.start_camera():
                self.camera_btn.setText("Stop Camera")
                self.capture_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Error", "Failed to open camera")
        else:
            self.camera_thread.stop_camera()
            self.camera_btn.setText("Start Camera")
            self.capture_btn.setEnabled(False)
    
    def update_camera_frame(self, frame):
        if not self.drawing_roi:
            self.current_image = frame.copy()
            self.processed_image = frame.copy()
            self.display_image(frame)
    
    def capture_frame(self):
        if self.current_image is not None:
            self.camera_thread.stop_camera()
            self.camera_btn.setText("Start Camera")
            self.capture_btn.setEnabled(False)
            self.display_image(self.current_image)
    
    def toggle_roi_selection(self):
        self.drawing_roi = not self.drawing_roi
        if self.drawing_roi:
            self.roi_btn.setText("Cancel ROI")
            self.roi_btn.setStyleSheet("""
                QPushButton {
                    background-color: #424242;
                    border: 1px solid #424242;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #616161;
                    border: 1px solid #616161;
                }
            """)
        else:
            self.roi_btn.setText("Select ROI")
            self.roi_btn.setStyleSheet("")
            self.roi_start = None
            self.roi_end = None
    
    def image_mouse_press(self, event):
        if self.drawing_roi and self.current_image is not None:
            x = event.x()
            y = event.y()
            # Convert to image coordinates
            pixmap = self.image_label.pixmap()
            if pixmap:
                img_width = pixmap.width()
                img_height = pixmap.height()
                label_width = self.image_label.width()
                label_height = self.image_label.height()
                
                # Calculate offset
                offset_x = (label_width - img_width) // 2
                offset_y = (label_height - img_height) // 2
                
                if offset_x <= x <= offset_x + img_width and offset_y <= y <= offset_y + img_height:
                    img_x = int((x - offset_x) * self.current_image.shape[1] / img_width)
                    img_y = int((y - offset_y) * self.current_image.shape[0] / img_height)
                    self.roi_start = (img_x, img_y)
                    self.roi_end = (img_x, img_y)
    
    def image_mouse_move(self, event):
        if self.drawing_roi and self.roi_start is not None and self.current_image is not None:
            x = event.x()
            y = event.y()
            pixmap = self.image_label.pixmap()
            if pixmap:
                img_width = pixmap.width()
                img_height = pixmap.height()
                label_width = self.image_label.width()
                label_height = self.image_label.height()
                
                offset_x = (label_width - img_width) // 2
                offset_y = (label_height - img_height) // 2
                
                if offset_x <= x <= offset_x + img_width and offset_y <= y <= offset_y + img_height:
                    img_x = int((x - offset_x) * self.current_image.shape[1] / img_width)
                    img_y = int((y - offset_y) * self.current_image.shape[0] / img_height)
                    self.roi_end = (img_x, img_y)
                    self.display_image_with_roi()
    
    def image_mouse_release(self, event):
        if self.drawing_roi and self.roi_start is not None:
            self.roi_selected = True
            self.drawing_roi = False
            self.roi_btn.setText("Select ROI")
            self.roi_btn.setStyleSheet("")
    
    def display_image_with_roi(self):
        if self.current_image is not None and self.roi_start is not None and self.roi_end is not None:
            display_img = self.current_image.copy()
            # Draw ROI with minimalistic black/white style
            x1, y1 = self.roi_start
            x2, y2 = self.roi_end
            # Draw filled rectangle with transparency (gray)
            overlay = display_img.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (128, 128, 128), -1)  # Gray fill
            cv2.addWeighted(overlay, 0.2, display_img, 0.8, 0, display_img)
            # Draw border (black)
            cv2.rectangle(display_img, (x1, y1), (x2, y2), (0, 0, 0), 2)
            # Draw corner markers (black)
            corner_size = 12
            cv2.line(display_img, (x1, y1), (x1 + corner_size, y1), (0, 0, 0), 2)
            cv2.line(display_img, (x1, y1), (x1, y1 + corner_size), (0, 0, 0), 2)
            cv2.line(display_img, (x2, y1), (x2 - corner_size, y1), (0, 0, 0), 2)
            cv2.line(display_img, (x2, y1), (x2, y1 + corner_size), (0, 0, 0), 2)
            cv2.line(display_img, (x1, y2), (x1 + corner_size, y2), (0, 0, 0), 2)
            cv2.line(display_img, (x1, y2), (x1, y2 - corner_size), (0, 0, 0), 2)
            cv2.line(display_img, (x2, y2), (x2 - corner_size, y2), (0, 0, 0), 2)
            cv2.line(display_img, (x2, y2), (x2, y2 - corner_size), (0, 0, 0), 2)
            self.display_image(display_img)
    
    def display_image(self, image):
        if image is None:
            return
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize for display while maintaining aspect ratio
        h, w = rgb_image.shape[:2]
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        
        scale = min(label_width / w, label_height / h, 1.0)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        if new_w > 0 and new_h > 0:
            rgb_image = cv2.resize(rgb_image, (new_w, new_h))
        
        # Convert to QImage
        bytes_per_line = 3 * new_w
        q_image = QImage(rgb_image.data, new_w, new_h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)
        self.image_label.setText("")  # Clear placeholder text when image is displayed
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Check if white background
        _, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        white_pixel_count = np.sum(mask == 255)
        is_white_background = white_pixel_count > (mask.size / 2)
        
        # Invert if white background
        if is_white_background:
            gray = cv2.bitwise_not(gray)
        
        # Apply threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def run_ocr(self):
        if self.current_image is None:
            QMessageBox.warning(self, "Error", "No image loaded")
            return
        
        try:
            # Get ROI if selected
            ocr_image = self.current_image.copy()
            if self.roi_selected and self.roi_start is not None and self.roi_end is not None:
                x1, y1 = self.roi_start
                x2, y2 = self.roi_end
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)
                ocr_image = ocr_image[y1:y2, x1:x2]
            
            # Preprocess
            processed = self.preprocess_image(ocr_image)
            
            # Run OCR with detailed data
            ocr_data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            text = pytesseract.image_to_string(processed)
            
            # Store OCR data for overlay
            self.ocr_data = ocr_data
            
            # Display text
            self.text_display.setPlainText(text)
            
            # Display details
            details = f"Total words detected: {len([w for w in ocr_data['text'] if w.strip()])}\n"
            details += f"Confidence scores:\n"
            confidences = [int(c) for c in ocr_data['conf'] if int(c) > 0]
            if confidences:
                details += f"  Average: {sum(confidences) / len(confidences):.1f}\n"
                details += f"  Min: {min(confidences)}\n"
                details += f"  Max: {max(confidences)}\n"
            self.details_display.setPlainText(details)
            
            # Update processed image
            self.processed_image = processed
            
            # Show overlay if enabled
            if hasattr(self, 'show_overlay') and self.show_overlay:
                self.display_overlay()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"OCR failed: {str(e)}")
    
    def toggle_invert(self):
        if self.current_image is not None:
            self.current_image = cv2.bitwise_not(self.current_image)
            self.display_image(self.current_image)
    
    def toggle_overlay(self):
        if not hasattr(self, 'show_overlay'):
            self.show_overlay = False
        self.show_overlay = not self.show_overlay
        
        if self.show_overlay and len(self.ocr_data) > 0:
            self.display_overlay()
        else:
            if self.current_image is not None:
                self.display_image(self.current_image)
    
    def display_overlay(self):
        """Display image with text overlay showing detected text"""
        if self.current_image is None or len(self.ocr_data) == 0:
            return
        
        overlay_image = self.current_image.copy()
        
        n_boxes = len(self.ocr_data['text'])
        for i in range(n_boxes):
            text = self.ocr_data['text'][i].strip()
            if text:
                x = self.ocr_data['left'][i]
                y = self.ocr_data['top'][i]
                w = self.ocr_data['width'][i]
                h = self.ocr_data['height'][i]
                conf = int(self.ocr_data['conf'][i])
                
                # Adjust coordinates if ROI was used
                if self.roi_selected and self.roi_start is not None:
                    x += self.roi_start[0]
                    y += self.roi_start[1]
                
                # Draw bounding box (black for high confidence, dark gray for lower)
                color = (0, 0, 0) if conf > 50 else (64, 64, 64)
                cv2.rectangle(overlay_image, (x, y), (x + w, y + h), color, 2)
                
                # Draw text (black)
                cv2.putText(overlay_image, text, (x, y - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        self.display_image(overlay_image)
    
    def clear_all(self):
        self.current_image = None
        self.processed_image = None
        self.ocr_data = []
        self.roi_selected = False
        self.roi_start = None
        self.roi_end = None
        self.image_label.clear()
        self.image_label.setText("No image loaded\n\nClick 'Load Image' or 'Start Camera' to begin")
        self.text_display.clear()
        self.details_display.clear()
        if self.camera_thread.running:
            self.camera_thread.stop_camera()
            self.camera_btn.setText("Start Camera")
            self.capture_btn.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    
    # Apply global stylesheet to ensure all dialogs and widgets are styled
    app.setStyleSheet("""
        * {
            color: #212121 !important;
        }
        QWidget {
            background-color: #ffffff;
            color: #212121;
        }
        QDialog {
            background-color: #ffffff !important;
            color: #212121 !important;
        }
        QDialog QLabel {
            color: #212121 !important;
            background-color: #ffffff !important;
        }
        QMessageBox {
            background-color: #ffffff !important;
            color: #212121 !important;
        }
        QMessageBox QLabel {
            color: #212121 !important;
            background-color: #ffffff !important;
        }
        QMessageBox QPushButton {
            background-color: #ffffff !important;
            border: 1px solid #bdbdbd !important;
            border-radius: 4px;
            padding: 8px 16px;
            min-width: 80px;
            color: #212121 !important;
        }
        QMessageBox QPushButton:hover {
            background-color: #f5f5f5 !important;
            border: 1px solid #757575 !important;
            color: #212121 !important;
        }
        QFileDialog {
            background-color: #ffffff !important;
            color: #212121 !important;
        }
        QFileDialog * {
            color: #212121 !important;
            background-color: #ffffff !important;
        }
        QFileDialog QLabel {
            color: #212121 !important;
            background-color: #ffffff !important;
        }
        QFileDialog QLineEdit {
            background-color: #ffffff !important;
            border: 1px solid #bdbdbd !important;
            color: #212121 !important;
        }
        QFileDialog QListView {
            background-color: #ffffff !important;
            color: #212121 !important;
        }
        QFileDialog QTreeView {
            background-color: #ffffff !important;
            color: #212121 !important;
        }
        QFileDialog QComboBox {
            background-color: #ffffff !important;
            border: 1px solid #bdbdbd !important;
            color: #212121 !important;
        }
        QFileDialog QComboBox QAbstractItemView {
            background-color: #ffffff !important;
            color: #212121 !important;
            selection-background-color: #e0e0e0 !important;
            selection-color: #212121 !important;
        }
        QFileDialog QPushButton {
            background-color: #ffffff !important;
            border: 1px solid #bdbdbd !important;
            color: #212121 !important;
        }
        QFileDialog QPushButton:hover {
            background-color: #f5f5f5 !important;
            border: 1px solid #757575 !important;
            color: #212121 !important;
        }
    """)
    
    window = OCRScannerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

