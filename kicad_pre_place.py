# coding: utf-8
# KiCad footprint pre place tool (2016-01-30)
# 
# This script places footprints based on the XY coordinate
# of Eeschema's schematic components.


# import sys
import codecs
import pcbnew

def input_num():
    while True:
        try:
            v = float(sys.stdin.readline())
            return v
        except ValueError:
            print 'Value Error!'

comp_flg    = False    # For Detect $Comp section
qty         = -1       # Comp counter
zuwaku      = []       # Sch sheet size
sch_comp    = []       # All Comp info (expect PWR-Symbol)
sch_comp_xy = []       # Comp Location List
pcb_comp_xy = []       # pcb location

scl_size  = float(0.4)  # Scaling for pcb
offset_x  = float(2000) # PCB Place offset X(mils)
offset_y  = float(2000) #                  Y(mils)

pcb      = pcbnew.GetBoard()        # Get pcb all info
pcb_name = pcb.GetFileName()        # current pcb file name
sch_name = pcb_name.replace('.kicad_pcb','.sch') # Generate Sch file name

org_aux  = pcb.GetAuxOrigin()  # fab. origin(gerber etc.) and conv string (non used)
org_grid = pcb.GetGridOrigin() # grid origin and conv string (non used)

#Start Sch operation
f   = codecs.open(sch_name,'r','utf-8') # Sch file reading (utf-8)
sch = f.readlines()
f.close()

for line in sch: # reading each sch lines...

    line = line.lstrip().rstrip()  # Del \t and \n
        
    if line.startswith('$Descr') : # Detect $Descr section...
        
        zuwaku    = line.replace('$Descr ','').split(' ')
        zuwaku[1] = float(zuwaku[1]) # X size
        zuwaku[2] = float(zuwaku[2]) # Y size
                
    if line.startswith('$Comp') : # Detect $Comp section...
        comp_flg = True           # flg on
        qty += 1                  # Component count
        sch_comp.append([])       # ex) sch_comp[0] = []  , sch_comp[1] = [] ....

    elif line.startswith('$EndComp') : # $EndComp -> flg off
        comp_flg = False

    if comp_flg :   # from $Comp to $EndComp
        
        if not line.startswith('$Comp') :  # except 1st line($Comp)
            sch_comp[qty].append(line)     # add comp all info
                        
            # ex) sch_comp[0][0] <- 'L 74AC04 U2'
            #             [0][1] <- 'U 1 1 512E0139'
            #             [0][2] <- 'P 4050 6950'
            #     ....



# Get Ref.No and XY
for c_line in sch_comp:

    if  '#' not in c_line[0] :          # except PWR SYMBOL (GND,Vcc,PWR_FLG etc.)
        ref      = c_line[0].split(' ')
        unit_num = c_line[1].split(' ')
        xy       = c_line[2].split(' ')
        angle    = c_line[-1]           # orientation matrix (angle and mirror)
        
        if unit_num[1] == '1': # detect 1st unit ( for OPAMP , logic IC etc.)
            
            xy_raw = [ref[2],float(xy[1]),float(xy[2]),angle] # make Ref,x,y list
            sch_comp_xy.append(xy_raw)
            
            # ex) sch_comp_xy[0][0] <- R1
            #                [0][1] <- X(mils)
            #                [0][2] <- Y(mils)
            #                [0][3] <- orientation matrix
            #
            #                [1][0] <- C1
            #                        .....

# End Sch operation

# print sch_comp     <- all comp list
# print sch_comp_xy  <- comp xy list
# print zuwaku       <- Sch paper size

# Start PCB operation

place_flg = 'n'
judge = 'n'

while place_flg == 'n' :

    if judge != 'n' :
        pass
        
    else :
        print 'scale = ' + str(scl_size)
        print 'offset x,y(mil) = ' + '(' +str(offset_x) + ',' + str(offset_y) + ')'
        
        for posi in sch_comp_xy:
        
            pcb_x = int(posi[1] * scl_size) # convert xy Sch --> PCB (scaling)
            pcb_y = int(posi[2] * scl_size)
        
            module = pcb.FindModuleByReference(posi[0])           # Get Footprint info
            module.SetPosition(pcbnew.wxPointMils(pcb_x , pcb_y)) # Move abs x,y(mils)
            module.Move(pcbnew.wxPointMils(offset_x , offset_y))  # Move inc(offset from origin, mils)
        
        print '''
    Place Finished , Press[F3] Key(Redraw).
'''
        
        
        
    print 'Is this floor plan all right(y/n,a:abort)?' # Layout check...
    
    judge = sys.stdin.readline()
    
    if judge == 'y':          # Layout OK
        print 'Place Completed.'
        place_flg = 'y'
        
    elif judge == 'n':        # Change place scale and origin
        print 'place scale = '
        scl_size  = input_num()
        print 'offset x(mil) = '
        offset_x  = input_num()
        print 'offset y(mil) = '
        offset_y  = input_num()
    
    elif judge == 'a':        # abort
        print 'Aborted.'
        place_flg = 'a'
    
    else :
        pass
