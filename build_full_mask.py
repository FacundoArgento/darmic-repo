import os
import numpy as np
from PIL import Image
from tqdm import tqdm
from glob import iglob
from pathlib import Path
import matplotlib.pyplot as plt


m2bool = lambda m : np.array(m, dtype=np.bool_)

bool2m = lambda m : m.astype(np.uint8)


def build(lv_mask=None, m_mask=None, rv_mask=None, 
          lv_color=85, m_color=170, rv_color=255):
  
    if (lv_mask is not None) or (m_mask is not None) or (rv_mask is not None):
        
        lv = 0 if (lv_mask is None) else bool2m(m2bool(lv_mask) * lv_color)

        m = 0 if (m_mask is None) else \
            bool2m((m2bool(lv_mask) ^ m2bool(m_mask)) * m_color) \
            if (lv_mask is not None) else \
                bool2m(m2bool(m_mask) * m_color)
        
        rv = 0 if (rv_mask is None) else \
            bool2m((m2bool(rv_mask) ^ (m2bool(m_mask) & m2bool(rv_mask))) * rv_color) \
            if (m_mask is not None) else \
                bool2m(m2bool(rv_mask) * rv_color)

        # region Debug
        # plt.imshow(lv, cmap='gray')
        # plt.show()
        # print(f'LV unique values: {np.unique(lv)}')
        # plt.imshow(m, cmap='gray')
        # plt.show()
        # print(f'M unique values: {np.unique(m)}')
        # plt.imshow(rv, cmap='gray')
        # plt.show()
        # print(f'RV unique values: {np.unique(rv)}')
        
        # i = Image.fromarray((lv + m) + rv)
        # plt.imshow(np.array(i), cmap='gray')
        # plt.show()
        # print(f'Final mask unique values: {np.unique(np.array(i))}')
        # endregion Debug

        return Image.fromarray(lv + m + rv)
    else: return None

if __name__ == '__main__':

    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Parse .xls notations file from segment software to binary mask.')
    parser.add_argument("--root_directory", 
                        required=False, 
                        default='/home/facundo/Documents/unnoba/investicaciones_patologicas/Mascaras/masks_2112024/caso2',
                        help='Root directory where the data are stored.')
    parser.add_argument('--mask_name', required=False, type=str, default='new mask.png',
                        help='Use this name if original image are not presented.')
    parser.add_argument('--lv_color', required=False, type=int, default=85,
                        help='Color for paint the LV strcture.')
    parser.add_argument('--m_color', required=False, type=int, default=170,
                        help='Color for paint the M strcture.')
    parser.add_argument('--rv_color', required=False, type=int, default=255,
                        help='Color for paint the RV strcture.')
   
    args = parser.parse_args()

    search_path = os.path.join(args.root_directory, '**/*')
    files_paths = [f for f in iglob(search_path, recursive=True) if os.path.isfile(f)]
    files_paths.append(os.path.join('This', 'Fake', 'Dir', 'Allow Us', 'Save', 'The', 'Last', 'Mask'))

    # n: file_name - p: path_to_image - c: cavity_type - m: mask
    read_image = lambda n, p, c, m : Image.open(p) if (c in n) else m
    
    prev_folder_directory = None
    for file_path in tqdm(files_paths, total=len(files_paths)):
        folder_directory = str(Path(file_path).parent)
        file_name = file_path.split(os.sep)[-1].upper()

        if (prev_folder_directory != folder_directory):
            if (prev_folder_directory is not None):
                mask_path = os.path.join(prev_folder_directory, mask_name)
                full_mask = build(lv_mask, m_mask, rv_mask, 
                            args.lv_color, args.m_color, args.rv_color)

                if (full_mask is not None): full_mask.save(mask_path, 'png')
            
            lv_mask = None; m_mask = None; rv_mask = None
            mask_name = args.mask_name

        if (files_paths.index(file_path) != (len(files_paths) - 1)):
            mask_name = file_name.replace('I', 'FM') if ('I' in file_name) and ('LVEPI' not in file_name) else mask_name
            lv_mask = read_image(file_name, file_path,  'LVENDO', lv_mask)
            m_mask  = read_image(file_name, file_path, 'LVEPI',  m_mask)
            rv_mask = read_image(file_name, file_path, 'RVENDO', rv_mask)
            
            prev_folder_directory = folder_directory
    