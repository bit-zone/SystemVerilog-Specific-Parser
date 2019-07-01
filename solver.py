import numpy as np
import random
import copy
import math

MAX_COUNTS = 500
TEMPERATURE = 1
PLS0 = 0
NUM_OF_BOOL_VARIABLES = 0

def compute_pls(iteration_number):
    pls = PLS0 * math.pow(2,1-iteration_number)
    if (pls>1):
        pls = 1
    elif (pls <0):
        pls = 0
    return pls


def is_discrete(clause):
    """
    clause is a list : it can be discrete(inside) or two lists for boolean and integer coeffs
    """
    if isinstance(clause[0], int):
        return True
    else:
        return False


def make_random_assignment_int(int_var_sizes):
    """
    
    """
    current_values_int = []
    for var_size in int_var_sizes:
        maximum = math.pow(2, var_size-1)-1
        minimum = -math.pow(2, var_size-1)-1
        current_values_int.append(random.randint(minimum,maximum))
    return current_values_int


def make_random_assignment_imp(NUM_OF_BOOL_VARIABLES):
    """

    """
    current_values_imp = [0]*NUM_OF_BOOL_VARIABLES
    for i in range(NUM_OF_BOOL_VARIABLES):
        current_values_imp[i] = random.randint(0,1)
    return current_values_imp


def check_int_literal(int_literal, current_values_int):
    """

    """
    copy_current_values_int = copy.deepcopy(current_values_int)
    count = 0
    while (len(int_literal)-1)!=len(copy_current_values_int):
        copy_current_values_int.append(0)
    for j in range(len(int_literal)-1):
        count += int_literal[j] * copy_current_values_int[j]
    count += int_literal[-1] #bias
    if count <= 0:
        return True
    return False


def check_bool_literal(bool_literal, bool_literal_num, current_values_imp):
    """
    boolean literal is just a number in the lst of boolean literals in the clause
    """
    # if not exist
    if bool_literal == 0: # 0b00 # not exist bool literal
        return -1
    if bool_literal == 3: # 0b11
        bool_literal_value = 1
    elif bool_literal == 2: # 0b10
        bool_literal_value = 0
    if current_values_imp[bool_literal_num] == bool_literal_value:
        return True
    else:
        return False 


def check_clause(clause, current_values_imp, current_values_int):
    """
    [[],[]]
    """
    if is_discrete(clause)==True:
        # check implication 
        pass
    else: # check normal clause (boolean and integer)
        # check boolean literals
        bool_literals = clause[0] # [0,0]or [0,1]...
        num = 0
        for bool_literal in bool_literals:
            if check_bool_literal(bool_literal, num , current_values_imp)==True:
                return True
            num+=1
        int_literal = clause[1]
        if check_int_literal(int_literal, current_values_int)==True:
            return True
        return False


def check_all(formula, current_values_imp, current_values_int):
    """
    """
    for clause in formula:
        if check_clause(clause, current_values_imp, current_values_int)==False:
            return False
    return True


def find_number_of_unsatisfied_clauses(formula, current_values_imp, current_values_int):
    """
    """
    c = 0
    for clause in formula:
        if check_clause(clause, current_values_imp, current_values_int) == False:
            c += 1
    return c


def reduce_literal(int_literal, index_variable_to_be_unchanged, current_values_int, NUM_OF_INT_VARIABLES):# from 0 to NUM_OF_INT_VARIABLES-1
    """

    """    
    reduced_int_literal = []
    reduced_int_literal = copy.deepcopy(int_literal)
    
    # this variable is not found in that int literal
    if reduced_int_literal[index_variable_to_be_unchanged] == 0:
            return False

    new_bias = 0
    bias_updating = False
    for i in range(NUM_OF_INT_VARIABLES):
        if i != index_variable_to_be_unchanged:
            if int_literal[i]!=0:
                bias_updating = True 
            new_bias += current_values_int[i] * int_literal[i]
            reduced_int_literal[i] = 0

    #updating the bias
    if bias_updating==True:
        reduced_int_literal[-1] = int_literal[-1] +new_bias
    
    # +ve value coeff                                                                     
    if(reduced_int_literal[index_variable_to_be_unchanged] > 0): 
        reduced_int_literal[-1] = int(reduced_int_literal[-1]/int_literal[index_variable_to_be_unchanged])
        reduced_int_literal[index_variable_to_be_unchanged] = 1
    
    # -ve value coeff
    else: 
        reduced_int_literal[-1] = int(reduced_int_literal[-1]/(-1 * int_literal[index_variable_to_be_unchanged]))
        reduced_int_literal[index_variable_to_be_unchanged] = -1


    #should be something like the form of y1 + 10 <= 0 or -1 y1 +5 <= 0
    return reduced_int_literal


