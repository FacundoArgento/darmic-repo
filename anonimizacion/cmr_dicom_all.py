"""
File: myDicomReader.py
Author: Ariel Hernán Curiale
Email: curiale@gmail.com
GitLab: https://gitlab.com/Curiale
Description:
    This class make use of pydicom for reading dicomfiles. SimpleITK is not
    working and I need to order the images. It is better to do all the work by
    using pydicom instead
"""

import pydicom
import os
import numpy as np
from natsort import natsorted


class AllReader:
    def __init__(
        self, dicom_folder: str, study_id: str = "", use_dicom_id: bool = True
    ):
        self.dicom_folder = dicom_folder
        self.origin = None
        self.spacing = None
        self.time = None
        self.instance = None
        #UNNOBA: Tag Agregados
        self.ImageOrientationPatient = None
        self.SliceThickness = None
        self.SliceLocation = None
        self.TriggerSourceOrType = None
        self.NominalInterval = None
        self.FrameTime = None
        self.NominalInterval = None
        self.TemporalPositionIndex = None
        self.DimensionIndexValues = None
        self.NumberOfFrames = None
        self.ScanningSequence = None
        self.SequenceVariant = None
        self.ScanOptions = None
        self.MRAcquisitionType = None
        self.EchoTime = None
        self.RepetitionTime = None
        self.InversionTime = None
        self.AcquisitionMatrix = None

        self._I = None
        self.patientID = (
            "".join(map(str, np.random.randint(0, 1000, size=5)))
            if study_id == ""
            else study_id
        )
        self.use_dicom_id = use_dicom_id
        self.seriesDescription = None
        self.seriesNumber = "0"

        dicom_files = [
            f
            for f in os.listdir(dicom_folder)
            if os.path.isfile(os.path.join(dicom_folder, f))
            and f.lower().endswith(".dcm")
        ]

        dicom_files = natsorted(dicom_files)
        nfiles = len(dicom_files)
        self.dicom_files = dicom_files
        self.nfiles = nfiles

    def get_array(self):
        return self._I

        
    def execute(self):
        dicom_files = self.dicom_files
        dicom_folder = self.dicom_folder
        nfiles = self.nfiles

        ds = []
        I = []
        origin = []
        spacing = []
        time = []
        instance = []
        ImageOrientationPatient = []
        SliceThickness = []
        SliceLocation = []
        TriggerSourceOrType = []
        NominalInterval = []
        FrameTime = []
        NominalInterval = []
        TemporalPositionIndex = []
        DimensionIndexValues = []
        NumberOfFrames = []
        ScanningSequence = []
        SequenceVariant = []
        ScanOptions = []
        MRAcquisitionType = []
        EchoTime = []
        RepetitionTime = []
        InversionTime = []
        AcquisitionMatrix = []

        z = None
        t = 0

        for f in dicom_files:          
                #UNNOBA:
                ds_i = pydicom.dcmread(os.path.join(dicom_folder, f))

                IPP = True
                PS = True
                TT = True
                IN = True
    
                #Tags para registración y medición de volumen en RM
                if 'ImagePositionPatient' in ds_i:
                    origin.append(ds_i.ImagePositionPatient)
                else: IPP = False
            
                if 'PixelSpacing' in ds_i:
                    spacing.append(ds_i.PixelSpacing)
                else: PS = False
            
                if 'TriggerTime' in ds_i:
                    time.append(ds_i.TriggerTime)
                else: TT = False

                if 'InstanceNumber' in ds_i:
                    instance.append(ds_i.InstanceNumber)
                else: IN = False

                if 'ImageOrientationPatient' in ds_i:
                    ImageOrientationPatient.append(ds_i.ImageOrientationPatient)

                if 'SliceThickness' in ds_i:
                    SliceThickness.append(ds_i.SliceThickness)

                if 'SliceLocation' in ds_i:
                    SliceLocation.append(ds_i.SliceLocation)

                #Tags para instancias de tiempo en cineresonancia cardíaca
                if 'TriggerSourceOrType' in ds_i:
                    TriggerSourceOrType.append(ds_i.TriggerSourceOrType)
                
                if 'NominalInterval' in ds_i:
                    NominalInterval.append(ds_i.NominalInterval)
                
                if 'FrameTime' in ds_i:
                    FrameTime.append(ds_i.FrameTime)
      
                if 'NominalInterval' in ds_i:
                    NominalInterval.append(ds_i.NominalInterval)

                if 'TemporalPositionIndex' in ds_i:
                    TemporalPositionIndex.append(ds_i.TemporalPositionIndex)

                if 'DimensionIndexValues' in ds_i:
                    DimensionIndexValues.append(ds_i.DimensionIndexValues)

                if 'NumberOfFrames' in ds_i:
                    NumberOfFrames.append(ds_i.NumberOfFrames)

                #Tags para identificar el tipo de secuencia de RM
                if 'ScanningSequence' in ds_i:
                    ScanningSequence.append(ds_i.ScanningSequence)

                if 'SequenceVariant' in ds_i:
                    SequenceVariant.append(ds_i.SequenceVariant)

                if 'ScanOptions' in ds_i:
                    ScanOptions.append(ds_i.ScanOptions)

                if 'MRAcquisitionType' in ds_i:
                    MRAcquisitionType.append(ds_i.MRAcquisitionType)

                if 'EchoTime' in ds_i:
                    EchoTime.append(ds_i.EchoTime)

                if 'RepetitionTime' in ds_i:
                    RepetitionTime.append(ds_i.RepetitionTime)

                if 'InversionTime' in ds_i:
                    InversionTime.append(ds_i.InversionTime)

                if 'AcquisitionMatrix' in ds_i:
                    AcquisitionMatrix.append(ds_i.AcquisitionMatrix)

                if (IPP and PS and TT and IN):
                    ds.append(ds_i)
                
                if z is None:
                    z = origin[-1][0]

                z_i = origin[-1][0]
                if z == z_i:
                    t += 1

        origin = np.array(origin)
        spacing = np.array(spacing)
        time = np.array(time)
        instance = np.array(instance)

        nslice = int(nfiles / t)
        dim = ds[0].pixel_array.shape

        dim = (nslice,) + dim

        self.dim = dim[::-1]  # `[x,y,z]

        I = np.zeros((t,) + dim, dtype=np.uint16)

        # Ordenamos por InstanceNumber
        idi = np.argsort(instance)
        origin = origin[idi, :]
        spacing = spacing[idi, :]
        time = time[idi]
        instance = instance[idi]
        dfiles = []

        if t == 1:
                for j in range(nslice):
                    idk = idi[j]
                    I[0, j, ...] = ds[idk].pixel_array
                    dfiles.append(os.path.join(dicom_folder, dicom_files[idk]))
        else:
                for i in range(t):
                    for j in range(nslice):
                        k = i + j * t
                        idk = idi[k]
                        I[i, j, ...] = ds[idk].pixel_array
                        dfiles.append(os.path.join(dicom_folder, dicom_files[idk]))

        spz = float(ds_i.SpacingBetweenSlices)
        #UNNOBA:  A spz sumar el thinkness
        spacing = np.column_stack((spacing, np.repeat(spz, nfiles)))

        origin.shape = (nslice, t, 3)
        spacing.shape = (nslice, t, 3)
        time.shape = (nslice, t)

        # (time, slice, ....)
        origin = origin.transpose((1, 0, 2))
        spacing = spacing.transpose((1, 0, 2))
        time = time.T

        self.origin = origin
        self.spacing = spacing
        self.time = time
        self._I = I
        if self.use_dicom_id:
                self.patientID = ds[0].PatientID
        self.seriesDescription = ds[0].SeriesDescription
        self.seriesNumber = ds[0].SeriesNumber

        self.dicom_files = dfiles
        self.instance = instance
