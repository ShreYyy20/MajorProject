from tkinter import Tk, filedialog
from PIL import Image
from pathlib import Path
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
stopwords = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
captions_file = Path("captions.txt")
# Initialize the pipeline for generating captions
pipe = pipeline("image-to-text", model="microsoft/git-large-textcaps")
# Generate caption for single image
def generate_caption(image_path):
    image = Image.open(image_path)
    caption = pipe(images=image, max_new_tokens=50)
    return caption[0]  # Return the caption text

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
        
    # Write captions to the file
    with open(captions_file, "a") as f:
        for image_path, caption_text in captions.items():
            f.write("{}|{}\n".format(image_path, caption_text))
    
def search_captions(query):
    query_words = nltk.word_tokenize(query)
    query_words = [w for w in query_words if w not in stopwords]
    query_words = [lemmatizer.lemmatize(w) for w in query_words]  # Lemmatize words
    matched_images = []
    with open(captions_file) as f:
        for line in f:
            image_path, caption_text = line.strip().split("|")
            caption_words = nltk.word_tokenize(caption_text)
            caption_words = [lemmatizer.lemmatize(w) for w in caption_words]  # Lemmatize words
            if any(qw in caption_words for qw in query_words):
                matched_images.append((image_path, caption_text))
    return matched_images

def main():
    # Create Tkinter window
    root = Tk()
    root.withdraw()  # Hide the root window

    # Allow user to select multiple images
    image_files = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", "*")])
    image_paths = [str(image_file) for image_file in image_files]
    
    generate_captions(image_paths)
    
    query = input("Enter search query: ")
    matches = search_captions(query)  
    print("Matching images:", matches)
    
    # Open the matched images
    for image_path, _ in matches:
        image = Image.open(image_path.strip())  # Strip to remove any leading/trailing whitespace
        image.show()  # Open the image

if __name__ == "__main__":
    main()