def get_active_clauses(formula, index_variable_to_be_unchanged, current_values_imp, current_values_int, 
    NUM_OF_INT_VARIABLES):
    """
    active_formula is an array of reduced int literals
    """
    active_formula = []
    for clause in formula:
        skip = 0
        active_clause = []
        bool_literals = clause[0]
        num = 0
        for bool_literal in bool_literals:
            if check_bool_literal(bool_literal, num, current_values_imp)==True:
                skip = 1 # the clause is satisfied
            num+=1
                
        if skip==0: # the clause is not satisfied
            int_literal = clause[1]
            reduced_int_literal = reduce_literal(int_literal, index_variable_to_be_unchanged, 
            current_values_int, NUM_OF_INT_VARIABLES)
            if reduced_int_literal==False: # this variable is not in that int literal
                if check_int_literal(int_literal, current_values_int)==True:
                    skip = 1
        if skip==0: # the clause is not satisfied 
            int_literal = clause[1]
            reduced_int_literal = reduce_literal(int_literal, index_variable_to_be_unchanged, 
            current_values_int, NUM_OF_INT_VARIABLES)
            if reduced_int_literal!=False: # this variable is in that int literal
                active_formula.append(reduced_int_literal)
    return active_formula


#encoding
UNIFORM = 3
EXP_UP = 2
EXP_DOWN = 1
#########

# The interval(segment) is defined as an array of 3 elements ( from , to , type ) ,
# type is ( uniform(3) ,exp_up(2) or exp_down(1) ) .
# The indicator will be explained later.

INTERVAL_NUM_OF_ROWS = 3 # range and type (uniform or exp)
INDICATOR_NUM_OF_ROWS = 2*INTERVAL_NUM_OF_ROWS  #indicator for one reduced literal has two intervals
NUM_OF_INTERVALS_IN_CLAUSE_INDICATOR = math.pow(2,1)
CLAUSE_INDICATOR_NUM_OF_ROWS = NUM_OF_INTERVALS_IN_CLAUSE_INDICATOR * INTERVAL_NUM_OF_ROWS


def is_int_literal_exist(int_literal):
    """
    test if the literal coefficients are all zeros (not exist)
    """
    exist = False
    for coeff in int_literal:
        if coeff!=0:
            exist = True
    return exist


def get_range(active_formula):
    c_less_than = 2**31 # any very large number
    c_greater_than = -2**31 # any very small number
    flag=''
    for reduced_int_literal in active_formula:
        for i in range(len(reduced_int_literal)-1):
            if reduced_int_literal[i] == 0:
                continue
            elif reduced_int_literal[i] == 1:  # y<=c , c = -bias
                c_less_than = min(c_less_than, -reduced_int_literal[-1])
            elif reduced_int_literal[i] == -1:  # y>=c , c=bias
                c_greater_than = max(c_greater_than, reduced_int_literal[-1])
        flag = 'normal'
        if c_less_than == 2**31: # any very large number 
            flag = 'greater_than_only'
        if c_greater_than == -2**31: # any very small number
            flag = 'less_than_only'
    return flag, c_less_than, c_greater_than


def get_segments_from_active_formula(int_var_sizes, index_variable_to_be_unchanged, active_formula):
    segments = []
    flag, c_less_than, c_more_than = get_range(active_formula)
    num_segments = 0
    if flag == 'normal':
        if c_less_than >= c_more_than:  # case 1  (expup uniform expdown)(2,3,1)
            num_segments = 3
            segments.append(-math.pow(2,int_var_sizes[index_variable_to_be_unchanged]-1)-1)
            segments.append(c_more_than)
            segments.append(2)
            segments.append(c_more_than)
            segments.append(c_less_than)
            segments.append(3)
            segments.append(c_less_than)
            segments.append(math.pow(2,int_var_sizes[index_variable_to_be_unchanged]-1)-1)
            segments.append(1)
        elif c_less_than < c_more_than:  # case 2  (expup expdown)(2,1)
            num_segments = 2
            segments.append(-math.pow(2,int_var_sizes[index_variable_to_be_unchanged]-1)-1)
            segments.append(int((c_less_than+c_more_than)/2))
            segments.append(2)
            segments.append(int((c_less_than+c_more_than)/2))
            segments.append(math.pow(2,int_var_sizes[index_variable_to_be_unchanged]-1)-1)
            segments.append(1)
    elif flag == 'greater_than_only':
        num_segments = 2
        segments.append(-math.pow(2,int_var_sizes[index_variable_to_be_unchanged]-1)-1)
        segments.append(c_more_than)
        segments.append(2)
        segments.append(c_more_than)
        segments.append(math.pow(2,int_var_sizes[index_variable_to_be_unchanged]-1)-1)
        segments.append(3)
    elif flag == 'less_than_only':
        num_segments = 2
        segments.append(-math.pow(2,int_var_sizes[index_variable_to_be_unchanged]-1)-1)
        segments.append(c_less_than)
        segments.append(3)
        segments.append(c_less_than)
        segments.append(math.pow(2,int_var_sizes[index_variable_to_be_unchanged]-1)-1)
        segments.append(1)
    return segments, num_segments


