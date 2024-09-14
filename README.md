---

# Image Captioning and Retrieval Application

This project is a GUI-based application that allows users to generate captions for selected images using a pre-trained image-to-text model. Users can search through generated captions and retrieve matching images based on text queries.

## Features
- **Image Captioning**: Automatically generates descriptive captions for selected images using a pre-trained model.
- **Image Search**: Allows users to search through captions and display images matching the search query.
- **Image Gallery**: Displays all images with generated captions in a scrollable gallery interface.
- **Interactive UI**: Built with `Tkinter` and styled using `ttkbootstrap`, providing a responsive and modern user interface.

## Technologies Used
- **Python**: Core programming language.
- **Tkinter**: For the GUI interface.
- **ttkbootstrap**: For enhanced styling of the Tkinter interface.
- **Pillow (PIL)**: For image manipulation and display.
- **Transformers**: Hugging Face's library used to load a pre-trained image-to-text model.
- **NLTK**: Used for text processing in the search functionality.
- **Threading**: To initialize NLP resources in the background.

## How It Works
### 1. Caption Generation
Users select images, and the application generates descriptive captions using a pre-trained image-to-text model from Hugging Face (`microsoft/git-large-textcaps`). Captions are saved in a `captions.txt` file, ensuring that previously processed images are not captioned again.

### 2. Search Functionality
Users can search for images based on their captions. The search algorithm tokenizes and lemmatizes the query, filters out stopwords, and checks for exact or fuzzy matches between the query words and the stored captions.

### 3. Displaying Results
Images matching the search query are displayed in a gallery format. Users can click on any image to open it in full view.

## Installation

### Prerequisites
Make sure you have the following installed:
- Python 3.x
- Pip (Python package manager)

### Step-by-step guide:
1. **Clone the repository:**
    ```bash
    git clone https://github.com/ShreYyy20/Image_Captioning_and_Retrieval.git
    cd Image_Captioning_and_Retrieval
    ```

2. **Install required packages:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Download NLTK resources:**
    The application uses NLTK's stopwords and lemmatizer. Run the following in a Python shell to download the necessary resources:
    ```python
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    ```

4. **Run the application:**
    ```bash
    python main.py
    ```

## Usage
1. **Select Images**: 
   - Navigate to the "Select Images" tab.
   - Click the "Select Images" button to choose images from your file system.
   - Captions will be automatically generated and saved in `captions.txt`.
   
2. **Search Images**:
   - Navigate to the "Search Query" tab.
   - Enter a search query in the provided text field.
   - Matching images will be displayed in the gallery below. Click any image to view it.

## File Structure
```bash
.
├── captions.txt           # File that stores image paths and their captions
├── main.py                # Main script for running the application
└── requirements.txt       # List of required Python packages
```

## Requirements
- Python 3.x
- Pip packages:
  - `Pillow`
  - `transformers`
  - `ttkbootstrap`
  - `nltk`

## Model Information
This project uses Hugging Face’s `microsoft/git-large-textcaps` model to generate captions from images. You can read more about the model [here](https://huggingface.co/microsoft/git-large-textcaps).


## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request for improvements or bug fixes.

---
