import threading
import webbrowser
from tkinter import Tk, Button, Label, Entry, messagebox, filedialog
from PIL import Image
from pathlib import Path
from tkinter import ttk
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

def select_images():
    root = Tk()
    root.attributes("-topmost", True)
    root.focus_set()
    root.title("Select Images")
    root.configure(bg="#08026c")
    
    def select():
        image_files = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", "*")])
        image_paths = [str(image_file) for image_file in image_files]
        if image_paths:
            generate_captions(image_paths)
            messagebox.showinfo("Information", "Captions generated for selected images.")
        root.destroy()
    
    label = Label(root, text="Click below to select images:", font=("Trebuchet MS", 24), bg="#08026c",foreground="yellow")
    label.pack(pady=10)
    
    button_style = ttk.Style()
    button_style.configure("TButton", font=("Trebuchet MS", 24), background="#4CA", foreground="yellow", padx=10, pady=5)
    
    button = ttk.Button(root, text="Select Images", command=select)
    button.pack(pady=10)
    
    root.mainloop()

def search_query():
    root = Tk()
    root.attributes("-topmost", True)
    root.focus_set()
    root.title("Search Query")
    root.configure(bg="#08026c")
    
    def search():
        query = entry.get()
        matches = search_captions(query)
        if matches:
            for image_path in matches:
                webbrowser.open(image_path)
        else:
            messagebox.showinfo("Information", "No matching images found.")
        root.destroy()
    
    label = Label(root, text="Enter search query:", font=("Trebuchet MS", 24), bg="#08026c", foreground="yellow")
    label.pack(pady=10)
    
    entry_style = ttk.Style()
    entry_style.configure("TEntry", font=("Trebuchet MS", 24), padx=10, pady=5)
    
    entry = Entry(root, font=("Trebuchet MS", 24))
    entry.pack(pady=10)
    
    button = ttk.Button(root, text="Search", command=search)
    button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    # Initialize the resources in a separate thread
    thread = threading.Thread(target=initialize)
    thread.start()
    
    # Wait for the initialization thread to complete
    thread.join()
    
    # Run the GUI
    select_images()
    search_query()
