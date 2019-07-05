from tkinter import *
from tkinter import filedialog
import tkinter.ttk as ttk
from parser_classes import *
from parser_functions import * 
from solver import solver
import time
from HoverClass import HoverInfo


n = 8 # binary length (width)
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


def is_discrete_clause(clause):
    """
    clause is a list : it can be discrete(inside) or two lists for boolean and integer coeffs
    """
    if isinstance(clause[0], int):
        return True
    else:
        return False


def split_coeffs(list_item):
    """
    split list of coeffs into 2 lists : discrete, integer variables
    """
    disc = []
    integ = []
                # split_coeffs list of coeffs [discrete imp integer]
                # using DISCRETE_VAR_INDEXES 
    for ind in DISCRETE_VAR_INDEXES:
        disc.append(list_item[ind])       
    for i in range(len(list_item)): # integer part only
        if i not in DISCRETE_VAR_INDEXES:
            integ.append(list_item[i])
    return disc, integ


# output in text file mode
def integer_initial_assignment_file_handling(initial_assignment_file_path, integer_initial_values):
    with open(initial_assignment_file_path, "w") as initial_assignment_file:
        disc,integ = split_coeffs(integer_initial_values)
        for item in disc:
            if item is None:
                initial_assignment_file.write("0\n")
            else:
                initial_assignment_file.write(item)
        for item in integ:
            if item is None:
                initial_assignment_file.write("0\n")
            else:
                initial_assignment_file.write(item)


def integer_sizes_file_handling(integer_sizes_file_path, integer_sizes):
    with open(integer_sizes_file_path, "w") as integer_sizes_file:
        disc,integ = split_coeffs(integer_sizes)
        for item in disc:
            string_item = str(item)
            integer_sizes_file.write(string_item)
            integer_sizes_file.write("\n")
        for item in integ:
            string_item = str(item)
            integer_sizes_file.write(string_item)
            integer_sizes_file.write("\n")


def integer_coeff_file_handling(integer_coeff_file_path, LIST_OF_COEFFS):
    with open(integer_coeff_file_path, "w") as integer_coeff_file:
        for list_item in LIST_OF_COEFFS:
            if is_discrete_clause(list_item)==False: # formula (clause)
                # reverse coeffs for input to verilog
                coeffs = list_item[1]
                disc, integ = split_coeffs(coeffs)
                integ.reverse()
                for item in integ: 
                    string_item = '{0:{fill}{width}b}'.format((item + 2**n) % 2**n, fill='0', width=n)
                    integer_coeff_file.write(string_item)
                    integer_coeff_file.write("_")
                disc.reverse()
                for item in disc: # not disc or imp
                    string_item = '{0:{fill}{width}b}'.format((item + 2**n) % 2**n, fill='0', width=n) 
                    integer_coeff_file.write(string_item)
                    integer_coeff_file.write("_")
                integer_coeff_file.write("\n")


def boolean_coeff_file_handling(boolean_coeff_file_path, LIST_OF_COEFFS):
    with open(boolean_coeff_file_path, "w") as boolean_coeff_file:
        for list_item in LIST_OF_COEFFS:
            if is_discrete_clause(list_item)==False: # formula (clause)
                boolean_literals = list_item[0]
                for boolean_literal in boolean_literals:
                    string_item = f"{boolean_literal:02b}"
                    boolean_coeff_file.write(string_item)
                    boolean_coeff_file.write("_")
                boolean_coeff_file.write("\n")


def discrete_number_of_choices_file_handling(discrete_number_of_choices_file_path, LIST_OF_COEFFS):
    with open(discrete_number_of_choices_file_path, "w") as discrete_number_of_choices_file:
        for list_item in LIST_OF_COEFFS:
            if is_discrete_clause(list_item)==True:
                number_of_choices = int(len(list_item)/2)
                string_item = f"{number_of_choices:08b}"
                discrete_number_of_choices_file.write(string_item)
            discrete_number_of_choices_file.write("\n")


