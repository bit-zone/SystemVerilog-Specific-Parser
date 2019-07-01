from tkinter import *
from tkinter import filedialog
import tkinter.ttk as ttk
from parser_classes import *
from parser_functions import * 
from solver import solver


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
    split list of coeffs into 3 lists : discrete, implication, integer variables
    """
    disc=[]
    imp=[]
    integ=[]
                # split_coeffs list of coeffs [discrete imp integer]
                # using DISCRETE_VAR_INDEXES and IMP_VAR_INDEXES lists
    for i in range(len(list_item)): # integer part only
        if i in DISCRETE_VAR_INDEXES:
            disc.append(list_item[i])
        elif i in IMP_VAR_INDEXES:
            imp.append(list_item[i])
        else:
            integ.append(list_item[i])
    return disc, imp, integ


# output in text file mode
def integer_initial_assignment_file_handling(initial_assignment_file_path, integer_initial_values):
    with open(initial_assignment_file_path, "w") as initial_assignment_file:
        disc,imp,integ = split_coeffs(integer_initial_values)
        for item in disc:
            if item is None:
                initial_assignment_file.write("0\n")
            else:
                initial_assignment_file.write(item)
        for item in imp:
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
        disc,imp,integ = split_coeffs(integer_sizes)
        for item in disc:
            string_item = str(item)
            integer_sizes_file.write(string_item)
            integer_sizes_file.write("\n")
        for item in imp:
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
                disc, imp, integ = split_coeffs(list_item[1])
                for item in disc: 
                    string_item = '{0:{fill}{width}b}'.format((item + 2**n) % 2**n, fill='0', width=n)
                    integer_coeff_file.write(string_item)
                    integer_coeff_file.write(" ")
                for item in imp: 
                    string_item = '{0:{fill}{width}b}'.format((item + 2**n) % 2**n, fill='0', width=n) 
                    integer_coeff_file.write(string_item)
                    integer_coeff_file.write(" ")
                for item in integ: 
                    string_item = '{0:{fill}{width}b}'.format((item + 2**n) % 2**n, fill='0', width=n) 
                    integer_coeff_file.write(string_item)
                    integer_coeff_file.write(" ")
                integer_coeff_file.write("\n")


def boolean_coeff_file_handling(boolean_coeff_file_path, LIST_OF_COEFFS):
    with open(boolean_coeff_file_path, "w") as boolean_coeff_file:
        for list_item in LIST_OF_COEFFS:
            if is_discrete_clause(list_item)==False: # formula (clause)
                boolean_literals = list_item[0]
                for boolean_literal in boolean_literals:
                    string_item = f"{boolean_literal:02b}"
                    boolean_coeff_file.write(string_item)
                    boolean_coeff_file.write(" ")
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
                    discrete_choices_file.write(" ")
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
	VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS = main_parser(code_entry.get(1.0, END))
	seed = int(seed_entry.get())
	formula = []
	for clause in LIST_OF_COEFFS:
		if len(clause)==2:
			formula.append(clause[1])
	int_sols = solver(seed, VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS,
	DISCRETE_VAR_INDEXES, IMP_VAR_INDEXES, MAX_NUMBER_OF_BOOLEAN_VARIABLES)
	solutions_text.delete("1.0", END)
	solutions_text.insert("1.0", "solution list:\n {}\n".format(int_sols))


def generate_files(code_entry):
    VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS = main_parser(code_entry.get(1.0, END))
    integer_coeff_file_handling("integer_coeffs.txt", LIST_OF_COEFFS)
    boolean_coeff_file_handling("boolean_coeffs.txt", LIST_OF_COEFFS)
    discrete_number_of_choices_file_handling("discrete_number_of_choices.txt", LIST_OF_COEFFS)
    discrete_choices_file_handling("discrete_choices.txt", LIST_OF_COEFFS)

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
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))

frame_code = ttk.Frame(root, borderwidth=4)
frame_out = ttk.Frame(root, borderwidth=4)



CODE_SAMPLE = """class c;
  rand bit [15 :0 ]x ;
  rand integer y;
  rand bit[1:0] z;
  rand bit a1,a2,a3;

  constraint legal{
  y inside{5,6,[7:11]};
  x+8>=y;
  -5*y>0;
  x>0;
  z==3 -> x+1<=0;
  if(z==2) {x+3<=0;}
  z==0 -> {x+1>=0; x+2>=0;}
  }
endclass """
code_entry = Text(frame_code, 
                  #bg="LightBlue4",
                  fg="gray15",
                  borderwidth=4,
                  font=("Helvetica", 15, "bold italic")
				   )
code_entry.insert("1.0", CODE_SAMPLE)
data_decl_text = Text(frame_out, height=5)
constraints_text = Text(frame_out, height=5)
solutions_text = Text(frame_out, height=5)
# create a Scrollbar and associate it with txt
scroll_data_decl = Scrollbar(frame_code, command=data_decl_text.yview)
data_decl_text['yscrollcommand'] = scroll_data_decl.set

seed_label = ttk.Label(frame_code, text="write seed value here:")
seed_entry = Entry(frame_code)

button = ttk.Button(
    frame_code,
    text="parse",
    command=lambda: main(data_decl_text, constraints_text, code_entry))

upload_button = ttk.Button(
	frame_code,
	text="upload",
	command=lambda: update_code_entry(code_entry)
)

solve_button = ttk.Button(
	frame_code,
	text="solve",
	command=lambda: solve(code_entry, seed_entry, solutions_text)
)
generate_files_button = ttk.Button(
    frame_code,
	text="generate files",
	command=lambda: generate_files(code_entry)
)

label = ttk.Label(frame_code, text="write and edit code here:")
frame_code.grid(row=0, column=0)
frame_out.grid(row=0, column=1)

label.grid(row=0, column=0)
code_entry.grid(row=1, column=0)
button.grid(row=2, column=0)
upload_button.grid(row=2, column=0, sticky=E)
generate_files_button.grid(row=2, column=0, sticky=W)
seed_label.grid(row=2, column= 1,padx =20)
seed_entry.grid(row=3, column=1,padx =20)
solve_button.grid(row=4, column=1,padx =20)
#scroll_data_decl.grid(row=0, column=1, sticky='nsew')
data_decl_text.grid(row=0, column=1)
constraints_text.grid(row=1, column=1)
solutions_text.grid(row=2, column=1)

root.mainloop()
