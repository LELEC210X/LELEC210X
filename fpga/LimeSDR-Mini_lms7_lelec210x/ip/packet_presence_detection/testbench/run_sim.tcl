
set TOP_LEVEL_NAME "top_tb"


set QSYS_SIMDIR .

source ./mentor/msim_setup.tcl

dev_com

com 

vlog -sv ./top_tb.sv
vlog -sv ./test_program.sv


elab

do wave.do
run 80000ns
