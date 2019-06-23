
import numpy as np
import random
import copy
import math

NUM_OF_BOOL_VARIABLES=0  # x0,[x1,x2,...] NUM_OF_BOOL_VARIABLES in all formula  
NUM_OF_INT_VARIABLES=2   # y0+y1+y2+bias<=0  in all formula and in the one literal and in all formula 
NUM_OF_BOOL_LITERALS=0   # [0(exist)/1(not exist)]x0  NUM_OF_BOOL_LITERALS in one clause
NUM_OF_INT_LITERALS=1    # y0+y1+y2+bias<=0   NUM_OF_INT_LITERALS in one clause
NUM_OF_CLAUSES=2         # clause0 and clause1 and clause2  NUM_OF_CLAUSES in formula


INT_LITERAL_NUM_OF_ROWS=(0 if NUM_OF_INT_VARIABLES==0 else NUM_OF_INT_VARIABLES+1)
BOOL_LITERAL_NUM_OF_ROWS=2
CLAUSE_NUM_OF_ROWS=NUM_OF_BOOL_LITERALS*BOOL_LITERAL_NUM_OF_ROWS+NUM_OF_INT_LITERALS*INT_LITERAL_NUM_OF_ROWS
FORMULA_NUM_OF_ROWS=CLAUSE_NUM_OF_ROWS*NUM_OF_CLAUSES


# # NOTES
# - each boolean literal has tow rows in formula list one for exist or not exist and second for x0 or ~x0
# - always NUM_OF_BOOL_VARIABLES=NUM_OF_BOOL_LITERALS


formula=[]
#clause0

formula.append(-1) # -y0+2<=0
formula.append(0)
formula.append(2)

#clause1

formula.append(0) # y0-16<=0
formula.append(1)
formula.append(-16)


##########################################################################################
bit_width_for_int_variables=[]
bit_width_for_int_variables.append(8)
bit_width_for_int_variables.append(8)


TEMPERATURE=1
PLS0=0
SEED=2
random.seed(SEED)
np.random.seed(SEED)


# # Modules(functions) 
# - global variables are usually inputs for all functions , so I don't write them in parameter list of each function


def compute_pls(iteration_number):
    pls = PLS0 * math.pow(2,1-iteration_number)
    if (pls>1):
        pls = 1
    elif (pls <0):
        pls = 0

    return pls


def make_random_assignment_int():
    
    current_values_int=[0]*NUM_OF_INT_VARIABLES
    for i in range(NUM_OF_INT_VARIABLES):
        maximum =math.pow(2,bit_width_for_int_variables[i]-1)-1
        minimum = -math.pow(2,bit_width_for_int_variables[i]-1)-1
        current_values_int[i]=(random.randint(minimum,maximum))
    return current_values_int


def make_random_assignment_bool():
    
    current_values_bool=[0]*NUM_OF_BOOL_VARIABLES
    for i in range(NUM_OF_BOOL_VARIABLES):
        current_values_bool[i]=random.randint(0,1)
    return current_values_bool


def check_int_literal(clause_num,int_literal_num,current_values_int):
    
    clause=[]
    first_c=clause_num *CLAUSE_NUM_OF_ROWS
    last_c=first_c+CLAUSE_NUM_OF_ROWS
    clause=formula[first_c:last_c]
    
    int_literal=[]
    first=(int_literal_num*INT_LITERAL_NUM_OF_ROWS)+BOOL_LITERAL_NUM_OF_ROWS*NUM_OF_BOOL_LITERALS
    last=first+INT_LITERAL_NUM_OF_ROWS
    int_literal=clause[first:last]
    
    #if not exist
    exist=0
    for i in range(INT_LITERAL_NUM_OF_ROWS):
        if int_literal[i]!=0:
            exist=1
    if exist==0:
        return -1
    
    count = 0
    for j in range(NUM_OF_INT_VARIABLES):
        count += int_literal[j] * current_values_int[j]
    count += int_literal[-1] #bias
    if count <= 0:
        return True

    return False


def check_bool_literal(clause_num,bool_literal_num,current_values_bool):
    clause=[]
    first_c=clause_num *CLAUSE_NUM_OF_ROWS
    last_c=first_c+CLAUSE_NUM_OF_ROWS
    clause=formula[first_c:last_c]
    bool_literal=[]
    first=bool_literal_num*BOOL_LITERAL_NUM_OF_ROWS
    last=first+BOOL_LITERAL_NUM_OF_ROWS
    bool_literal=clause[first:last]
    
    #if no boolean literals at all
    if len(bool_literal) ==0: 
        return -1
    #if not exist
    elif bool_literal[0]==0:#not exist bool literal
        return -1
    
    elif current_values_bool[bool_literal_num]==bool_literal[1]:
        return True
    else:
        return False 