def select_segment(segments, num_segments):
    """
    """
    w = [0]*num_segments # segments_weights
    for i in range(num_segments):
        segment = []
        first = i * INTERVAL_NUM_OF_ROWS
        last = first + INTERVAL_NUM_OF_ROWS
        segment = segments[first:last]
        segment_type = segment[2]
        segment_from = segment[0]
        segment_to = segment[1]
        if segment_type == UNIFORM:
            w[i] = segment_to - segment_from + 1
        if segment_type == EXP_UP :
            w[i] = ((1 - (math.pow(2, -(segment_to - segment_from + 1))))/(1 - math.pow(2, -1)))
        if segment_type == EXP_DOWN:
            w[i] = ((1 - (math.pow(2, -(segment_to - segment_from + 1))))/(1 - math.pow(2, -1)))
    probabilities = [] # segments_normalized_probabilities
    sum_w = sum(w)
    probabilities = [x / sum_w for x in w]
    # select segment according to the normalized propabilities p1,p2,p3,...
    if len(probabilities) > 1:
        selected_segment_number = np.random.choice(range(num_segments), p=probabilities)
    else:
        selected_segment_number = 0
    first = selected_segment_number * INTERVAL_NUM_OF_ROWS
    last = first + INTERVAL_NUM_OF_ROWS
    selected_segment = segments[first:last]
    return selected_segment, w[selected_segment_number]


def propose_from_segment(segment, w_segment):
    """
    """
    segment_type = segment[2]
    segment_from = segment[0]
    segment_to = segment[1]
    
    if segment_type == UNIFORM:
        proposed_value = random.randint(segment_from, segment_to)
        return proposed_value
    
    theta = random.uniform(0, w_segment)
    d = math.ceil(-1 - math.log(1 - theta * (1 - math.pow(2,-1))))
    if segment_type == EXP_UP :
        proposed_value = segment_to - d
        return proposed_value
    if segment_type == EXP_DOWN:
        proposed_value = segment_from + d
        return proposed_value


def propose(formula, selected_int_variable_index, current_values_imp, current_values_int, int_var_sizes):

    active_formula = get_active_clauses(formula, selected_int_variable_index, current_values_imp,current_values_int, len(int_var_sizes))
    segments, num_segments = get_segments_from_active_formula(int_var_sizes, selected_int_variable_index, active_formula)
    selected_segment,w_selected_segment = select_segment(segments, num_segments)
    proposed_value = propose_from_segment(selected_segment, w_selected_segment)
    return proposed_value


def metropolis_move(formula, current_values_imp, current_values_int, int_var_sizes, NUM_OF_BOOL_VARIABLES, 
    NUM_OF_INT_VARIABLES):
    """
    """
    # select variable bool or int
    if NUM_OF_BOOL_VARIABLES == 0:
        random_variable_is_int_or_bool = random.randint(1, 1)
    elif NUM_OF_INT_VARIABLES == 0:
        random_variable_is_int_or_bool = random.randint(0, 0)
    else:
        random_variable_is_int_or_bool = random.randint(0, 1)  ## 1 --> int     0-->  bool
    if random_variable_is_int_or_bool == 0:
        # select bool variable
        selected_bool_variable_index = random.choice(range(NUM_OF_BOOL_VARIABLES))
        # flip the value of this selected bool variable
        if current_values_imp[selected_bool_variable_index] == 0:
            current_values_imp[selected_bool_variable_index] = 1
        elif current_values_imp[selected_bool_variable_index] == 1:
            current_values_imp[selected_bool_variable_index] = 0
        return current_values_imp, current_values_int
    else:                                                                                                  
        # select int variable
        selected_int_variable_index = random.choice(range(NUM_OF_INT_VARIABLES))
        print(selected_int_variable_index)
        proposed_value = propose(formula, selected_int_variable_index, current_values_imp,
        current_values_int, int_var_sizes)
        # save current int assignment
        last_current_values_int = current_values_int
        # update current int assignment
        current_values_int[selected_int_variable_index] = proposed_value
        # Q calculating
        Q = 1
        # U,V calculating
        U = find_number_of_unsatisfied_clauses(formula, current_values_imp,last_current_values_int) 
        
        V = find_number_of_unsatisfied_clauses(formula, current_values_imp,current_values_int)
        
        # take it or not
        if U-V <0:
            pr_do_change = Q * ((math.pow(2,U-V) / TEMPERATURE))
        else:
            pr_do_change=1
        pr_stay = 1 - pr_do_change
        choice = np.random.choice(['do_change', 'stay'], p=[pr_do_change, pr_stay])
        if choice == 'stay':
            return current_values_imp, last_current_values_int
        elif choice == 'do_change':
            # the change is made already
            return current_values_imp, current_values_int


