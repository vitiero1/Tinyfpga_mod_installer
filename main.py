import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import PhotoImage
import os
import serial
import serial.tools.list_ports
from Tinyprog.__init__ import TinyProg
import sys
import logging
import subprocess
import glob
import shutil
from time import sleep
import recursos

directorio = None


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

# Refresca los puertos COM del PC
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


"""
def procesar_archivo():

    files = glob.glob(directorio + '/*.v')
    if len(files) > 0:
        subprocess.Popen("apio verify", cwd=directorio)
        sleep(2)
        subprocess.Popen("apio build", cwd=directorio)
        sleep(2)
        archivo = directorio + "/hardware.bin"
        if os.path.exists(archivo):
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
        else:
            print("No existen *.v en el directorio")
"""
# Seleccion de directorio, crea .init y .pcf
def sel_folder():
    global directorio
    directorio = filedialog.askdirectory()
    subprocess.Popen("apio init --board TinyFPGA-BX -y", cwd=directorio)
    #shutil.copyfile('./Resources/pins.pcf', directorio + '/pins.pcf')
    with open(directorio + "/pins.pcf", 'w') as f:
        f.write(recursos.pins_pcf)

# Comprueba si existe *.v  lanza apio verify
def verify():
    text_widget.delete('1.0',tk.END)
    files = glob.glob(directorio + '/*.v')
    if len(files) > 0:
        subprocess.Popen("apio verify", cwd=directorio)
        sleep(2)
    else:
        print("No existen *.v en el directorio")
        print("Crea tu archivo verilog")


def build():
    files = glob.glob(directorio + '/*.v')
    if len(files) > 0:
        p=subprocess.Popen("apio build", cwd=directorio)
        p.wait()
        sleep(2)
        archivo = directorio + "/hardware.bin"
        if os.path.exists(archivo):
            # Realiza la acción que desees con el archivo binario seleccionado
            # Por ejemplo, puedes imprimir la ruta del archivo
            print("Archivo seleccionado:", archivo)

            # ser = SerialPort('COM5')
            puerto = combo.get()
            ser = serial.Serial(puerto, timeout=1.0, writeTimeout=1.0).__enter__()

            tinyprog = TinyProg(ser)
            bitstream = tinyprog.slurp(archivo)
            addr = tinyprog.meta.userimage_addr_range()[0]
            print("    Programming at addr 0x{:06x}".format(addr))
            if not tinyprog.program_bitstream(addr, bitstream):
                print("Failed to program... exiting")
                text_widget.insert(tk.END, "\nFallo al programar\n")
                # sys.exit(1)
            else:
                tinyprog.boot()
                text_widget.insert(tk.END, "\nProgramado correctamente\n")
                # sys.exit(0)

# Funcion que se encarga de guardar el path de las imagenes
def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

""" Compilar .exe con el comando pyinstaller --onefile --add-data "Resources;Resources" main.py"""

ventana = tk.Tk()
ventana.title("TinyFPGA Program Loader")
# Configura la ventana
ventana.geometry("400x400")  # Ancho x Alto en píxeles
ventana.resizable(False,False) #Fija la ventana
color="#23343c" #color fondo de los frames


#Datos de icono
icon_path = resource_path(os.path.join("Resources","icon.ico"))
ventana.iconbitmap(icon_path)


# Background ventana
img_bg= PhotoImage(file=resource_path(os.path.join("Resources","tinyfpga_logo.png")))
img_width = img_bg.width()
img_height = img_bg.height()

x_position = (400 - img_width) // 2
y_position = (400 - img_height) // 2

canvas_bg = tk.Canvas(ventana, width=400, height=400)
canvas_bg.pack()

canvas_bg.create_image(x_position, y_position, anchor=tk.NW, image=img_bg)

# Obtener la lista de puertos serie disponibles
puertos_serie = [port.device for port in serial.tools.list_ports.comports()]


frame_top = tk.Frame(ventana, bg=color)
frame_top.place(relx=0.5, rely=0.1, anchor=tk.CENTER)



frame_sel = tk.Frame(ventana, bg=color)
frame_sel.place(relx=0.5, rely=0.3, anchor=tk.CENTER)


frame_ver_build = tk.Frame(ventana,bg=color)
frame_ver_build.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

frame_text_widget = tk.Frame(ventana)
frame_text_widget.place(relx=0.5, rely=0.8, anchor=tk.CENTER)


# Crear una variable para almacenar la selección
combo = ttk.Combobox(frame_top, values=puertos_serie)
combo.pack(side=tk.LEFT, padx=10)

# Botón para mostrar la selección
btn_recargar = tk.Button(frame_top, text="Recargar", command=refrescar_puertos)
btn_recargar.pack(side=tk.LEFT, padx=10)

etiqueta = tk.Label(ventana, text="")
etiqueta.pack(side=tk.BOTTOM)

#Botón Seleccionar Carpeta
btn_folder = tk.Button(frame_sel, text="Seleccionar carpeta", command=sel_folder)
btn_folder.pack(side=tk.TOP, pady=(10 , 5))


#Boton Verificar
btn_verify = tk.Button(frame_ver_build, text="Verificar",command=verify)
btn_verify.pack(side=tk.LEFT, padx=10)

#Boton Build & Upload
btn_build = tk.Button(frame_ver_build, text="Build & Upload",command=build)
btn_build.pack(side=tk.LEFT, padx=10)


text_widget = tk.Text(frame_text_widget, wrap=tk.WORD, height= 3, width=40)
text_widget.pack()

redirigir_output(text_widget)
refrescar_puertos()

ventana.mainloop()

