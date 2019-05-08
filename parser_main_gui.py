from parser_classes import *
from parser_functions import *
from tkinter import *
import tkinter.ttk as ttk
"""
we don't support else or not equal implication yet.
"""


def main_parser(SOURCE_CODE):
    """
    """
    C = parse(SOURCE_CODE, ClassDeclaration)
    VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES = parse_data_declarations(C)
    LIST_OF_COEFFS = parse_constraints(C)
    return VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS


def main(var_signing_label, var_sizes_label,var_initial_values_label,var_number_label, code_entry):
    """
    """
    VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS = main_parser(
        code_entry.get(1.0, END))

    var_signing_label.config(
        text="variables signing:\n {}".format(VAR_SIGNING))
    var_sizes_label.config(text="variables sizes:\n {}".format(VAR_SIZES))
    var_initial_values_label.config(
        text="variables initial values:\n {}".format(INITIAL_VALUES))
    var_number_label.config(
        text="variables names and numbers:\n {}".format(VAR_NUMBER))


root = Tk()

style = ttk.Style()
#style.theme_use("default")
style.configure("TButton", padding=6, relief="flat")
style.configure("TFrame",
                padding=6,
                relief="flat",
                bg="LightBlue4",
                fg="gray15")
style.configure("TLabel", font=("Helvetica", 15, "bold italic"))


root.title('SystemVerilog Specific Parser')
#root.geometry("800x600")

frame_code = ttk.Frame(root, relief='flat', borderwidth=4, height=700, width=300)
frame_out = ttk.Frame(root, relief='flat', borderwidth=4)
frame_button = ttk.Frame(root, relief='flat', borderwidth=4)

code_entry = Text(frame_code,
                  bg="LightBlue4",
                  fg="gray15",
                  borderwidth=4,
                  font=("Helvetica", 15, "bold italic"))
var_signing_label = ttk.Label(frame_out, text="var signing:")
var_sizes_label = ttk.Label(frame_out, text="var sizes:")
var_initial_values_label = ttk.Label(frame_out, text="var initial values:")
var_number_label = ttk.Label(frame_out, text="var number:")
button = ttk.Button(frame_button,
                    text="parse",
                    command=lambda: main(var_signing_label, var_sizes_label,
                                         var_initial_values_label,var_number_label, code_entry))

frame_code.grid(row=0, column=0)
frame_out.grid(row=0, column=1)
frame_button.grid(row=1, column=1)
code_entry.grid(row=0, column=0)
button.grid(row=0, column=0)
var_signing_label.grid(row=0, column=0)
var_sizes_label.grid(row=1, column=0)
var_initial_values_label.grid(row=2, column=0)
var_number_label.grid(row=3, column=0)
root.mainloop()
