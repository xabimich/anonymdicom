import pydicom as pm
import os
import pandas as pd
import shutil
from pathlib import Path
from anonymise import anonymise_dicom
import pandas as pd 

def get_accession_dict(file): 
    df = pd.read_csv(file)
    dict_accession = {}
    for index, row in df.iterrows():
        key = row['accessionnumber']
        value = row['id']
        dict_accession[key] = value
    return dict_accession
    

def change_folder_name(accessiondict, path):
    
    first_sub_folders='STU00000/SER00000/IMG00001'
    for root, dirs, files in os.walk(path):
        for name in dirs:
            folder_path = os.path.join(root, name)
            final_path = os.path.join(folder_path, first_sub_folders)
            ds = pm.dcmread(final_path)
            an = ds.AccessionNumber
            id = str(accessiondict[an])
            new_folder_path = os.path.join(root, id)
            os.rename(folder_path, new_folder_path)

            

def allimages_from_folder(directory, patient_start, patient_end):
    for patient_folder in range(patient_start, patient_end):
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






#Change dir to where you have all the folders of the patients"
dir= "TestData"
file = 'Datasets/id_accession.csv'
file2='Datasets/series_id.csv'
if __name__ == "__main__":
    accession_dict=get_accession_dict(file)
    change_folder_name(accession_dict, dir)
    patient_start=input("Introdueix el id del pacient inicial que vols anonimitzar= ")
    patient_end=input("Introdueix el id del pacient final que vols anonimitzar= ")
    allimages_from_folder(dir, patient_start, patient_end)