def discrete_choices_file_handling(discrete_choices_file_path, LIST_OF_COEFFS):
    with open(discrete_choices_file_path, "w") as discrete_choices_file:
        for list_item in LIST_OF_COEFFS:
            if is_discrete_clause(list_item)==True:
                for discrete_value in list_item:
                    string_item = '{0:{fill}{width}b}'.format((discrete_value + 2**n) % 2**n, fill='0', width=n) 
                    discrete_choices_file.write(string_item)
                    discrete_choices_file.write("_")
            discrete_choices_file.write("\n")


def main(data_decl_text, constraints_text, code_entry):
    """
    """
    VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS = main_parser(code_entry.get(1.0, END))
    data_decl_text.delete("1.0", END)
    constraints_text.delete("1.0", END)
    data_decl_text.insert("1.0", "variables signing:\n {}\n".format(VAR_SIGNING))
    data_decl_text.insert("4.0", "variables sizes:\n {}\n".format(VAR_SIZES))
    data_decl_text.insert("7.0", "variables initial values:\n {}\n".format(INITIAL_VALUES))
    data_decl_text.insert("10.0", "variables index dictioanry:\n {}\n".format(VAR_NUMBER))
    constraints_text.insert("1.0", "constraints coeffs :\n {}\n".format(LIST_OF_COEFFS) )
    
def update_code_entry(code_entry):
	
	INPUT_FILE_PATH = filedialog.askopenfilename()
	# input sv file reading
	with open(INPUT_FILE_PATH, "r") as input_file:
		SOURCE_CODE = input_file.read().replace("\n", "").strip(" ")
	input_file.close()
	code_entry.delete("1.0", END)
	code_entry.insert("1.0", SOURCE_CODE)

def solve(code_entry, seed_entry, solutions_text):
    start_time = time.time()
    VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS = main_parser(code_entry.get(1.0, END))
    seed = int(seed_entry.get())
    formula = []
    for clause in LIST_OF_COEFFS:
        if len(clause)==2:
            formula.append(clause[1])
    moves, int_sols = solver(seed, VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS,
    DISCRETE_VAR_INDEXES, IMP_VAR_INDEXES, MAX_NUMBER_OF_BOOLEAN_VARIABLES)
    solutions_text.delete("1.0", END)
    solutions_text.insert("1.0", "solution list:\n")
    if isinstance(int_sols, str):
        solutions_text.insert(END, int_sols)
    else:
        var_names = list(VAR_NUMBER.keys())
        for i in range(len(int_sols)):
            solutions_text.insert(END, f"{var_names[i]} = {str(int_sols[i])}\n")
        solutions_text.insert(END, f"it takes {str(time.time()-start_time)} seconds to solve!\n")
        solutions_text.insert(END, f"it takes {str(moves)} moves!\n")
        
    
def generate_files(code_entry):
    VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS = main_parser(code_entry.get(1.0, END))
    integer_coeff_file_handling("integer_coeffs.txt", LIST_OF_COEFFS)
    boolean_coeff_file_handling("boolean_coeffs.txt", LIST_OF_COEFFS)
    discrete_number_of_choices_file_handling("discrete_number_of_choices.txt", LIST_OF_COEFFS)
    discrete_choices_file_handling("discrete_choices.txt", LIST_OF_COEFFS)


def clear(data_decl_text, constraints_text, solutions_text):
    data_decl_text.delete("1.0", END)
    constraints_text.delete("1.0", END)
    solutions_text.delete("1.0", END)
####################################### GUI #############################################
root = Tk()
style = ttk.Style()
style.configure("TButton", padding=9, relief="raised", font=("Helvetica ", 13))
style.configure("TFrame",
                padding=6,
                relief="flat",
                bg="LightBlue4",
                fg="gray15")
style.configure("TLabel", foreground="black", font=("Courier", 12))

root.title('SystemVerilog Specific Parser')
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))

frame_left = ttk.Frame(root, borderwidth=4)
frame_right = ttk.Frame(root, borderwidth=4)