def check_clause(clause_num,current_values_bool,current_values_int):#from 0 to NUM_OF_CLAUSES-1
    clause=[]
    first_c=clause_num *CLAUSE_NUM_OF_ROWS
    last_c=first_c+CLAUSE_NUM_OF_ROWS
    clause=formula[first_c:last_c]
    
    #if not exist
    exist=0
    
    for i in range(CLAUSE_NUM_OF_ROWS):
        
        if clause[i]!=0:
            exist=1
    if exist==0:
        return -1
    
    for j in range(NUM_OF_BOOL_LITERALS):
        if check_bool_literal(clause_num,j,current_values_bool)==True :
            return True
    for k in range(NUM_OF_INT_LITERALS):
        if check_int_literal(clause_num,k,current_values_int)==True :
            return True
    return False


def check_formula(current_values_bool,current_values_int):
    for i in range(NUM_OF_CLAUSES):
        if check_clause(i,current_values_bool,current_values_int)==False:
            return False
    return True


def find_number_of_unsatisfied_clauses(current_values_bool,current_values_int):
    c=0
    for i in range(NUM_OF_CLAUSES):
        if check_clause(i,current_values_bool,current_values_int)==False:
            c+=1
    return c


def reduce_literal(clause_num,int_literal_num,index_variable_to_be_unchanged,current_values_int):# from 0 to NUM_OF_INT_VARIABLES-1
    clause=[]
    first_c=clause_num *CLAUSE_NUM_OF_ROWS
    last_c=first_c+CLAUSE_NUM_OF_ROWS
    clause=formula[first_c:last_c]
    
    int_literal=[]
    first=(int_literal_num*INT_LITERAL_NUM_OF_ROWS)+BOOL_LITERAL_NUM_OF_ROWS*NUM_OF_BOOL_LITERALS
    last=first+INT_LITERAL_NUM_OF_ROWS
    int_literal=clause[first:last]

    reduced_int_literal=[]
    reduced_int_literal=int_literal
    
    # this variable is not found in that int literal
    if reduced_int_literal[index_variable_to_be_unchanged] == 0:
            return False

    new_bias = 0
    bias_updating=False
    for i in range(NUM_OF_INT_VARIABLES):
        if i != index_variable_to_be_unchanged:
            if int_literal[i]!=0:
                bias_updating=True 
            new_bias += current_values_int[i] * int_literal[i]
            reduced_int_literal[i] = 0

    #updating the bias
    if bias_updating==True:
        reduced_int_literal[-1] =int_literal[-1] +new_bias
    
    # +ve value coeff                                                                     
    if(reduced_int_literal[index_variable_to_be_unchanged] > 0): 
        reduced_int_literal[-1] /= int_literal[index_variable_to_be_unchanged]
        reduced_int_literal[index_variable_to_be_unchanged] = 1
    
    # -ve value coeff
    else: 
        reduced_int_literal[-1] /= (-1 * int_literal[index_variable_to_be_unchanged])
        reduced_int_literal[index_variable_to_be_unchanged] = -1


    #should be something like the form of y1 + 10 <= 0 or -1 y1 +5 <= 0
    return reduced_int_literal


def get_active_clauses(index_variable_to_be_unchanged,current_values_bool,current_values_int): # return active formula
    
    active_formula=[0]*FORMULA_NUM_OF_ROWS
    for i in range(NUM_OF_CLAUSES):
        skip=0
        active_clause=[0]*CLAUSE_NUM_OF_ROWS

        for j in range(NUM_OF_BOOL_LITERALS):
            if check_bool_literal(i,j,current_values_bool)==True:
                skip=1 # the clause is satisfied
                
        if skip==0:# the clause is not satisfied
            for k in range(NUM_OF_INT_LITERALS):
                reduced_int_literal=reduce_literal(i,k,index_variable_to_be_unchanged,current_values_int)
                if reduced_int_literal==False: # this variable is not in that int literal
                    if check_int_literal(i,k,current_values_int)==True:
                        skip=1
        if skip==0: # the clause is not satisfied 
            for k in range(NUM_OF_INT_LITERALS):
                reduced_int_literal=reduce_literal(i,k,index_variable_to_be_unchanged,current_values_int)
                if reduced_int_literal!=False: # this variable is in that int literal
                    first=(k*INT_LITERAL_NUM_OF_ROWS)+BOOL_LITERAL_NUM_OF_ROWS*NUM_OF_BOOL_LITERALS
                    last=first+INT_LITERAL_NUM_OF_ROWS
                    active_clause[first:last]=reduced_int_literal
        

        first_c=i *CLAUSE_NUM_OF_ROWS
        last_c=first_c+CLAUSE_NUM_OF_ROWS
        active_formula[first_c:last_c]= active_clause
    return active_formula



