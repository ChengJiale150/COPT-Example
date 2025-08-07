NAME          COPTPROB
OBJSENSE
    MAX
ROWS
 N  __OBJ___           
 L  budget_constraint  
 L  weight_constraint  
 G  min_vegetable_types
 L  logic_upper_0      
 G  logic_lower_0      
 L  logic_upper_1      
 G  logic_lower_1      
 L  logic_upper_2      
 G  logic_lower_2      
 L  logic_upper_3      
 G  logic_lower_3      
 L  logic_upper_4      
 G  logic_lower_4      
COLUMNS
    x_protein(0)    __OBJ___             23
    x_protein(0)    budget_constraint    3
    x_protein(0)    weight_constraint    100
    x_protein(1)    __OBJ___             20
    x_protein(1)    budget_constraint    5
    x_protein(1)    weight_constraint    100
    x_protein(2)    __OBJ___             8
    x_protein(2)    budget_constraint    1.5
    x_protein(2)    weight_constraint    100
    MARKER    'MARKER'                 'INTORG'
    y_vegetable(0)  __OBJ___             2.7999999999999998
    y_vegetable(0)  budget_constraint    1.2
    y_vegetable(0)  weight_constraint    100
    y_vegetable(0)  logic_upper_0        1
    y_vegetable(0)  logic_lower_0        1
    y_vegetable(1)  __OBJ___             0.90000000000000002
    y_vegetable(1)  budget_constraint    0.80000000000000004
    y_vegetable(1)  weight_constraint    100
    y_vegetable(1)  logic_upper_1        1
    y_vegetable(1)  logic_lower_1        1
    y_vegetable(2)  __OBJ___             2.8999999999999999
    y_vegetable(2)  budget_constraint    1.5
    y_vegetable(2)  weight_constraint    100
    y_vegetable(2)  logic_upper_2        1
    y_vegetable(2)  logic_lower_2        1
    y_vegetable(3)  __OBJ___             1
    y_vegetable(3)  budget_constraint    1
    y_vegetable(3)  weight_constraint    100
    y_vegetable(3)  logic_upper_3        1
    y_vegetable(3)  logic_lower_3        1
    y_vegetable(4)  __OBJ___             3.1000000000000001
    y_vegetable(4)  budget_constraint    2
    y_vegetable(4)  weight_constraint    100
    y_vegetable(4)  logic_upper_4        1
    y_vegetable(4)  logic_lower_4        1
    z_choice(0)     min_vegetable_types  1
    z_choice(0)     logic_upper_0        -8
    z_choice(0)     logic_lower_0        -1
    z_choice(1)     min_vegetable_types  1
    z_choice(1)     logic_upper_1        -8
    z_choice(1)     logic_lower_1        -1
    z_choice(2)     min_vegetable_types  1
    z_choice(2)     logic_upper_2        -8
    z_choice(2)     logic_lower_2        -1
    z_choice(3)     min_vegetable_types  1
    z_choice(3)     logic_upper_3        -8
    z_choice(3)     logic_lower_3        -1
    z_choice(4)     min_vegetable_types  1
    z_choice(4)     logic_upper_4        -8
    z_choice(4)     logic_lower_4        -1
    MARKER    'MARKER'                 'INTEND'
RHS
    RHS       budget_constraint    20
    RHS       weight_constraint    800
    RHS       min_vegetable_types  3
BOUNDS
 LI BOUND     y_vegetable(0)  0
 LI BOUND     y_vegetable(1)  0
 LI BOUND     y_vegetable(2)  0
 LI BOUND     y_vegetable(3)  0
 LI BOUND     y_vegetable(4)  0
 UP BOUND     z_choice(0)     1
 UP BOUND     z_choice(1)     1
 UP BOUND     z_choice(2)     1
 UP BOUND     z_choice(3)     1
 UP BOUND     z_choice(4)     1
ENDATA
