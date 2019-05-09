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
    VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, BOOLEAN_INITIAL_VALUES, BOOLEAN_VAR_NUMBER = parse_data_declarations(C)
    LIST_OF_COEFFS = parse_constraints(C)
    return VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS


def main(data_decl_text, constraints_text, code_entry):
    """
    """
    VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS = main_parser(code_entry.get(1.0, END))
    data_decl_text.delete("1.0", END)
    constraints_text.delete("1.0", END)
    data_decl_text.insert("1.0", "variables signing:\n {}\n".format(VAR_SIGNING))
    data_decl_text.insert("4.0", "variables sizes:\n {}\n".format(VAR_SIZES))
    data_decl_text.insert("7.0", "variables initial values:\n {}\n".format(INITIAL_VALUES))
    data_decl_text.insert("10.0", "variables initial values:\n {}\n".format(VAR_NUMBER))
    constraints_text.insert("1.0", "constraints coeffs :\n {}\n".format(LIST_OF_COEFFS) )
    


root = Tk()

style = ttk.Style()
# style.theme_use("default")
style.configure("TButton", padding=6, relief="flat")
style.configure("TFrame",
                padding=6,
                relief="flat",
                bg="LightBlue4",
                fg="gray15")
style.configure("TLabel")


root.title('SystemVerilog Specific Parser')
root.geometry("")

frame_code = ttk.Frame(root, borderwidth=4)
frame_out = ttk.Frame(root, borderwidth=4)



CODE_SAMPLE = """class c;
  rand bit [15 :0 ]x ;
  rand integer y;
  rand bit[1:0] z;
  rand bit a1,a2,a3;

  constraint legal{
  y inside{5,6,[7:11]};
  x+8<=y;
  -5*y>0;
  x>0;
  z==3 -> x+1<=0;
  if(z==2) {x+3<=0;}
  z==0 -> {x+1>=0; x+2>=0;}
  

  }

endclass """
code_entry = Text(frame_code, 
                  bg="LightBlue4",
                  fg="gray15",
                  borderwidth=4,
                  font=("Helvetica", 15, "bold italic"))
code_entry.insert("1.0", CODE_SAMPLE)
data_decl_text = Text(frame_out)
constraints_text = Text(frame_out)

button = ttk.Button(
    frame_code,
    text="parse",
    command=lambda: main(data_decl_text, constraints_text, code_entry))

frame_code.grid(row=0, column=0)
frame_out.grid(row=0, column=1)

code_entry.grid(row=0, column=0)
button.grid(row=1, column=0)
data_decl_text.grid(row=0, column=0)
constraints_text.grid(row=1, column=0)
root.mainloop()
