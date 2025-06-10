import os
import datetime
from tkinter import StringVar, filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from PIL.ExifTags import TAGS
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from fpdf import FPDF
import cv2
import webbrowser
import shutil

# Functions to extract EXIF data
def extract_exif(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    if exif_data:
        return {TAGS.get(tag): value for tag, value in exif_data.items()}
    return {}

def extract_metadata(video_path):
    parser = createParser(video_path)
    metadata = extractMetadata(parser)
    if metadata:
        return metadata.exportDictionary()
    return {}

def get_exif_data(directory, process_images, process_videos):
    exif_data = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if process_images and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            exif_data[filename] = extract_exif(file_path)
        elif process_videos and filename.lower().endswith(('.mp4', '.mov', '.avi')):
            exif_data[filename] = extract_metadata(file_path)
    return exif_data

# Functions to generate reports
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'EXIFHunt Report', ln=True, align='C')
        self.ln(5)

    def add_media_section(self, filename, exif_data, media_path, is_image=True):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, filename, ln=True)
        self.ln(2)
        if include_file_size_var.get():
            size = os.path.getsize(media_path)
            self.multi_cell(0, 8, f"File Size: {size / 1024:.2f} KB")

        if include_timestamps_var.get():
            stat = os.stat(media_path)
            created = datetime.datetime.fromtimestamp(stat.st_ctime)
            modified = datetime.datetime.fromtimestamp(stat.st_mtime)
            self.multi_cell(0, 8, f"Created: {created}")
            self.multi_cell(0, 8, f"Modified: {modified}")

        # Add image or video thumbnail
        try:
            thumb_path = self.create_thumbnail(media_path, is_image)
            if thumb_path:
                self.image(thumb_path, w=60)
        except Exception as e:
            self.set_font('Arial', '', 10)
            self.multi_cell(0, 10, f"[Thumbnail not available: {e}]")

        self.ln(5)
        self.set_font('Arial', '', 11)
        for key, value in exif_data.items():
            self.multi_cell(0, 8, f"{key}: {value}")
        self.ln(10)

    def create_thumbnail(self, path, is_image=True):
        thumb_dir = "thumbnails"
        os.makedirs(thumb_dir, exist_ok=True)
        filename = os.path.splitext(os.path.basename(path))[0]
        thumb_path = os.path.join(thumb_dir, f"{filename}_thumb.jpg")

        if is_image:
            image = Image.open(path)
            image.thumbnail((thumbnail_size_var.get(), thumbnail_size_var.get()))
            image.convert('RGB').save(thumb_path, "JPEG")
        else:
            # Use OpenCV to get the first frame
            cap = cv2.VideoCapture(path)
            success, frame = cap.read()
            if success:
                cv2.imwrite(thumb_path, frame)
            cap.release()
        return thumb_path if os.path.exists(thumb_path) else None

def create_pdf_report(exif_data, output_directory):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = os.path.join(output_directory, f'exif_{timestamp}.pdf')

    os.makedirs(output_directory, exist_ok=True)

    pdf = PDFReport()
    pdf.add_page()

    for filename, data in exif_data.items():
        file_path = os.path.join(folder_path.get(), filename)
        ext = os.path.splitext(filename)[1].lower()
        is_image = ext in ['.jpg', '.jpeg', '.png']
        pdf.add_media_section(filename, data, file_path, is_image=is_image)

    pdf.output(output_path)
    return output_path


def create_text_report(exif_data, output_directory):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = os.path.join(output_directory, f'exif_{timestamp}.txt')
    os.makedirs(output_directory, exist_ok=True)

    with open(output_path, 'w') as file:
        for filename, data in exif_data.items():
            file.write(f"{filename}\n")
            for key, value in data.items():
                file.write(f"  {key}: {value}\n")
            file.write("\n")

    return output_path

def generate_report():
    directory = folder_path.get()
    
    output_directory = output_folder_path.get() or "results"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        
    if not directory:
        messagebox.showerror("Error", "Please select a folder.")
        return

    process_images = images_var.get()
    process_videos = videos_var.get()
    output_format = output_format_var.get() or default_format_var.get()
    
    if not process_images and not process_videos:
        messagebox.showerror("Error", "Please select at least one file type (images or videos).")
        return
    
    if output_format not in [1, 2]:
        messagebox.showerror("Error", "Please select an output format.")
        return

    exif_data = get_exif_data(directory, process_images, process_videos)
    
    if output_format == 1:
        output_path = create_pdf_report(exif_data, output_directory)
    elif output_format == 2:
        output_path = create_text_report(exif_data, output_directory)
    
    messagebox.showinfo("Success", f"Report generated: {output_path}")
    
    if open_report_var.get():
        open_report(output_path)

    if cleanup_thumbnails_var.get():
        shutil.rmtree("thumbnails", ignore_errors=True)

def open_report(output_path):
    if os.path.exists(output_path):
        webbrowser.open(output_path)
    else:
        messagebox.showerror("Error", "The report file does not exist.")

def select_folder():
    folder = filedialog.askdirectory()
    folder_path.set(folder)
    if not contains_compatible_files(folder):
        messagebox.showerror("Error", "The folder contains no compatible images/videos.")

def contains_compatible_files(directory):
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv')
    for filename in os.listdir(directory):
        if filename.lower().endswith(image_extensions) or filename.lower().endswith(video_extensions):
            return True
    return False

def select_output_folder():
    folder = filedialog.askdirectory()
    output_folder_path.set(folder)



