NAME          COPTPROB
OBJSENSE
    MAX
ROWS
 N  __OBJ___               
 L  wood_resource          
 L  steel_resource         
 L  truck_train_exclusive  
 L  boat_requires_plane    
 L  boat_not_exceed_train  
 L  quantity_upper_bound_1 
 L  quantity_upper_bound_2 
 L  quantity_upper_bound_3 
 L  quantity_upper_bound_4 
 G  production_activation_1
 G  production_activation_2
 G  production_activation_3
 G  production_activation_4
COLUMNS
    MARKER    'MARKER'                 'INTORG'
    x(1)      __OBJ___                 5
    x(1)      wood_resource            12
    x(1)      steel_resource           6
    x(1)      quantity_upper_bound_1   1
    x(1)      production_activation_1  1
    x(2)      __OBJ___                 10
    x(2)      wood_resource            20
    x(2)      steel_resource           3
    x(2)      quantity_upper_bound_2   1
    x(2)      production_activation_2  1
    x(3)      __OBJ___                 8
    x(3)      wood_resource            15
    x(3)      steel_resource           5
    x(3)      boat_not_exceed_train    1
    x(3)      quantity_upper_bound_3   1
    x(3)      production_activation_3  1
    x(4)      __OBJ___                 7
    x(4)      wood_resource            10
    x(4)      steel_resource           4
    x(4)      boat_not_exceed_train    -1
    x(4)      quantity_upper_bound_4   1
    x(4)      production_activation_4  1
    y(1)      truck_train_exclusive    1
    y(1)      quantity_upper_bound_1   -74
    y(1)      production_activation_1  -1
    y(2)      boat_requires_plane      -1
    y(2)      quantity_upper_bound_2   -44
    y(2)      production_activation_2  -1
    y(3)      boat_requires_plane      1
    y(3)      quantity_upper_bound_3   -59
    y(3)      production_activation_3  -1
    y(4)      truck_train_exclusive    1
    y(4)      quantity_upper_bound_4   -89
    y(4)      production_activation_4  -1
    MARKER    'MARKER'                 'INTEND'
RHS
    RHS       wood_resource            890
    RHS       steel_resource           500
    RHS       truck_train_exclusive    1
BOUNDS
 LI BOUND     x(1)      0
 LI BOUND     x(2)      0
 LI BOUND     x(3)      0
 LI BOUND     x(4)      0
 UP BOUND     y(1)      1
 UP BOUND     y(2)      1
 UP BOUND     y(3)      1
 UP BOUND     y(4)      1
ENDATA
