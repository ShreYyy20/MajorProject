import threading
import webbrowser
from tkinter import Tk, ttk, Label, Entry, messagebox, filedialog
from tkinter.font import Font
from PIL import Image
from pathlib import Path
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

captions_file = Path("captions.txt")
initialized = False

def initialize():
    global initialized
    if not initialized:
        global stopwords, lemmatizer, pipe
        stopwords = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        pipe = pipeline("image-to-text", model="microsoft/git-large-textcaps")
        initialized = True

def generate_caption(image_path):
    image = Image.open(image_path)
    caption = pipe(images=image, max_new_tokens=50)
    return caption[0]

def generate_captions(image_paths):
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
    query_words = nltk.word_tokenize(query)
    query_words = [w for w in query_words if w not in stopwords]
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
    def select():
        image_files = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", "*")])
        image_paths = [str(image_file) for image_file in image_files]
        if image_paths:
            generate_captions(image_paths)
            messagebox.showinfo("Information", "Captions generated for selected images.")
    
    label = Label(frame, text="Click below to select images:", font=("Arial", 16, "bold"), bg="#08026c", fg="goldenrod")
    label.pack(pady=20)
    
    button = ttk.Button(frame, text="Select Images", command=select, style="Custom.TButton")
    button.pack(pady=20)

def search_query(frame):
    def search():
        query = entry.get()
        matches = search_captions(query)
        if matches:
            for image_path in matches:
                webbrowser.open(image_path)
        else:
            messagebox.showinfo("Information", "No matching images found.")
    
    label = Label(frame, text="Enter search query:", font=("Arial", 16, "bold"), bg="#08026c", fg="goldenrod")
    label.pack(pady=20)

    entry = Entry(frame, font=("Arial", 14))
    entry.pack(pady=20)

    button = ttk.Button(frame, text="Search", command=search, style="Custom.TButton")
    button.pack(pady=20)

if __name__ == "__main__":
    # Initialize the resources in a separate thread
    thread = threading.Thread(target=initialize)
    thread.start()
    
    # Wait for the initialization thread to complete
    thread.join()
    
    # Create main window
    root = Tk()
    root.state("zoomed")
    root.resizable(True, True)
    root.attributes("-topmost", True)
    root.title(" Image Retriever")
    root.geometry("600x600")
    root.configure(bg="#08026c")
    
    # Define a custom style for buttons with darker blue color
    button_style = ttk.Style()
    button_style.configure("Custom.TButton", font=("Arial", 14), background="#062a78", foreground="goldenrod", relief="groove", hovercolor="#3d8d")
    button_style.configure("Custom.TButton", font=("Arial", 14,),background="#062a78", foreground="goldenrod", relief="flat",hover_color="#0d8d")
    
    # Create notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)
    
    # Define a custom style for frames with the desired background color
    frame_style = ttk.Style()
    frame_style.configure("Custom.TFrame", background="#08026c")
    
    # Create frames for each page
    select_frame = ttk.Frame(notebook, style="Custom.TFrame")
    search_frame = ttk.Frame(notebook, style="Custom.TFrame")
    
    # Add frames to notebook
    notebook.add(select_frame, text="Select Images")
    notebook.add(search_frame, text="Search Query")
    
    # Populate frames with content
    select_images(select_frame)
    search_query(search_frame)
    
    root.mainloop()
