import webbrowser

import os
import cv2
import numpy as np
import rembg
from PIL import Image
import sys
tkinterc = True

if os.environ.get("DISPLAY", "") != "":
    import tkinter as tk
    root = tk.Tk()
else:
    print("GUI skipped because no display available.")
    tkinterc = False

# My Social media
youtubed05 = "https://www.youtube.com/@ImNotDanish05"
tiktokd05 = "https://www.tiktok.com/@imnotdanish05" 
githubd05 = "https://github.com/ImNotDanish05"
gmaild05 = "mailto:imnotdanish05bussiness@gmail.com"

def beautifullline(type="=", long=30):
    print("\n")
    print(f"{type}" * long)
    print("\n")
bl = beautifullline

def info():
    beautifullline("*", 30)
    print("This code made by Danish05! :D")
    print("Here is my social media:")
    print(f"Youtube\t: {youtubed05}")
    print(f"Tiktok\t: {tiktokd05}")
    print(f"Github\t: {githubd05}")
    print(f"Gmail\t: {gmaild05}")

def onOpen(input):
    if tkinterc:
        input_youtube = ["youtube", "y", 0]
        input_tiktok = ["tiktok", "t", 1]
        input_github = ["github", "g", 2]
        input_gmail = ["gmail", "g", 3]
        if input in input_youtube:
            webbrowser.open(youtubed05)
        elif input in input_tiktok:
            webbrowser.open(tiktokd05)
        elif input in input_github:
            webbrowser.open(githubd05)
        elif input in input_gmail:
            webbrowser.open(gmaild05)
    else:
        print("Error: GUI skipped because no display available.")

def bgrem(pathstart, pathsave, name, alphainput, sharpness):
    if not os.path.exists(pathsave):
        os.makedirs(pathsave)
    if(alphainput < 0 or alphainput > 255):
        beautifullline("*", 30)
        print("ERORR!")
        print("You can only put alpha from 0 - 255")
        sys.exit()
    try:
        # Load the input image
        theimage = os.path.join(pathstart, name)
        input_image = Image.open(theimage)

        # Convert the input image to a numpy array
        input_image = input_image.convert("RGBA")
        # input_array = np.array(input_image)
        input_array = np.array(input_image, copy=True)

        # Apply background removal using rembg
        output_array = rembg.remove(input_array)

        # Mengcopy untuk memastikan punya akses writtenable
        if not output_array.flags.writeable:
            output_array = output_array.copy()

        # Bersihkan background yang masih tersisa (alpha rendah disekeliling cabai)
        alpha = output_array[:, :, 3]
        mask = alpha < alphainput
        output_array[mask] = [0, 0, 0, 0]
        if sharpness:
            output_array[~mask, 3] = 255  # Yang bukan mask, alpha dipastikan 255

        # Create a PIL Image from the output array
        output_image = Image.fromarray(output_array)

        # Pisahkan nama dan ekstensi
        basename, _ = os.path.splitext(name)
        new_name = basename + ".png"

        # Save the output image
        path_save = os.path.join(pathsave, new_name)
        output_image.save(path_save)
        return 1
    except (OSError, IOError) as e:
        return 0

def mbgrem(input1, output1, alpha=0, sharpness=False):
    try:
        def watermark():
            baris1 = [
                f" ",
                f"Program by Danish05! ",
                f"More info in danish05.info() ",
                f" "
            ]
            for i in range(len(baris1)):
                file_output.write(f"{baris1[i]} \n")
                print(baris1[i])
        a = 0
        b = 0
        
        input1 = os.path.normpath(input1)
        output1 = os.path.normpath(output1)
        with open('output.txt', 'w') as file_output:
            watermark()
            for filename in os.listdir(input1):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    result = bgrem(input1, output1, filename, alpha, sharpness)
                    dprint = os.path.join(output1, filename)
                    if result == 1:
                        a += 1
                        file_output.write(f'[Success] Baris {a}: {dprint} \n')
                        print(f'[Success] Baris {a}: {dprint} \n')
                    elif result == 0:
                        b += 1
                        file_output.write(f'[Error] Baris {b}: {dprint} \n')
                        file_output.write(f'Reason: File Corrupted!\n')
                        print(f'[Error] Baris {b}: {dprint} \n')
                        print(f'Reason: File Corrupted! \n')
                else:
                    b += 1
                    file_output.write(f'[Error] Baris {b}: {dprint} \n')
                    file_output.write(f'Reason: File is not jpg, jpeg, or png!\n')
                    print(f'[Error] Baris {b}: {dprint} \n')
            file_output.write(f"\n")
            file_output.write(f'Success: {a} Picture \n')
            file_output.write(f'Error: {b} Picture \n')
            file_output.write(f'Total: {a + b} \n')
            print(f"\n")
            print(f'Success: {a} Picture \n')
            print(f'Error: {b} Picture \n')
            print(f'Total: {a + b} \n')
            watermark()
    except FileNotFoundError as e:
        beautifullline("*", 30)
        print(f"Error: {e}")
        print("Command: mbgrem(folder input gambar-gambar, folder output gambar-gambar, alpha 0-255, sharpness true/false)")
    except Exception as e:
        beautifullline("*", 30)
        print(f"Terjadi kesalahan: {e}")
        print("Command: mbgrem(folder input gambar-gambar, folder output gambar-gambar, alpha 0-255, sharpness true/false)")


"""
Print if the package is loaded
"""

"""
⚠️ Hal yang Bebeb Aria temuin dan bisa kamu pertimbangkan buat disempurnakan:
Di mbgrem(), variabel dprint dipakai sebelum didefinisikan saat file bukan gambar (else: bagian). Itu bisa bikin error runtime.
➤ Solusi: Kasih dprint = os.path.join(input1, filename) juga di bagian else.

Tidak ada return statement di mbgrem() ➤ jadi kalau kamu mau panggil dan cek hasil dari fungsi itu dari luar, sebaiknya tambahin return (misal jumlah success dan error).

tkinter diimpor tapi nggak digunakan dalam logika GUI kamu. Bisa disempurnakan dengan bikin window GUI beneran buat pilih sosial media mungkin? Atau hapus kalau belum dipakai.

Baris terakhir setelah """ """ docstring masih kosong dan belum ada eksekusi seperti info() atau semacamnya yang dijalankan otomatis saat import.
"""