# CustomTkinter window
root = ctk.CTk()
root.title("EXIFHunt v1.2")
root.iconbitmap('assets\icon.ico')
root.geometry("600x450")
root.resizable(True, True)
root.minsize(600, 450)

# Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
theme_switch_var = ctk.BooleanVar(value=True)  # start in dark mode

def toggle_theme():
    if theme_switch_var.get():
        ctk.set_appearance_mode("dark")
    else:
        ctk.set_appearance_mode("light")

# Responsiveness
root.update_idletasks()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 450
window_height = 400  
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

ctk.CTkLabel(root, text="2025 v1.2 @pteras", font=("Arial", 10), text_color="gray").grid(row=5, column=0, sticky="w", padx=10, pady=10)

folder_path = StringVar(value=os.path.dirname(__file__))
output_folder_path = StringVar(value=os.path.join(os.path.dirname(__file__), "reports"))
images_var = ctk.BooleanVar()
videos_var = ctk.BooleanVar()
output_format_var = ctk.IntVar()
open_report_var = ctk.BooleanVar(value=False)

thumbnail_size_var = ctk.IntVar(value=300)
include_file_size_var = ctk.BooleanVar(value=True)
include_timestamps_var = ctk.BooleanVar(value=True)
default_format_var = ctk.IntVar(value=1)
cleanup_thumbnails_var = ctk.BooleanVar(value=True)


# Tabs
tab_view = ctk.CTkTabview(root)
tab_view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Generate 
tab_generate = tab_view.add("Generate")
ctk.CTkLabel(master=tab_generate, text="Select Media:").grid(row=0, column=0, padx=10, pady=10, sticky="e")

tab_generate.grid_rowconfigure(0, weight=1)
tab_generate.grid_columnconfigure(1, weight=1)

ctk.CTkEntry(tab_generate, textvariable=folder_path).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
ctk.CTkButton(tab_generate, text="Browse", command=select_folder).grid(row=0, column=2, padx=10, pady=10)

ctk.CTkLabel(master=tab_generate, text="Output Folder:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
ctk.CTkEntry(tab_generate, textvariable=output_folder_path).grid(row=1, column=1, padx=10, pady=10, sticky="ew")
ctk.CTkButton(tab_generate, text="Browse", command=select_output_folder).grid(row=1, column=2, padx=10, pady=10)

ctk.CTkLabel(master=tab_generate, text="File Types:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
ctk.CTkCheckBox(tab_generate, text="Images", variable=images_var).grid(row=2, column=1, sticky="w")
ctk.CTkCheckBox(tab_generate, text="Videos", variable=videos_var).grid(row=2, column=2, sticky="w")

ctk.CTkLabel(master=tab_generate, text="Save As:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
ctk.CTkRadioButton(tab_generate, text="PDF", variable=output_format_var, value=1).grid(row=3, column=1, sticky="w")
ctk.CTkRadioButton(tab_generate, text="Text", variable=output_format_var, value=2).grid(row=3, column=2, sticky="w")

ctk.CTkCheckBox(tab_generate, text="Open Report Once Ready", variable=open_report_var).grid(row=4, column=0, columnspan=3, pady=10)

ctk.CTkButton(tab_generate, text="Generate EXIF Report", command=generate_report).grid(row=5, column=0, columnspan=3, pady=20)

# Settings tab
tab_settings = tab_view.add("Settings")
tab_settings.grid_columnconfigure(1, weight=1)

ctk.CTkLabel(tab_settings, text="Thumbnail Size (pixels):").grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
ctk.CTkSlider(tab_settings, from_=100, to=600, variable=thumbnail_size_var, number_of_steps=10).grid(row=0, column=1, padx=10, pady=(10, 0), sticky="ew")

ctk.CTkCheckBox(tab_settings, text="Include File Size in Report", variable=include_file_size_var).grid(row=1, column=0, columnspan=2, sticky="w", padx=10)
ctk.CTkCheckBox(tab_settings, text="Include File Timestamps", variable=include_timestamps_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=10)
ctk.CTkCheckBox(tab_settings, text="Clear Thumbnails After Report", variable=cleanup_thumbnails_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=10)

ctk.CTkLabel(tab_settings, text="Default Report Format:").grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")
ctk.CTkRadioButton(tab_settings, text="PDF", variable=default_format_var, value=1).grid(row=4, column=1, sticky="w")
ctk.CTkRadioButton(tab_settings, text="Text", variable=default_format_var, value=2).grid(row=5, column=1, sticky="w")
ctk.CTkButton(tab_settings, text="Reset Settings", command=lambda: (thumbnail_size_var.set(300), include_file_size_var.set(True), include_timestamps_var.set(True), cleanup_thumbnails_var.set(True), default_format_var.set(1))).grid(row=6, column=0, padx=10, pady=(10, 0), sticky="ew")
ctk.CTkSwitch(tab_settings, text="Dark Mode", variable=theme_switch_var, command=toggle_theme).grid(row=6, column=1, sticky="w", padx=10, pady=(10, 0))


# About tab
tab_about = tab_view.add("About")
ctk.CTkLabel(tab_about, text="EXIFHunt v1.2\n\nA tool for extracting EXIF metadata from images and videos and generating reports.\n\nDeveloped by @pteras", justify="center").grid(row=0, column=0, padx=10, pady=10)
tab_about.grid_rowconfigure(0, weight=1)
tab_about.grid_columnconfigure(0, weight=1)

# Grid layout for the window
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.minsize(600, 450)

# Start the application
root.mainloop()
