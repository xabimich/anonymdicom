import pydicom as pm
import os
import pandas as pd
import shutil
from pathlib import Path
from anonymise import anonymise_dicom
import tkinter as tk
from tkinter import filedialog,ttk, messagebox
import threading

def get_accession_dict(file): 
    df = pd.read_excel(file)
    dict_accession = {}
    for index, row in df.iterrows():
        key = row['accessionnumber']
        value = row['id']
        dict_accession[str(key)] = str(value)
    return dict_accession
    

def change_folder_name(accessiondict, path):
    
    first_sub_folders='STU00000/SER00000/IMG00001'
    for root, dirs, files in os.walk(path):
        for name in dirs:
            folder_path = os.path.join(root, name)
            final_path = os.path.join(folder_path, first_sub_folders)
            try:
                ds = pm.dcmread(final_path)
                an = ds.AccessionNumber
                if an in accessiondict:
                    id = str(accessiondict[an])
                    new_folder_path = os.path.join(root, id)
                    os.rename(folder_path, new_folder_path)
                else:
                    # Show error message if AccessionNumber not found in dictionary
                    messagebox.showerror("Accession Number Not Found", f"Accession Number {an} not found in the provided dictionary. Skipping folder: {folder_path}")
                    continue  # Skip to next iteration of the loop
            except Exception as e:
                # Handle any errors with reading the DICOM file
                messagebox.showerror("Error", f"Error processing {folder_path}: {e}")
                break


            

def allimages_from_folder(directory, patient_folder):
    patient_folder_name = str(patient_folder)
    patient_directory = os.path.join(directory, patient_folder_name)
    patient_directory = Path(patient_directory)
    if patient_directory.exists():
        img_number = 1  
        for subdir, _, files in os.walk(patient_directory):
            if subdir == patient_directory:
                continue
            for file in files:
                if not file.startswith('thumbnail'):
                    new_filename = f'img_{img_number}{os.path.splitext(file)[1]}.dcm'
                    source_path = os.path.join(subdir, file)
                    output_path = os.path.join(subdir,new_filename)
                    anonymise_dicom(source_path,output_path,patient_folder_name)
                    destination_path = os.path.join(patient_directory, new_filename)
                    shutil.move(output_path, destination_path)
                    img_number += 1
        subfolders = [subfolder for subfolder in os.listdir(patient_directory) if os.path.isdir(os.path.join(patient_directory, subfolder))]
        if len(subfolders) == 1:
            shutil.rmtree(os.path.join(patient_directory, subfolders[0]))

