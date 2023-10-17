import sys
import tkinter as tk
from tkinter import filedialog
import os
import serial
from Tinyprog.__init__ import TinyProg,SerialPort

#ser = SerialPort("COM5")


def strict_query_user(question):
    valid = {"yes": True}

    prompt = " [yes/NO] > "

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        return valid.get(choice, False)

def check_if_overwrite_bootloader(addr, length, userdata_range):
    ustart = userdata_range[0]
    uend = userdata_range[1]

    if addr < ustart or addr + length >= uend:
        print("")
        print("    !!! WARNING !!!")
        print("")
        print("    The address given may overwrite the USB bootloader. Without the")
        print("    USB bootloader the board will no longer be able to be programmed")
        print("    over the USB interface. Without the USB bootloader, the board can")
        print("    only be programmed via the SPI flash interface on the bottom of")
        print("    the board")
        print("")
        retval = strict_query_user("    Are you sure you want to continue? Type in 'yes' to overwrite bootloader.")
        print("")
        return retval

    return True



def procesar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos binarios", "*.bin")])
    if archivo:
        # Realiza la acción que desees con el archivo binario seleccionado
        # Por ejemplo, puedes imprimir la ruta del archivo
        print("Archivo seleccionado:", archivo)
        #ser = SerialPort('COM5')
        ser=serial.Serial('COM5', timeout=1.0, writeTimeout=1.0).__enter__()

        tinyprog = TinyProg(ser)
        bitstream = tinyprog.slurp(archivo)
        addr = tinyprog.meta.userimage_addr_range()[0]
        print("    Programming at addr {:06x}".format(addr))
        if not tinyprog.program_bitstream(addr, bitstream):
            tinyprog.boot()
            tinyprog.program()
            sys.exit(1)


ventana = tk.Tk()
ventana.title("Program Loader")
# Configura el tamaño de la ventana
ventana.geometry("400x200")  # Ancho x Alto en píxeles

boton = tk.Button(ventana, text="Seleccionar archivo", command=procesar_archivo)
boton.pack()

ventana.mainloop()

