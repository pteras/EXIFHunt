# EXIFHunt

EXIFHunt is a lightweight and user-friendly python script designed to extract and organize EXIF data from images and videos. 

## Features

- Extract EXIF data from multiple images and videos in a selected folder
- Generate reports in PDF or text format
- User-friendly interface
- Great tool for CTF

### Supported Image Extensions
- .jpg
- .jpeg
- .png
- .bmp
- .gif
- .tiff

### Supported Video Extensions
- .mp4
- .mov
- .avi
- .mkv
- .wmv
- .flv

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/pteras/EXIFHunt.git
    cd EXIFHunt
    ```

2. **Install the required dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

3. **Run the application:**

    ```sh
    python main.py
    ```

## Requirements

- Python 3.x
- [Pillow](https://python-pillow.org/)
- [hachoir](https://github.com/vstinner/hachoir)
- [FPDF](http://www.fpdf.org/)
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter)

## Screenshots

![EXIFHunt](https://github.com/user-attachments/assets/05ea5a1a-bc9f-479d-82ac-e8cb3c68af4e)

![Example Report Output](https://github.com/user-attachments/assets/d37393ef-da2a-4df2-8981-e6e54444fcc2)

## Contributing

Please fork this repository and submit a pull request with your improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
