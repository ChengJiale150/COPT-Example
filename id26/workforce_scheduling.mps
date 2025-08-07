NAME          COPTPROB
OBJSENSE
    MIN
ROWS
 N  __OBJ___       
 G  demand_period_1
 G  demand_period_2
 G  demand_period_3
 G  demand_period_4
 G  demand_period_5
 G  demand_period_6
COLUMNS
    MARKER    'MARKER'                 'INTORG'
    x(1)      __OBJ___         1
    x(1)      demand_period_1  1
    x(1)      demand_period_2  1
    x(2)      __OBJ___         1
    x(2)      demand_period_2  1
    x(2)      demand_period_3  1
    x(3)      __OBJ___         1
    x(3)      demand_period_3  1
    x(3)      demand_period_4  1
    x(4)      __OBJ___         1
    x(4)      demand_period_4  1
    x(4)      demand_period_5  1
    x(5)      __OBJ___         1
    x(5)      demand_period_5  1
    x(5)      demand_period_6  1
    x(6)      __OBJ___         1
    x(6)      demand_period_1  1
    x(6)      demand_period_6  1
    MARKER    'MARKER'                 'INTEND'
RHS
    RHS       demand_period_1  10
    RHS       demand_period_2  15
    RHS       demand_period_3  25
    RHS       demand_period_4  20
    RHS       demand_period_5  18
    RHS       demand_period_6  12
BOUNDS
 LI BOUND     x(1)      0
 LI BOUND     x(2)      0
 LI BOUND     x(3)      0
 LI BOUND     x(4)      0
 LI BOUND     x(5)      0
 LI BOUND     x(6)      0
ENDATA