def local_move(formula, current_values_imp, current_values_int, int_var_sizes):
    """
    """
    # 1 select unsatisﬁed clause C ∈ ϕ uniformly at random
    unsatisfied_clauses_indices = []
    for clause in formula:
        if check_clause(clause, current_values_imp, current_values_int) == False:
            i = formula.index(clause)
            unsatisfied_clauses_indices.append(i)
    selected_unsatisfied_clause_index = random.choice(unsatisfied_clauses_indices)

    # bool part
    '''
    for j in range (NUM_OF_BOOL_LITERALS):
        unsatisfied_clause.bool_literals[i].value =~ unsatisfied_clause.bool_literals[i].value
        value =find_number_of_unsatisfied_clauses()
        if (i == 0):
            min_bool = value
        elif (value < min_bool):
            min_bool = value
    
    '''
    
    # int part
    for k in range(1):
        #select random variable that is involved in this literal
        int_variables_in_literal = []
        selected_unsatisfied_clause = []
        first_c = selected_unsatisfied_clause_index * CLAUSE_NUM_OF_ROWS
        last_c = first_c + CLAUSE_NUM_OF_ROWS
        selected_unsatisfied_clause = formula[first_c:last_c]
        
        int_literal = []
        first = (k * INT_LITERAL_NUM_OF_ROWS) + BOOL_LITERAL_NUM_OF_ROWS * NUM_OF_BOOL_LITERALS
        last = first + INT_LITERAL_NUM_OF_ROWS
        int_literal = selected_unsatisfied_clause[first:last]
        for m in range(NUM_OF_INT_VARIABLES):
            if int_literal[m] != 0:
                int_variables_in_literal.append(m)
        selected_int_variable_index = random.choice(int_variables_in_literal)
        
        # save current int assignment
        last_current_values_int = current_values_int
        
        old_number = find_number_of_unsatisfied_clauses(formula, current_values_imp,current_values_int)
        
        current_values_int[selected_int_variable_index] = propose(formula, selected_int_variable_index, 
        current_values_imp, current_values_int, int_var_sizes)
        new_number = find_number_of_unsatisfied_clauses(formula, current_values_imp, current_values_int)
        if (old_number < new_number):
            current_values_int = last_current_values_int
            
    return current_values_imp, current_values_int

def split(list_item, DISCRETE_VAR_INDEXES, IMP_VAR_INDEXES):
    """
    split list of coeffs into 3 lists : discrete, implication, integer variables
    """
    disc = []
    imp = []
    integ = []
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


def solver(SEED, VAR_NUMBER, VAR_SIZES, _, INITIAL_VALUES, LIST_OF_COEFFS, DISCRETE_VAR_INDEXES,
	IMP_VAR_INDEXES, MAX_NUMBER_OF_BOOLEAN_VARIABLES):
    """
    """
    random.seed(SEED)
    np.random.seed(SEED)
    # splitting 
    _,_,int_var_sizes = split(VAR_SIZES, DISCRETE_VAR_INDEXES, IMP_VAR_INDEXES)
    # make random assignments
    current_values_int = make_random_assignment_int(int_var_sizes)
    current_values_imp = make_random_assignment_imp(MAX_NUMBER_OF_BOOLEAN_VARIABLES)
    print('random',current_values_imp,current_values_int)
    # metropolis
    current_values_imp, current_values_int = metropolis_move(LIST_OF_COEFFS, current_values_imp, 
    current_values_int, int_var_sizes, MAX_NUMBER_OF_BOOLEAN_VARIABLES, len(int_var_sizes))
    counter = 1
    print(counter, current_values_imp, current_values_int)
    while check_all(LIST_OF_COEFFS, current_values_imp, current_values_int) == False : #problem here
        counter += 1
        pls = compute_pls(counter)
        choice = np.random.choice(['local', 'metropolis'], p=[pls, 1-pls])
        #choice = 'metropolis'
        if choice == 'local':
            print("local")
            current_values_imp, current_values_int = local_move(LIST_OF_COEFFS, current_values_imp,
            current_values_int, int_var_sizes)
        elif choice == 'metropolis':
            print("metropolis")
            current_values_imp, current_values_int = metropolis_move(LIST_OF_COEFFS, current_values_imp,
            current_values_int, int_var_sizes, MAX_NUMBER_OF_BOOLEAN_VARIABLES, len(int_var_sizes))
        print(counter, current_values_imp, current_values_int)
        if counter == MAX_COUNTS:
            return "conflict!"
            break
    return current_values_int

