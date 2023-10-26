import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import serial
import serial.tools.list_ports
from Tinyprog.__init__ import TinyProg
import sys
import logging


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, str):
        self.text_widget.insert(tk.END, str)
        self.text_widget.see(tk.END)  # Desplaza automáticamente hacia la última línea
        self.text_widget.update()  # Forzar una actualización de la ventana

    def flush(self):
        pass  # Dejar flush vacío, ya que no es necesario

def redirigir_output(text_widget):
    sys.stdout = StdoutRedirector(text_widget)


#ser = SerialPort("COM5")

"""
def seleccionar_puerto():
    seleccion = combo.get()
    etiqueta.config(text=f"Puerto seleccionado: {seleccion}")
"""

def refrescar_puertos():
    puertos_serie = [port.device for port in serial.tools.list_ports.comports()]
    combo['values'] = puertos_serie
    if len(puertos_serie) > 0:
        combo.set(puertos_serie[0])
    else:
        combo.set("")

    logging.info("Puertos disponibles refrescados\n")

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
        puerto = combo.get()
        ser=serial.Serial(puerto, timeout=1.0, writeTimeout=1.0).__enter__()

        tinyprog = TinyProg(ser)
        bitstream = tinyprog.slurp(archivo)
        addr = tinyprog.meta.userimage_addr_range()[0]
        print("    Programming at addr 0x{:06x}".format(addr))
        if not tinyprog.program_bitstream(addr, bitstream):
            print("Failed to program... exiting")
            text_widget.insert(tk.END, "\nFallo al programar\n")
            #sys.exit(1)
        else:
            tinyprog.boot()
            text_widget.insert(tk.END, "\nProgramado correctamente\n")
            #sys.exit(0)


ventana = tk.Tk()
ventana.title("Program Loader")
# Configura el tamaño de la ventana
ventana.geometry("400x600")  # Ancho x Alto en píxeles
# Obtener la lista de puertos serie disponibles
puertos_serie = [port.device for port in serial.tools.list_ports.comports()]

# Crear una variable para almacenar la selección
combo = ttk.Combobox(ventana, values=puertos_serie)

combo.pack(pady=10)

# Botón para mostrar la selección
boton = tk.Button(ventana, text="Recargar", command=refrescar_puertos)
boton.pack()

etiqueta = tk.Label(ventana, text="")
etiqueta.pack(pady=10)

#Boton de carga archivo
boton = tk.Button(ventana, text="Seleccionar archivo", command=procesar_archivo)
boton.pack()


text_widget = tk.Text(ventana, wrap=tk.WORD)
text_widget.pack()

redirigir_output(text_widget)

refrescar_puertos()



ventana.mainloop()

