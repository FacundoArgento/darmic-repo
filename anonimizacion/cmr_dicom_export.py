"""
File: dicom_to_nrrd.py
Author: Ariel Hernán Curiale
Email: curiale@gmail.com
Github: https://gitlab.com/Curiale
Description:
    This script read cine SA dicom studies and save them as 3D nrrd images
"""
#Para ejecutarlo por lìnea de comandos se debe correr:
#cmr_dicom_export.py -d  -o  -sid 1
import os
import argparse
import SimpleITK as sitk
from pathlib import Path
from cmr_dicom_all import AllReader
from pydicom import dcmread
import glob
from conexionDarmic import addNRRDtoStudyInDarmic
import re

def extract_study_name(path):
    parts = path.split('/')
    for part in parts:
        if part.count('-') >= 5 and re.search(r'_\d{2}:?\d{2}:?\d{2}$', part):
            return part
    return None

def main(dicom_data, output_folder, file_format, study_id, archivo):
    # NUEVO: Manejo de errores básicos por si la carpeta está vacía o es inválida
    try:
        study_name = extract_study_name(dicom_data)
        if study_name is None:
            print(f"No se pudo extraer el nombre del estudio de la ruta: {dicom_data}",file=archivo)
            return
        reader = AllReader(dicom_data, study_id, use_dicom_id=False)
        reader.execute()
        I = reader.get_array()
    except Exception as e:
        print(f"Error al leer la carpeta DICOM: {dicom_data}. Detalle: {e}",file=archivo)
        return # No continuar si no se pudo leer

    time = reader.time
    origin = reader.origin
    spacing = reader.spacing

    save_path = Path(output_folder)
    save_path.mkdir(parents=True, exist_ok=True)

    # --- NUEVO: Verificación de archivos existentes ---
    # Primero, construimos la lista de nombres de archivo esperados
    expected_files = []
    for i in range(len(time)):
        #UNNOBA: Se agrega la SerieDescription al nombre del archivo
        fname = f"{reader.seriesDescription}_{reader.patientID}_{i:02d}.{file_format}"
        expected_files.append(os.path.join(output_folder, fname))

    print(f"Procesando: '{dicom_data}' (ID: {reader.patientID})...",file=archivo)
    for i, t in enumerate(time):
        # We are not using the time right now but if we want to identify
        # ED and ES we should use it
        sp = spacing[i].mean(axis=0)
        orig = origin[i, 0]
        I_i = I[i]

        img = sitk.GetImageFromArray(I_i)
        img.SetOrigin(tuple(orig))
        img.SetSpacing(tuple(sp))

        # Usamos el nombre de archivo que ya generamos en la verificación
        fname = expected_files[i] 
        sitk.WriteImage(img, fname, True)
        print(f"Archivo procesado: {fname}",file=archivo)
    
    # --- AGREGAMOS EL patientID en la base de DARMIC
    try:
        addNRRDtoStudyInDarmic(study_name=study_name, nrrd_string=reader.patientID)
    except Exception as e:
        print(f"Error al agregar NRRD ID a Darmic para el estudio '{study_name}': {e}",file=archivo)
        return

    print(f"Completado: {dicom_data} .",file=archivo)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dicom_data", help="Study folder", type=str)
    parser.add_argument(
        "-o", "--output_folder", help="Output folder", type=str, default=""
    )
    parser.add_argument(
        "-sid", "--study_id", help="Study ID", type=str, default=""
    )
    parser.add_argument(
        "-ff", "--file_format", help="Output format", type=str, default="nrrd"
    )
    args = parser.parse_args()
    
    # Permitir que el argumento -d funcione, o usar el valor hardcodeado si -d no se usa
    if args.dicom_data:
        dicom_data = args.dicom_data
    else:
        dicom_data = "./test_files/studys"

    output_folder_base = (
        dicom_data if len(args.output_folder) == 0 else args.output_folder
    )
    
    # Usar la ruta hardcodeada si no se proveyó -o
    if not args.output_folder:
        output_folder_base = "./test_files/results"
    
    
    folder = dicom_data
    recursive_path = os.path.join(folder, "**")

    # --- NUEVO: Usar un set para guardar carpetas únicas ---
    folders_to_process = set()

    with open('archivo_salida.txt', 'w') as archivo:
        print(f"Buscando archivos .dcm recursivamente en: {folder}...",file=archivo)
        for file in glob.iglob(recursive_path, recursive=True):     
            if "is_dicom_file" not in locals():
                try:
                    def is_dicom_file(path):
                        try:
                            dcmread(path, stop_before_pixels=True, force=False)
                            return True
                        except Exception:
                            return False
                except Exception:
                    def is_dicom_file(path):
                        try:
                            with open(path, "rb") as f:
                                f.seek(128)
                                return f.read(4) == b"DICM"
                        except Exception:
                            return False

            if not os.path.isfile(file) or not is_dicom_file(file):
                continue
            # Obtener la carpeta contenedora
            folder_name, nombre_archivo = os.path.split(file)
            print(f"****** Encontró archivo: {nombre_archivo} en carpeta {folder}",file=archivo)

            # Añadir la carpeta al set (los duplicados se ignoran automáticamente)
            folders_to_process.add(folder_name)
    
        if not folders_to_process:
            print("No se encontraron carpetas con archivos .dcm.",file=archivo)
        else:
            print(f"Se encontraron {len(folders_to_process)} carpetas únicas para procesar.",file=archivo)

        # --- NUEVO: Iterar sobre las carpetas ÚNICAS ---
        for unique_folder in folders_to_process:
            try:
                # Llamar a main UNA SOLA VEZ por carpeta encontrada
                main(unique_folder, output_folder_base, args.file_format, args.study_id,archivo)
            except Exception as e:
                print(f"ERROR inesperado al procesar la carpeta {unique_folder}: {e}",file=archivo)

        print("Proceso finalizado.",file=archivo)