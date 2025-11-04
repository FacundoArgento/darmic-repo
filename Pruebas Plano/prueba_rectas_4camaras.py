import cv2
from dicom import Dicom
import numpy as np
import comandos_imagenes as ci
from skimage import color

# Lectura de Dicoms

filename = '/home/facundo/Documents/Unnoba/Investigaciónes Patológicas/Datasets - Dicoms/CasoA/SE0008 CINE_TF2D13_RETRO_4_CAMARAS/OUTIM0008.dcm'
dcm_1 = Dicom(filename)

filename2 = '/home/facundo/Documents/Unnoba/Investigaciónes Patológicas/Datasets - Dicoms/CasoA/SE0016 CINE_TF2D13_RETRO_EJE_CORTO/OUTIM0008.dcm'
dcm_2= Dicom(filename2)

filename3 = '/home/facundo/Documents/Unnoba/Investigaciónes Patológicas/Datasets - Dicoms/CasoA/SE0021 CINE_TF2D13_RETRO_EJE_CORTO/OUTIM0008.dcm'
dcm_3= Dicom(filename3)

# Sacamos una copia de las imagenes de cada dicom (las paso a rgb para graficar los puntos)

imagen1 = ci.leer_imagen_dicom(filename)
imagen1_copy = color.gray2rgb(imagen1.copy())

imagen2 = ci.leer_imagen_dicom(filename2)
imagen2_copy = color.gray2rgb(imagen2.copy())

imagen3 = ci.leer_imagen_dicom(filename3)
imagen3_copy = color.gray2rgb(imagen3.copy())

## WINDOWS

#cv2.namedWindow("ventana 1",cv2.WINDOW_NORMAL)
#cv2.namedWindow("ventana 2",cv2.WINDOW_NORMAL)
#cv2.namedWindow("ventana 3",cv2.WINDOW_NORMAL)

## Rectas interseccion con un dicom

dcm_1.graficar_rectas_interseccion_planos(dcm_2, imagen1_copy, imagen2_copy)
#dcm_1.graficar_rectas_interseccion_planos(dcm_3, imagen1_copy, imagen3_copy)

Fx, Fy = dcm_1.get_recta_interseccion_imagenes_Fx_Fy(dcm_2)
# imagen1_copy[np.where(imagen1 <= Fx(imagen1))] = 0

muestras = 300
extremo = 300

filas = dcm_1.get_filas()
columnas = dcm_1.get_columnas()
coordenada_inicial = dcm_1.coordenadas_pixel_en_espacio([0,0])
coordenada_extremo = dcm_1.coordenadas_pixel_en_espacio([filas,columnas])

az = coordenada_inicial[2]
bz = coordenada_extremo[2]

# rango_zi = np.linspace(-extremo,extremo, muestras)
rango_zi = np.linspace(az,bz, muestras)

Z1 = rango_zi[0]
Z2 = rango_zi[extremo-1]

X1 = Fx(Z1)
X2 = Fx(Z2)

Y1 = Fy(X1,Z1)
Y2 = Fy(X2,Z2)

coordenada_3d_1 = [X1,Y1,Z1]
coordenada_3d_2 = [X2,Y2,Z2]

print('Coordenadas espacio')
print(coordenada_3d_1, coordenada_3d_2)

# pixels dcm_1
pixel_11 = dcm_1.coordenadas_espacio_a_pixel(coordenada_3d_1)
pixel_12 = dcm_1.coordenadas_espacio_a_pixel(coordenada_3d_2)

# pixels
pixel_derecha1 = (pixel_11[0]+5, pixel_11[1])
pixel_derecha2 = (pixel_12[0]+5, pixel_12[1])

pixel_izquierda1 = (pixel_11[0]-5, pixel_11[1])
pixel_izquierda2 = (pixel_12[0]-5, pixel_12[1])

# Graficamos ambas rectas

colorLinea2 = (255,255,0) 
grosorLinea2 = 1  

imagen = cv2.line(imagen1_copy, pixel_derecha1, pixel_derecha2, colorLinea2, grosorLinea2)
cv2.line(imagen1_copy, pixel_izquierda1, pixel_izquierda2 , colorLinea2, grosorLinea2)

cv2.imshow("ventana 1", imagen1_copy)

cv2.waitKey(0)
cv2.destroyAllWindows()