#encoding
UNIFORM=3
EXP_UP=2
EXP_DOWN=1
#########


# The interval(segment) is defined as an array of 3 elements ( from , to , type ) ,
# type is ( uniform(3) ,exp_up(2) or exp_down(1) ) .
# The indicator will be explained later.

INTERVAL_NUM_OF_ROWS=3 # range and type (uniform or exp)
INDICATOR_NUM_OF_ROWS=2*INTERVAL_NUM_OF_ROWS  #indicator for one reduced literal has two intervals
NUM_OF_INTERVALS_IN_CLAUSE_INDICATOR=math.pow(2,NUM_OF_INT_LITERALS)
NUM_OF_INTERVALS_IN_FORMULA_INDICATOR=math.pow(NUM_OF_INTERVALS_IN_CLAUSE_INDICATOR,NUM_OF_CLAUSES)
CLAUSE_INDICATOR_NUM_OF_ROWS=NUM_OF_INTERVALS_IN_CLAUSE_INDICATOR*INTERVAL_NUM_OF_ROWS
FORMULA_INDICATOR_NUM_OF_ROWS=NUM_OF_INTERVALS_IN_FORMULA_INDICATOR*INTERVAL_NUM_OF_ROWS



def is_int_literal_exist(int_literal):
    #test if the literal coefficients are all zeros (not exist)
    
    exist=False
    for i in range(INT_LITERAL_NUM_OF_ROWS):
        if int_literal[i]!=0:
            exist=True
            
    return exist


# # 12) is_clause_exist 
# to check if it is a clause or not , all coefficients will be zeros if no clause

def is_clause_exist(clause):
    #test if the boolean literal coefficients are all zeros (not exist)
    
    exist=False
    for i in range(BOOL_LITERAL_NUM_OF_ROWS*NUM_OF_BOOL_LITERALS):
        if clause[i]!=0:
            exist=True
    #here if exist = false , then no boolean literals in the clause
    if exist==True:
        return exist
    elif exist==False: # then check existance of int literal
        int_literal=[]
        first=BOOL_LITERAL_NUM_OF_ROWS*NUM_OF_BOOL_LITERALS
        last=first+INT_LITERAL_NUM_OF_ROWS
        int_literal=clause[first:last]
        return is_int_literal_exist(int_literal)



# # 12) get_segments_from_active_formula
# For each clause C, we take the pointwise max (<b>union</b>) of the indicators for relations in C to get an indicator for the clause as a whole. Then we take the pointwise min (<b>intersection</b>) the clause indicators to create a distribution.
# the output should be a list (array) of intervals(segments).

# #  - get_range


def get_range(active_formula):
    c_less_than=1000000 # any very large number
    c_greater_than=-1000000 # any very small number
    flag=''
    for i in range(NUM_OF_CLAUSES):
        
        active_clause=[]
        first_c=i *CLAUSE_NUM_OF_ROWS
        last_c=first_c+CLAUSE_NUM_OF_ROWS
        active_clause=active_formula[first_c:last_c]
        #print(active_clause)
        if is_clause_exist(active_clause) == False:
            continue
        else:
            reduced_int_literal=[]
            first=BOOL_LITERAL_NUM_OF_ROWS*NUM_OF_BOOL_LITERALS
            last=first+INT_LITERAL_NUM_OF_ROWS
            reduced_int_literal=active_clause[first:last]
            #print(reduced_int_literal)
            for j in range(NUM_OF_INT_VARIABLES):
                if reduced_int_literal[j]==0:
                    continue
                elif reduced_int_literal[j]==1:  # y<=c , c = -bias
                    c_less_than= min(c_less_than,-reduced_int_literal[-1])
                elif reduced_int_literal[j]==-1:  # y>=c , c=bias
                    c_greater_than= max(c_greater_than,reduced_int_literal[-1])
        flag='normal'
        if c_less_than == 1000000 :
            flag='greater_than_only'
        if c_greater_than ==-1000000:
            flag='less_than_only'
    return flag,c_less_than,c_greater_than


