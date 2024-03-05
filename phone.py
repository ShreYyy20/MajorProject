from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.lang import Builder
from kivy.core.window import Window
from pathlib import Path
from PIL import Image
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Set up transformer pipeline
pipe = pipeline("image-to-text", model="microsoft/git-large-textcaps")

# Path for captions file
captions_file = Path("captions.txt")


class ImageRetrieverApp(App):
    def build(self):
        self.title = "Image Retriever"
        return MainScreen()


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.orientation = "vertical"

        # Widgets
        self.select_button = Button(text="Select Images", size_hint=(1, 0.1))
        self.search_button = Button(text="Search", size_hint=(1, 0.1))
        self.query_input = TextInput(hint_text="Enter search query", size_hint=(1, 0.1))
        self.results_label = Label(text="", size_hint=(1, 0.6))

        # Bind events
        self.select_button.bind(on_press=self.select_images)
        self.search_button.bind(on_press=self.search_query)

        # Add widgets to layout
        self.add_widget(self.select_button)
        self.add_widget(self.search_button)
        self.add_widget(self.query_input)
        self.add_widget(self.results_label)

    def select_images(self, instance):
        file_chooser = FileChooserListView()
        file_chooser.bind(on_submit=self.generate_captions_popup)
        popup = Popup(title="Select Images", content=file_chooser, size_hint=(0.9, 0.9))
        popup.open()

    def generate_captions_popup(self, instance, selected_files):
        image_paths = [str(file) for file in selected_files]
        self.generate_captions(image_paths)
        popup = Popup(title="Information", content=Label(text="Captions generated for selected images."), size_hint=(None, None), size=(400, 200))
        popup.open()



    def generate_captions(self, image_paths):
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
            caption_text = self.generate_caption(image_path)
            captions[image_path] = caption_text

        with open(captions_file, "a") as f:
            for image_path, caption_text in captions.items():
                f.write("{}|{}\n".format(image_path, caption_text))

    def generate_caption(self, image_path):
        image = Image.open(image_path)
        caption = pipe(images=image, max_new_tokens=50)
        return caption[0]

    def search_query(self, instance):
        query = self.query_input.text
        matches = self.search_captions(query)
        if matches:
            self.results_label.text = "\n".join(matches)
        else:
            self.results_label.text = "No matching images found."

    def search_captions(self, query):
        query_words = nltk.word_tokenize(query)
        query_words = [lemmatizer.lemmatize(w) for w in query_words if w.lower() not in stop_words]
        matched_images = []
        with open(captions_file) as f:
            for line in f:
                image_path, caption_text = line.strip().split("|")
                caption_words = nltk.word_tokenize(caption_text)
                caption_words = [lemmatizer.lemmatize(w) for w in caption_words]
                if any(qw in caption_words for qw in query_words):
                    matched_images.append(image_path)
        return matched_images


if __name__ == "__main__":
    Window.size = (400, 600)
    ImageRetrieverApp().run()
