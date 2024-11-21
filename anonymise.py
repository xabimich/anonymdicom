import pydicom as pm

import os

file_path = 'dicom/93/img_50.dcm'
output_path = r'C:\Users\41545527Y\Documents\DICOMDb\DICOM\PAT00000\STU00000\SER00000'


def anonymise_dicom(dicom_path, output_path, anonymised_name): 
    dicom_file = pm.dcmread(dicom_path)
    dicom_file.PatientName = anonymised_name
    dicom_file.PatientID = anonymised_name
    dicom_file.PatientSex = ''
    dicom_file.PatientBirthDate=''
    dicom_file.AccessionNumber=''
    output = output_path
    dicom_file.save_as(output)



if __name__ == '__main__': 
    dicom_file = pm.dcmread(file_path)
    for element in dicom_file: 
        print(element)
    #anonymise_dicom(dicom_path, output_path, '')