def get_segments_from_active_formula(index_variable_to_be_unchanged,active_formula):
    segments=[]
    flag,c_less_than,c_more_than =get_range(active_formula)
    num_segments=0
    if flag=='normal':
        if c_less_than >= c_more_than:  # case 1  (expup uniform expdown)(2,3,1)
            num_segments=3
            segments.append(-math.pow(2,bit_width_for_int_variables[index_variable_to_be_unchanged]-1)-1)
            segments.append(c_more_than)
            segments.append(2)
            segments.append(c_more_than)
            segments.append(c_less_than)
            segments.append(3)
            segments.append(c_less_than)
            segments.append(math.pow(2,bit_width_for_int_variables[index_variable_to_be_unchanged]-1)-1)
            segments.append(1)
        elif c_less_than < c_more_than:  # case 2  (expup expdown)(2,1)
            num_segments=2
            segments.append(-math.pow(2,bit_width_for_int_variables[index_variable_to_be_unchanged]-1)-1)
            segments.append(int((c_less_than+c_more_than)/2))
            segments.append(2)
            segments.append(int((c_less_than+c_more_than)/2))
            segments.append(math.pow(2,bit_width_for_int_variables[index_variable_to_be_unchanged]-1)-1)
            segments.append(1)
    elif flag=='greater_than_only':
        num_segments=2
        segments.append(-math.pow(2,bit_width_for_int_variables[index_variable_to_be_unchanged]-1)-1)
        segments.append(c_more_than)
        segments.append(2)
        segments.append(c_more_than)
        segments.append(math.pow(2,bit_width_for_int_variables[index_variable_to_be_unchanged]-1)-1)
        segments.append(3)
    elif flag=='less_than_only':
        num_segments=2
        segments.append(-math.pow(2,bit_width_for_int_variables[index_variable_to_be_unchanged]-1)-1)
        segments.append(c_less_than)
        segments.append(3)
        segments.append(c_less_than)
        segments.append(math.pow(2,bit_width_for_int_variables[index_variable_to_be_unchanged]-1)-1)
        segments.append(1)
    return segments,num_segments

def select_segment(segments,num_segments):
    
    w=[0]*num_segments #segments_weights
    for i in range(num_segments):
        segment=[]
        first=i*INTERVAL_NUM_OF_ROWS
        last=first+INTERVAL_NUM_OF_ROWS
        #print(first)
        #print(last)
        segment=segments[first:last]
        #print(segment)
        segment_type=segment[2]
        segment_from=segment[0]
        segment_to=segment[1]
        if segment_type==UNIFORM:
            w[i]=segment_to-segment_from+1
        if segment_type== EXP_UP :
            w[i]=((1-(math.pow(2,-(segment_to-segment_from+1))))/(1-math.pow(2,-1)))
        if segment_type==EXP_DOWN:
            w[i]=((1-(math.pow(2,-(segment_to-segment_from+1))))/(1-math.pow(2,-1)))
            print(w[i])
    probabilities=[]#segments_normalized_probabilities
    print(w)
    sum_w = sum(w)
    #print(sum_w)
    probabilities = [x / sum_w for x in w]
    print('probabilities: ',probabilities)
    #print(probabilities)
    # select segment according to the normalized propabilities p1,p2,p3,...
    selected_segment_number = np.random.choice(range(num_segments), p=probabilities)
    #print(selected_segment_number)
    first=selected_segment_number*INTERVAL_NUM_OF_ROWS
    last=first+INTERVAL_NUM_OF_ROWS
    selected_segment=segments[first:last]
    return selected_segment,w[selected_segment_number]


def propose_from_segment(segment,w_segment):
    
    
    segment_type=segment[2]
    segment_from=segment[0]
    segment_to=segment[1]
    
    if segment_type==UNIFORM:
        proposed_value = random.randint(segment_from, segment_to)
        return proposed_value
    
    theta = random.uniform(0, w_segment)
    d = math.ceil(-1 - math.log(1 - theta * (1 - math.pow(2,-1))))
    if segment_type== EXP_UP :
        proposed_value = segment_to - d
        return proposed_value
    if segment_type== EXP_DOWN:
        proposed_value = segment_from + d
        return proposed_value