def process_directory(directory, file, number1, number2, progress_callback):
    accession_dict = get_accession_dict(file)
    change_folder_name(accession_dict, directory)

    total_items = number2 - number1 + 1
    for count, patient_folder in enumerate(range(number1, number2 + 1), start=1):
        allimages_from_folder(directory, patient_folder)
        progress = int((count / total_items) * 100)
        progress_callback(progress, patient_folder)
         


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Anonimitzador de DICOM by X. Michelena")

        self.directory = None
        self.info_file = None
        self.number1 = None
        self.number2 = None

        self.create_widgets()

    def create_widgets(self):
    
        self.select_dir_label = tk.Label(self.root, text="Selecciona la carpeta amb tots els pacients (si utilitzes Starviewer és la carpeta DICOM)")
        self.select_dir_label.pack(pady=5)

        self.select_dir_button = tk.Button(self.root, text="Selecciona carpeta", command=self.select_directory)
        self.select_dir_button.pack(pady=5)

        self.dir_display = tk.Label(self.root, text="Cap directori seleccionat", fg="gray")
        self.dir_display.pack(pady=5)

        self.select_file_label = tk.Label(self.root, text="Selecciona l'excel amb la relació id-accession number. Utilitza format arxiu de prova")
        self.select_file_label.pack(pady=5)
        self.select_file_label.pack_forget()

        self.select_file_button = tk.Button(self.root, text="Selecciona excel", command=self.select_file)
        self.select_file_button.pack(pady=5)
        self.select_file_button.pack_forget()

        self.file_display = tk.Label(self.root, text="Cap excel seleccionat", fg="gray")
        self.file_display.pack(pady=5)
        self.file_display.pack_forget()

        # Step 2: Ask for first number
        self.num1_label = tk.Label(self.root, text="Entra el id del primer pacient que vols anonimitzar")
        self.num1_label.pack(pady=5)
        self.num1_label.pack_forget()

        self.num1_entry = tk.Entry(self.root)
        self.num1_entry.pack(pady=5)
        self.num1_entry.pack_forget()

        self.num1_button = tk.Button(self.root, text="Següent", command=self.enter_number1)
        self.num1_button.pack(pady=5)
        self.num1_button.pack_forget()

        # Step 3: Ask for second number
        self.num2_label = tk.Label(self.root, text="Entra el id del últim pacient que vols anonimitzar")
        self.num2_label.pack(pady=5)
        self.num2_label.pack_forget()

        self.num2_entry = tk.Entry(self.root)
        self.num2_entry.pack(pady=5)
        self.num2_entry.pack_forget()

        self.num2_button = tk.Button(self.root, text="Començar procés", command=self.start_process)
        self.num2_button.pack(pady=5)
        self.num2_button.pack_forget()

        # Progress Bar
        self.progress_label = tk.Label(self.root, text="Progrés:")
        self.progress_label.pack(pady=5)
        self.progress_label.pack_forget()

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(pady=5)
        self.progress_bar.pack_forget()

        # Current ID being processed
        self.current_id_label = tk.Label(self.root, text="Reconfigurant les carpetes...")
        self.current_id_label.pack(pady=5)
        self.current_id_label.pack_forget()


    def select_directory(self):
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.dir_display.config(text=f"Directori seleccionat: {self.directory}", fg="black")

            # Show step 1.5
            self.select_file_label.pack()
            self.select_file_button.pack()
            self.file_display.pack()

    def select_file(self):
        self.info_file = filedialog.askopenfilename()
        if self.info_file:
            self.file_display.config(text=f"Excel seleccionat: {self.info_file}", fg="black")

            # Show step 2
            self.num1_label.pack()
            self.num1_entry.pack()
            self.num1_button.pack()

    def enter_number1(self):
        try:
            self.number1 = int(self.num1_entry.get())
            self.num1_label.pack_forget()
            self.num1_entry.pack_forget()
            self.num1_button.pack_forget()

            # Show step 3
            self.num2_label.pack()
            self.num2_entry.pack()
            self.num2_button.pack()
        except ValueError:
            self.num1_label.config(text="No és un nombre vàlid", fg="red")

    def start_process(self):
        try:
            self.number2 = int(self.num2_entry.get())
            self.num2_label.pack_forget()
            self.num2_entry.pack_forget()
            self.num2_button.pack_forget()

            # Show progress bar
            self.progress_label.pack()
            self.progress_bar.pack()
            self.progress_bar['value'] = 0

            self.current_id_label.pack()
            self.current_id_label.config(text="Processant les carpetes...")

            # Start the processing in a separate thread
            thread = threading.Thread(target=self.run_process)
            thread.start()
        except ValueError:
            self.num2_label.config(text="Si us plau, posa un nombre vàlid", fg="red")

    def run_process(self):
        def update_progress(progress, current_id):
            self.progress_bar['value'] = progress
            self.current_id_label.config(text=f"Processant imatges del ID: {current_id}")
            self.root.update_idletasks()

        try:
            process_directory(self.directory, self.info_file, self.number1, self.number2, update_progress)

            # When done
            self.progress_label.config(text="Procés complet!", fg="green")
            self.current_id_label.config(text="Procés complet!")
        except Exception as e:
            # Catch and show the error in a messagebox
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.progress_label.config(text="El procés ha fallat. Torna a començar", fg="red")


        # When done
        self.progress_label.config(text="Procés complet!", fg="green")



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
