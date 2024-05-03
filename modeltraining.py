import threading
from tkinter import Tk, Label, Entry, messagebox, filedialog, Canvas, Scrollbar
from PIL import Image, ImageTk
from pathlib import Path
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import ttkbootstrap as tb

# Global variables
captions_file = Path("captions.txt")
initialized = False

def initialize_resources():
    """
    Initialize NLP resources.
    """
    global initialized
    if not initialized:
        global stopwords_set, lemmatizer, pipeline_model
        stopwords_set = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        pipeline_model = pipeline("image-to-text", model="microsoft/git-large-textcaps")
        initialized = True

def generate_caption(image_path):
    """
    Generate caption for the given image using NLP model.
    """
    image = Image.open(image_path)
    caption = pipeline_model(images=image, max_new_tokens=50)
    return caption[0]

def generate_captions(image_paths):
    """
    Generate captions for a list of images and save them to a file.
    """
    existing_images = set()
    if captions_file.exists():
        with open(captions_file) as f:
            for line in f:
                image_path, _ = line.strip().split("|")
                existing_images.add(image_path)
    
    captions = {}
    for image_path in image_paths:
        if image_path in existing_images:
            print("Caption for", image_path, "already exists. Skipping.")
            continue
        
        print("Processing image:", image_path)
        caption_text = generate_caption(image_path)
        captions[image_path] = caption_text
        
    with open(captions_file, "a") as f:
        for image_path, caption_text in captions.items():
            f.write("{}|{}\n".format(image_path, caption_text))

def search_captions(query):
    """
    Search captions for the given query and return matched image paths.
    """
    query_words = nltk.word_tokenize(query)
    query_words = [w for w in query_words if w not in stopwords_set]
    query_words = [lemmatizer.lemmatize(w) for w in query_words]
    matched_images = []
    with open(captions_file) as f:
        for line in f:
            image_path, caption_text = line.strip().split("|")
            caption_words = nltk.word_tokenize(caption_text)
            caption_words = [lemmatizer.lemmatize(w) for w in caption_words]
            if any(qw in caption_words for qw in query_words):
                matched_images.append(image_path)
    return matched_images

def select_images(frame):
    """
    Create UI for selecting images.
    """
    def select():
        image_files = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", "*")])
        image_paths = [str(image_file) for image_file in image_files]
        if image_paths:
            generate_captions(image_paths)
            messagebox.showinfo("Information", "Captions generated for selected images.")
    
    label = Label(frame, text="Click below to select images:", font=("Arial", 16, "bold"))
    label.pack(pady=20)
    
    button = tb.Button(frame, text="Select Images", command=select, bootstyle="dark")
    button.pack(pady=20)

def open_image(image_path):
    """
    Open the image when clicked by the user.
    """
    image = Image.open(image_path)
    image.show()

def display_gallery(frame, images):
    """
    Display images in a gallery view with a scrollbar.
    """
    # Clear any existing content in the frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Create a canvas for the frame
    canvas = Canvas(frame)
    canvas.pack(side="left", fill="both", expand=True)

    # Create a scrollbar for the canvas
    scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    # Configure the canvas to use the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the images
    inner_frame = tb.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # Function to update the scroll region when the inner frame changes size
    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    inner_frame.bind("<Configure>", update_scroll_region)

    # Display images in the inner frame
    row, col = 0, 0
    for image_path in images:
        # Load and display image
        image = Image.open(image_path)
        image.thumbnail((250, 200))
        photo = ImageTk.PhotoImage(image)

        # Create label for image
        label = Label(inner_frame, image=photo)
        label.image = photo
        label.grid(row=row, column=col, padx=25, pady=10)

        # Bind click event to open the image
        label.bind("<Button-1>", lambda event, path=image_path: open_image(path))

        # Update row and col for next image placement
        col += 1
        if col == 6:
            col = 0
            row += 1

    # Update the scroll region of the canvas
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox(all))

def on_query_change(event):
    """
    Event handler for search query change.
    """
    query = entry.get()
    if query:
        matches = search_captions(query)
    else:
        # If no query, show all images
        matches = []
        if captions_file.exists():
            with open(captions_file) as f:
                for line in f:
                    image_path, caption_text = line.strip().split("|")
                    matches.append(image_path)
    display_gallery(gallery_frame, matches)

if __name__ == "__main__":
    # Initialize NLP resources in a separate thread
    thread = threading.Thread(target=initialize_resources)
    thread.start()
    
    # Wait for the initialization thread to complete
    thread.join()
    
    # Create main window
    root = tb.Window(themename="vapor")
    root.state("zoomed")
    root.resizable(True, True)
    root.title("Image Retriever")
    
    # Define a custom style for buttons
    button_style = tb.Style()
    button_style.configure("Custom.TButton", font=("Arial", 14), bootstyle="primary")
    
    # Create notebook
    notebook = tb.Notebook(root , bootstyle="dark", width="30") 
    notebook.pack(fill="both", expand=True, padx=25, pady=10)
    
    # Create frames for each page
    select_frame = tb.Frame(notebook)
    search_frame = tb.Frame(notebook)
    
    # Add frames to notebook
    notebook.add(select_frame, text="Select Images")
    notebook.add(search_frame, text="Search Query")
    
    # Populate frames with content
    select_images(select_frame)
    
    # Search bar
    label = Label(search_frame, text="Enter search query:", font=("Arial", 16, "bold"))
    label.pack(pady=20)

    entry = Entry(search_frame, font=("Arial", 14))
    entry.pack(pady=20)
    entry.bind("<KeyRelease>", on_query_change)  # Bind event handler for query change

   # Gallery frame
    gallery_frame = tb.Frame(search_frame)
    gallery_frame.pack(fill="both", expand=True)

    # Preload all images initially
    all_images = []
    if captions_file.exists():
        with open(captions_file) as f:
            for line in f:
                image_path, _ = line.strip().split("|")
                all_images.append(image_path)
    display_gallery(gallery_frame, all_images)

    root.mainloop()