def propose(selected_int_variable_index,current_values_bool,current_values_int):

    active_formula=get_active_clauses(selected_int_variable_index,current_values_bool,current_values_int)
    #print(active_formula)
    segments,num_segments=get_segments_from_active_formula(selected_int_variable_index,active_formula)
    #print(segments,num_segments)
    selected_segment,w_selected_segment=select_segment(segments,num_segments)
    #print(selected_segment,w_selected_segment)
    proposed_value=propose_from_segment(selected_segment,w_selected_segment)
    return proposed_value


def metropolis_move(current_values_bool,current_values_int):
    
    
    #select variable bool or int
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
        if current_values_bool[selected_bool_variable_index]==0:
            current_values_bool[selected_bool_variable_index]=1
        elif current_values_bool[selected_bool_variable_index]==1:
            current_values_bool[selected_bool_variable_index]=0
        return current_values_bool,current_values_int
    else:                                                                                                  
        # select int variable
        selected_int_variable_index = random.choice(range(NUM_OF_INT_VARIABLES))
        print(selected_int_variable_index)
        proposed_value = propose(selected_int_variable_index,current_values_bool,current_values_int)
        # save current int assignment
        last_current_values_int = current_values_int
        #print(last_current_values_int)
        # update current int assignment
        current_values_int[selected_int_variable_index] = proposed_value
        #print(current_values_int)
        # Q calculating
        Q = 1
        # U,V calculating
        U = find_number_of_unsatisfied_clauses(current_values_bool,last_current_values_int) 
        
        V = find_number_of_unsatisfied_clauses(current_values_bool,current_values_int)
        
        # take it or not
        if U-V <0:
            pr_do_change = Q * ((math.pow(2,U-V) / TEMPERATURE))
        else:
            pr_do_change=1
        pr_stay = 1 - pr_do_change
        choice = np.random.choice(['do_change', 'stay'], p=[pr_do_change, pr_stay])
        if choice == 'stay':
            return current_values_bool,last_current_values_int
        elif choice == 'do_change':
            # the change is made already
            return current_values_bool,current_values_int



def local_move(current_values_bool,current_values_int):
    
    
    #1 select unsatisﬁed clause C ∈ ϕ uniformly at random
    unsatisfied_clauses_indices = []
    for i in range(NUM_OF_CLAUSES):
        if check_clause(i,current_values_bool,current_values_int)==False:
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
    for k in range(NUM_OF_INT_LITERALS):
        #select random variable that is involved in this literal
        int_variables_in_literal=[]
        selected_unsatisfied_clause=[]
        first_c=selected_unsatisfied_clause_index *CLAUSE_NUM_OF_ROWS
        last_c=first_c+CLAUSE_NUM_OF_ROWS
        selected_unsatisfied_clause=formula[first_c:last_c]
        
        int_literal=[]
        first=(k*INT_LITERAL_NUM_OF_ROWS)+BOOL_LITERAL_NUM_OF_ROWS*NUM_OF_BOOL_LITERALS
        last=first+INT_LITERAL_NUM_OF_ROWS
        int_literal=selected_unsatisfied_clause[first:last]
        for m in range(NUM_OF_INT_VARIABLES):
            if int_literal[m]!=0:
                int_variables_in_literal.append(m)
        selected_int_variable_index = random.choice(int_variables_in_literal)
        
        # save current int assignment
        last_current_values_int = current_values_int
        
        old_number = find_number_of_unsatisfied_clauses(current_values_bool,current_values_int)
        
        current_values_int[selected_int_variable_index] = propose(selected_int_variable_index,current_values_bool,current_values_int)
        new_number = find_number_of_unsatisfied_clauses(current_values_bool,current_values_int)
        if (old_number<new_number):
            current_values_int = last_current_values_int
            
    return current_values_bool,current_values_int


def solver():
    
    #make random assignments
    current_values_int=make_random_assignment_int()
    current_values_bool=make_random_assignment_bool()
    print('random',current_values_bool,current_values_int)
    #metropolis
    current_values_bool,current_values_int=metropolis_move(current_values_bool,current_values_int)
    counter=1
    print(counter,current_values_bool,current_values_int)

    while check_formula(current_values_bool,current_values_int)==False : #problem here
        counter+=1
        pls=compute_pls(counter)
        choice=np.random.choice(['local','metropolis'], p=[pls,1-pls])
        #choice='metropolis'
        if choice == 'local':
            print("local")
            current_values_bool,current_values_int=local_move(current_values_bool,current_values_int)
        elif choice == 'metropolis':
            print("metropolis")
            current_values_bool,current_values_int=metropolis_move(current_values_bool,current_values_int)
        print(counter,current_values_bool,current_values_int)


solver()