CODE_SAMPLE = """class c;
  rand bit [15 :0 ]x ;
  rand integer y;
  rand bit [4 :0 ]arr[12] ;
  rand bit[1:0] z;
  

  constraint legal{
  foreach (arr[i]) {arr[i]+10 <=0;}
  y inside{-20,[-30:-10]};
  x+8>=y;
  -5*y>0;
  x>0;
  z==3 -> x+1<=0;
  if(z==2) {x+3<=0;}
  z==0 -> {x+1>=0; x+2>=0;}
  }
endclass """
code_entry = Text(frame_left, 
                  bg="bisque",
                  fg="gray15",
                  borderwidth=4,
                  font=("Helvetica", 15, "bold italic")
				   )
code_entry.focus_force()
code_entry.insert("1.0", CODE_SAMPLE)

data_decl_label = ttk.Label(frame_right, text="Outputs of parsing data declarations:")
data_decl_text = Text(frame_right, height=10, width=60, relief='raised')

constraints_label = ttk.Label(frame_right, text="Outputs of parsing constraints:")
constraints_text = Text(frame_right, height=10, width=60, relief='raised')

solution_label = ttk.Label(frame_right, text="Solutions:")
solutions_text = Text(frame_right, height=10, width=60, relief='raised')
# create a Scrollbar and associate it with txt
#scroll_data_decl = Scrollbar(frame_out, command=data_decl_text.yview)
#data_decl_text['yscrollcommand'] = scroll_data_decl.set

seed_label = ttk.Label(frame_right, text="write seed value here:")
seed_entry = Entry(frame_right)
seed_entry.insert(END, '1')

button = ttk.Button(
    frame_left,
    text="parse",
    command=lambda: main(data_decl_text, constraints_text, code_entry))
HoverInfo(button, "parse the SystemVerilog file, the output is shown on the screen for debugging")
upload_button = ttk.Button(
	frame_left,
	text="upload",
	command=lambda: update_code_entry(code_entry)
)
HoverInfo(upload_button, "upload the SystemVerilog file")
solve_button = ttk.Button(
	frame_right,
	text="solve",
	command=lambda: solve(code_entry, seed_entry, solutions_text)
)
HoverInfo(solve_button, "solve the constraints")
generate_files_button = ttk.Button(
    frame_left,
	text="generate files",
	command=lambda: generate_files(code_entry)
)
HoverInfo(generate_files_button, "generate binary output of parsing constraints in text files")
clear_button = ttk.Button(
    frame_left,
	text="clear outputs",
	command=lambda: clear(data_decl_text, constraints_text, solutions_text)
)
HoverInfo(clear_button, "clear outputs")

label = ttk.Label(frame_left, text="write and edit code here:")

frame_left.grid_rowconfigure(0, weight=1)
frame_left.grid_columnconfigure(0, weight=1)
frame_left.grid(row=0, column=0, sticky="nsew")
frame_right.grid_rowconfigure(0, weight=1)
frame_right.grid_columnconfigure(0, weight=1)
frame_right.grid(row=0, column=1, sticky="nsew")

# left frame
label.grid(row=0, column=0)
code_entry.grid(row=1, column=0)
button.grid(row=2, column=0)
upload_button.grid(row=2, column=0, sticky=E)
generate_files_button.grid(row=2, column=0, sticky=W)
# right frame
#scroll_data_decl.grid(row=0, column=1, sticky='nsew')
data_decl_label.grid(row=0, column=0)
data_decl_text.grid(row=1, column=0, padx=30, sticky=N)
constraints_label.grid(row=2, column=0, sticky=N)
constraints_text.grid(row=3, column=0, padx=30)
solution_label.grid(row=4, column=0)
solutions_text.grid(row=5, column=0, padx=30)
seed_label.grid(row=6, column=0,padx =20)
seed_entry.grid(row=7, column=0,padx =20)
solve_button.grid(row=8, column=0,padx =20, sticky="nsew")
clear_button.grid(row=9, column=0,padx =20)


root.mainloop()
