import threading
from tkinter import Tk, Label, Entry, messagebox, filedialog, Canvas, Scrollbar
from PIL import Image, ImageTk
from pathlib import Path
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import ttkbootstrap as tb
import re
# Global variables
captions_file = Path("captions.txt")
initialized = False

#INITALIZING THE NLP RESOURCES
def initialize_resources():
    global initialized
    if not initialized:
        global stopwords_set, lemmatizer, pipeline_model
        stopwords_set = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        pipeline_model = pipeline("image-to-text", model="microsoft/git-large-textcaps")
        initialized = True
#GENERATE CAPTION FOR THE IMAGE
def generate_caption(image_path):
    image = Image.open(image_path)
    caption = pipeline_model(images=image, max_new_tokens=50)
    return caption[0]
#GENERATING CAPTIONS FOR THE LIST OF IMAGES AND SAVING THEM TO  CAPTIONS.TXT FILE.
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
#SEARCHING CAPTIONS BASED ON THE GIVEN QUERY AND THEN RETURNING THE MATCHED IMAGES
def search_captions(query):
    query = query.lower()  # Convert the query to lowercase
    query_words = nltk.word_tokenize(query)
    query_words = [w for w in query_words if w not in stopwords_set]
    query_words = [lemmatizer.lemmatize(w) for w in query_words]

    matched_images = []
    with open(captions_file) as f:
        for line in f:
            image_path, caption_text = line.strip().split("|")
            caption_text = caption_text.lower()  # Convert the caption text to lowercase

            # Check for an exact match
            if any(qw in caption_text for qw in query_words):
                matched_images.append(image_path)
                continue

            # Check for a fuzzy match (to handle typos)
            for qw in query_words:
                pattern = fr'\b{qw}\b'
                if re.search(pattern, caption_text, re.IGNORECASE):
                    matched_images.append(image_path)
                    break

    return matched_images


#UI FOR THE SELECT IMAGES PAGE
def select_images(frame):
    def select():
        image_files = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", ".jpg, .png , .CR2 , .bmp , .jpeg, .webp , .")])
        image_paths = [str(image_file) for image_file in image_files]
        if image_paths:
            generate_captions(image_paths)
            messagebox.showinfo("Information", "Captions generated for selected images.")
    
    label = Label(frame, text="Click below to select images:", font=("Arial", 16, "bold"))
    label.pack(pady=20)
    
    button = tb.Button(frame, text="Select Images", command=select, bootstyle="dark")
    button.pack(pady=20)
#FUNCTION TO OPEN THE IMAGE CLICKED BY A USER
def open_image(image_path):
    image = Image.open(image_path)
    image.show()
#DISPLAY IMAGES IN A GALLERY
def display_gallery(frame, images):
    #if any existing content is present then clear them
    for widget in frame.winfo_children():
        widget.destroy()
    #Canvas for the frame
    canvas = Canvas(frame)
    canvas.pack(side="left", fill="both", expand=True)
    #Scrollbar 
    scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
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
        #Image Label
        label = Label(inner_frame, image=photo)
        label.image = photo
        label.grid(row=row, column=col, padx=25, pady=10)
        label.bind("<Button-1>", lambda event, path=image_path: open_image(path))
        #dynamic Columns and rows placement
        col += 1
        if col == 6:
            col = 0
            row += 1
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox(all))
#Event handler for search query change.
def on_query_change(event):
    query = entry.get()
    if query:
        matches = search_captions(query)
    else:
        #showing all images when no query is present
        matches = []
        if captions_file.exists():
            with open(captions_file) as f:
                for line in f:
                    image_path, caption_text = line.strip().split("|")
                    matches.append(image_path)
    display_gallery(gallery_frame, matches)

if __name__ == "__main__":
    #NLP initializing
    thread = threading.Thread(target=initialize_resources)
    thread.start()
    thread.join()
    # Create main window
    root = tb.Window(themename="morph")
    root.state("zoomed")
    root.resizable(True, True)
    root.title("Image Retriever")
    button_style = tb.Style()
    button_style.configure("Custom.TButton", font=("Arial", 14), bootstyle="primary")
    #notebook
    notebook = tb.Notebook(root , bootstyle="dark", width="30") 
    notebook.pack(fill="both", expand=True, padx=25, pady=10)
    #frames
    select_frame = tb.Frame(notebook)
    search_frame = tb.Frame(notebook)
    notebook.add(select_frame, text="Select Images")
    notebook.add(search_frame, text="Search Query")
    select_images(select_frame)
    # Search bar
    label = Label(search_frame, text="Enter search query:", font=("Arial", 16, "bold"))
    label.pack(pady=20)
    entry = Entry(search_frame, font=("Arial", 14))
    entry.pack(pady=20)
    entry.bind("<KeyRelease>", on_query_change) #Query change event handling
    # Gallery frame
    gallery_frame = tb.Frame(search_frame)
    gallery_frame.pack(fill="both", expand=True)
    # Preloading images initially
    all_images = []
    if captions_file.exists():
        with open(captions_file) as f:
            for line in f:
                image_path, _ = line.strip().split("|")
                all_images.append(image_path)
    display_gallery(gallery_frame, all_images)
    root.mainloop()