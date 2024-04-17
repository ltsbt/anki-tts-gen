from random import randint
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.ttk as ttk
import os
import genanki
import tts


class App(tk.Tk):
    def __init__(self):
        """Initialize the main window"""
        super().__init__()

        self.title("Anki TTS Generator")

        WIDTH = 350
        HEIGHT = 300
        x_offset = (self.winfo_screenwidth() - WIDTH) // 2
        y_offset = (self.winfo_screenheight() - HEIGHT) // 2

        # center the window on the screen
        self.geometry(f"+{x_offset}+{y_offset}")
        self.resizable(False, False)

        self.update_idletasks()
        self.grid_columnconfigure(0, weight=0, pad=10)
        self.grid_columnconfigure(1, weight=1)

        self["padx"] = 10
        self["pady"] = 10

        self.anki_deck_name = ""
        """Name of the Anki deck"""
        self.anki_deck_id = randint(1 << 30, 1 << 31)
        """ID of the Anki deck. For now, randomly generated."""
        self.anki_model_id = randint(1 << 30, 1 << 31)
        """ID of the Anki model. For now, randomly generated."""
        self.piper_model_file = ""
        """Piper model file"""
        self.text_file = ""
        """Text file containing phrases"""
        self.is_pairs = tk.BooleanVar(value=False)
        """Whether the input text file is a list of translation pairs or single language sentences"""
        self.keep_audio = tk.BooleanVar(value=False)
        """Whether to keep audio files after generating the Anki deck"""
        self.output_dir = ""
        """Output directory for the Anki deck"""
        self.exists_model_json = False
        """Whether a JSON file exists for the model"""

        # read deck name
        deck_name_label = tk.Label(self, text="Deck Name:")
        self.deck_name_input = tk.Entry(self, justify="center")
        deck_name_label.grid(row=0, column=0, sticky="w")
        self.deck_name_input.grid(row=0, column=1, sticky="ew")

        # # read deck id (int)
        # deck_id_label = tk.Label(self, text="Deck ID")
        # self.deck_id_input = tk.Entry(self, validate="key")
        # self.deck_id_input["validatecommand"] = (
        #     self.register(lambda value: value.isnumeric()),
        #     "%P",
        # )
        # deck_id_label.pack()
        # self.deck_id_input.pack()

        # # read model id (int)
        # model_id_label = tk.Label(self, text="Model ID")
        # self.model_id_input = tk.Entry(self, validate="key")
        # self.model_id_input["validatecommand"] = (
        #     self.register(lambda value: value.isnumeric()),
        #     "%P",
        # )
        # model_id_label.pack()
        # self.model_id_input.pack()

        # choose .onnx model file
        model_file_label = tk.Label(self, text="Model File:")
        # warning button for missing JSON file
        model_json_warning = tk.Button(
            self,
            text="↻ No JSON file found for this model. Click to retry.",
            highlightbackground="red",
        )

        def on_model_file_input_click():
            new_model_file = fd.askopenfilename(filetypes=[("ONNX files", "*.onnx")])
            if new_model_file in ((), ""):
                return
            self.piper_model_file = new_model_file
            self.piper_model_file_input["text"] = new_model_file.split(os.sep)[-1]
            # check if, in the same directory, there is a file with the same name + ".json"
            self.exists_model_json = os.path.exists(self.piper_model_file + ".json")

            # only show warning button if the JSON file does not exist
            if not self.exists_model_json:
                model_json_warning.grid(row=15, column=0, columnspan=2, sticky="ew")
                self.piper_model_file_input.config(highlightbackground="red")
            # otherwise, hide the button
            else:
                model_json_warning.grid_forget()
                self.piper_model_file_input.config(highlightbackground="#d9d9d9")

        self.piper_model_file_input = tk.Button(
            self, text="Choose a model file...", command=on_model_file_input_click
        )

        model_file_label.grid(row=1, column=0, sticky="w")
        self.piper_model_file_input.grid(row=1, column=1, sticky="ew")

        # choose text file
        text_file_label = tk.Label(self, text="Text File:")

        def on_text_file_input_click():
            new_text_file = fd.askopenfilename(filetypes=[("Text files", "*.txt")])
            if new_text_file in ((), ""):
                return
            self.text_file = new_text_file
            self.text_file_input["text"] = new_text_file.split(os.sep)[-1]
            self.text_file_input.config(highlightbackground="#d9d9d9")

        self.text_file_input = tk.Button(
            self, text="Choose a text file...", command=on_text_file_input_click
        )

        text_file_label.grid(row=2, column=0, sticky="w")
        self.text_file_input.grid(row=2, column=1, sticky="ew")

        # toggle is_pairs
        pairs_label = tk.Label(self, text="Input Type:")
        pairs_checkbox = tk.Checkbutton(
            self, text="Translation Pairs", variable=self.is_pairs
        )
        pairs_label.grid(row=3, column=0, sticky="w")
        pairs_checkbox.grid(row=3, column=1, sticky="ew")

        # choose output directory
        output_dir_label = tk.Label(self, text="Output Directory:")

        def on_output_dir_input_click():
            new_dir = fd.askdirectory()
            if new_dir in ((), ""):
                return
            self.output_dir = new_dir
            self.output_dir_input["text"] = new_dir.split(os.sep)[-1]
            self.output_dir_input.config(highlightbackground="#d9d9d9")

        self.output_dir_input = tk.Button(
            self,
            text="Choose an output directory...",
            command=on_output_dir_input_click,
        )
        output_dir_label.grid(row=4, column=0, sticky="w")
        self.output_dir_input.grid(row=4, column=1, sticky="ew")

        # toggle keep_audio
        keep_audio_label = tk.Label(self, text="Keep Audio Files:")
        keep_audio_checkbox = tk.Checkbutton(
            self, text="Keep audio files", variable=self.keep_audio
        )
        keep_audio_label.grid(row=5, column=0, sticky="w")
        keep_audio_checkbox.grid(row=5, column=1, sticky="ew")

        # submit button
        submit_button = tk.Button(self, text="Generate deck", command=self.submit)
        submit_button.grid(row=10, column=1, pady=15, sticky="ew")

    def submit(self):
        is_input_valid = True

        self.anki_deck_name = self.deck_name_input.get()

        if self.anki_deck_name == "":
            self.deck_name_input.config(highlightbackground="red")
            is_input_valid = False
        else:
            self.deck_name_input.config(highlightbackground="#d9d9d9")

        if self.piper_model_file == "":
            self.piper_model_file_input.config(highlightbackground="red")
            is_input_valid = False
        else:
            self.piper_model_file_input.config(highlightbackground="#d9d9d9")

        if self.text_file == "":
            self.text_file_input.config(highlightbackground="red")
            is_input_valid = False
        else:
            self.text_file_input.config(highlightbackground="#d9d9d9")

        if self.output_dir == "":
            self.output_dir_input.config(highlightbackground="red")
            is_input_valid = False
        else:
            self.output_dir_input.config(highlightbackground="#d9d9d9")

        if not is_input_valid:
            return

        self.generate_anki_deck()

    def generate_anki_deck(self):
        """Open new window showing the progress of generating Anki deck"""
        progress_window = tk.Toplevel(self)
        progress_window.title("Generating Anki Deck")
        width = 400
        height = 200
        x_offset = (self.winfo_screenwidth() - width) // 2
        y_offset = (self.winfo_screenheight() - height) // 2
        progress_window.geometry(f"{width}x{height}+{x_offset}+{y_offset}")
        progress_window.resizable(False, False)

        progress_bar = ttk.Progressbar(progress_window, length=300, mode="determinate")
        progress_bar.pack(pady=[50, 10])

        deck = genanki.Deck(self.anki_deck_id, self.anki_deck_name)

        model = genanki.Model(
            self.anki_model_id,
            "TTS Model",
            fields=[
                {"name": "Audio"},
                {"name": "Text"},
            ],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": "{{Audio}}",
                    "afmt": '{{FrontSide}}<hr id="answer">{{Text}}',
                },
            ],
        )

        with open(self.text_file, "r") as f:
            phrases = f.readlines()

        dir_exists = os.path.exists(f"{self.output_dir}{os.sep}audios")
        if not dir_exists:
            os.makedirs(f"{self.output_dir}{os.sep}audios")

        for i, phrase in enumerate(phrases):
            if self.is_pairs and i % 2 != 0:
                continue

            audio_index = i if not self.is_pairs.get() else i // 2

            tts.tts_gen(
                self.output_dir,
                self.piper_model_file,
                audio_index,
                phrase,
            )

            note_back = (
                f"{phrases[i]}\n{phrases[i + 1]}" if self.is_pairs.get() else phrases[i]
            )

            new_note = genanki.Note(
                model=model,
                fields=[
                    f"[sound:tts_{audio_index}.wav]",
                    note_back,
                ],
            )

            deck.add_note(new_note)

            progress_bar["value"] = i / len(phrases) * 100
            progress_window.update()

        progress_bar["value"] = 100
        progress_window.update()

        # success message
        success_label = tk.Label(
            progress_window, text="Anki deck generated successfully!"
        )
        success_label.pack(pady=10)

        # button to close the progress window
        close_button = tk.Button(
            progress_window, text="Close", command=progress_window.destroy
        )
        close_button.pack(pady=10)

        # create package
        my_package = genanki.Package(deck)
        my_package.media_files = [
            f"{self.output_dir}{os.sep}audios{os.sep}tts_{i}.wav"
            for i in range(len(phrases) // 2 if self.is_pairs.get() else len(phrases))
        ]
        my_package.write_to_file(f"{self.output_dir}{os.sep}{self.anki_deck_name}.apkg")

        # delete audio files if keep_audio is not checked
        if not self.keep_audio.get():
            if not dir_exists:
                for file in os.listdir(f"{self.output_dir}{os.sep}audios"):
                    os.remove(f"{self.output_dir}{os.sep}audios{os.sep}{file}")
                os.rmdir(f"{self.output_dir}{os.sep}audios")
            else:
                for i in range(
                    len(phrases) // 2 if self.is_pairs.get() else len(phrases)
                ):
                    os.remove(f"{self.output_dir}{os.sep}audios{os.sep}tts_{i}.wav")


if __name__ == "__main__":
    app = App()
    app.mainloop()
