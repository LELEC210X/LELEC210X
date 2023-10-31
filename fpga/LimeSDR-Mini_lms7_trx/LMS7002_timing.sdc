# ----------------------------------------------------------------------------
# FILE: 	LMS7002_timing.sdc
# DESCRIPTION:	Timing constrains for LMS7002 IC
# DATE:	June 2, 2017
# AUTHOR(s):	Lime Microsystems
# REVISIONS:
# ----------------------------------------------------------------------------
# NOTES:
<<<<<<< refs/remotes/upstream/main
# 
=======
#
>>>>>>> Revert "enlever le chain de argu"
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
#Timing parameters
# ----------------------------------------------------------------------------
#LMS7002
	#LMS_MCLK2 period
set LMS_MCLK1_period  		8.00
set LMS_MCLK2_period			8.00
	#Setup and hold times from datasheet
set LMS_LMS7_Tsu				1.20
set LMS_LMS7_Th				1.00

	#Measured Tco_min and Tco_max values
set LMS_Tco_max				1.05
set LMS_Tco_min				2.90

	#Tco based
set LMS7_IN_MAX_DELAY [expr $LMS_Tco_max]
set LMS7_IN_MIN_DELAY [expr $LMS_Tco_min]

# ----------------------------------------------------------------------------
#Base clocks
# ----------------------------------------------------------------------------
create_clock 	-name LMS_MCLK2 \
					-period 	$LMS_MCLK2_period \
								[get_ports LMS_MCLK2]
<<<<<<< refs/remotes/upstream/main
							
=======

>>>>>>> Revert "enlever le chain de argu"
create_clock 	-name LMS_MCLK1 \
					-period 	$LMS_MCLK1_period \
								[get_ports LMS_MCLK1]

# ----------------------------------------------------------------------------
#Virtual clocks
# ----------------------------------------------------------------------------
create_clock 	-name LMS_MCLK2_VIRT \
					-period 	$LMS_MCLK2_period
<<<<<<< refs/remotes/upstream/main
					
=======

>>>>>>> Revert "enlever le chain de argu"

# ----------------------------------------------------------------------------
#Generated clocks
# ----------------------------------------------------------------------------

#LMS TX PLL
create_generated_clock 	-name  TX_C0 \
								-master 	[get_clocks LMS_MCLK2] \
								-source 	[get_pins -compatibility_mode *pll_top*|pll1|inclk[0]] \
								-phase 0 \
											[get_pins -compatibility_mode *pll_top*|pll1|clk[0]]
<<<<<<< refs/remotes/upstream/main
								
=======

>>>>>>> Revert "enlever le chain de argu"
create_generated_clock 	-name   TX_C1 \
								-master 	[get_clocks LMS_MCLK2] \
								-source 	[get_pins -compatibility_mode *pll_top*|pll1|inclk[0]] \
								-phase 90 \
											[get_pins -compatibility_mode *pll_top*|pll1|clk[1]]
<<<<<<< refs/remotes/upstream/main
								
=======

>>>>>>> Revert "enlever le chain de argu"
create_generated_clock 	-name   RX_C2 \
								-master 	[get_clocks LMS_MCLK2] \
								-source 	[get_pins -compatibility_mode *pll_top*|pll1|inclk[0]] \
								-phase 0 \
											[get_pins -compatibility_mode *pll_top*|pll1|clk[2]]

create_generated_clock 	-name   RX_C3 \
								-master 	[get_clocks LMS_MCLK2] \
								-source 	[get_pins -compatibility_mode *pll_top*|pll1|inclk[0]] \
								-phase 90 \
											[get_pins -compatibility_mode *pll_top*|pll1|clk[3]]
<<<<<<< refs/remotes/upstream/main
								
#LMS1_FCLK1 clock output pin 
=======

#LMS1_FCLK1 clock output pin
>>>>>>> Revert "enlever le chain de argu"
create_generated_clock 	-name LMS_FCLK1 \
								-master 	[get_clocks TX_C0] \
								-source 	[get_pins -compatibility_mode *pll_top*|*inst6*|*dataout*] \
											[get_ports LMS_FCLK1]
<<<<<<< refs/remotes/upstream/main
								
=======

>>>>>>> Revert "enlever le chain de argu"
#create_generated_clock 	-name LMS_FCLK1_DRCT \
#								-master 	[get_clocks LMS_MCLK1] \
#								-source 	[get_pins -compatibility_mode *pll_top*|*inst6*|*dataout*] \
#											[get_ports LMS_FCLK1] \
#								-add
<<<<<<< refs/remotes/upstream/main
								
#LMS_FCLK2 clock 							
=======

#LMS_FCLK2 clock
>>>>>>> Revert "enlever le chain de argu"
create_generated_clock 	-name LMS_FCLK2 \
								-master 	[get_clocks RX_C2] \
								-source 	[get_pins -compatibility_mode *pll_top*|*inst7*|*dataout*] \
											[get_ports {LMS_FCLK2}]
<<<<<<< refs/remotes/upstream/main
								
=======

>>>>>>> Revert "enlever le chain de argu"
#create_generated_clock 	-name LMS_FCLK2_DRCT \
#								-master 	[get_clocks LMS_MCLK1] \
#								-source 	[get_pins -compatibility_mode *pll_top*|*inst7*|*dataout*] \
#											[get_ports LMS_FCLK2] \
#								-add
<<<<<<< refs/remotes/upstream/main
								
=======

>>>>>>> Revert "enlever le chain de argu"
# ----------------------------------------------------------------------------
#Input constraints
# ----------------------------------------------------------------------------
#LMS1 when MCLK2 is 160MHz
set_input_delay	-max $LMS7_IN_MAX_DELAY \
						-clock 	[get_clocks LMS_MCLK2_VIRT] \
									[get_ports {LMS_DIQ2_D[*] LMS_ENABLE_IQSEL2}]
<<<<<<< refs/remotes/upstream/main
						
set_input_delay	-min $LMS7_IN_MIN_DELAY \
						-clock 	[get_clocks LMS_MCLK2_VIRT] \
									[get_ports {LMS_DIQ2_D[*] LMS_ENABLE_IQSEL2}]
						
=======

set_input_delay	-min $LMS7_IN_MIN_DELAY \
						-clock 	[get_clocks LMS_MCLK2_VIRT] \
									[get_ports {LMS_DIQ2_D[*] LMS_ENABLE_IQSEL2}]

>>>>>>> Revert "enlever le chain de argu"
set_input_delay	-max $LMS7_IN_MAX_DELAY \
						-clock 	[get_clocks LMS_MCLK2_VIRT] \
						-clock_fall \
									[get_ports {LMS_DIQ2_D[*] LMS_ENABLE_IQSEL2}] \
						-add_delay
<<<<<<< refs/remotes/upstream/main
												
=======

>>>>>>> Revert "enlever le chain de argu"
set_input_delay	-min $LMS7_IN_MIN_DELAY \
						-clock 	[get_clocks LMS_MCLK2_VIRT] \
						-clock_fall \
									[get_ports {LMS_DIQ2_D[*] LMS_ENABLE_IQSEL2}] \
						-add_delay
<<<<<<< refs/remotes/upstream/main
						
						
#LMS1 when MCLK2 is 5MHz						
=======


#LMS1 when MCLK2 is 5MHz
>>>>>>> Revert "enlever le chain de argu"
#set_input_delay	-max $LMS7_IN_MAX_DELAY \
#						-clock 	[get_clocks LMS_MCLK1_VIRT] \
#									[get_ports {LMS_DIQ2_D[*] LMS_ENABLE_IQSEL2}] \
#						-add_delay
<<<<<<< refs/remotes/upstream/main
#						
=======
#
>>>>>>> Revert "enlever le chain de argu"
#set_input_delay	-min $LMS7_IN_MIN_DELAY \
#						-clock 	[get_clocks LMS_MCLK1_VIRT] \
#									[get_ports {LMS_DIQ2_D[*] LMS_ENABLE_IQSEL2}] \
#						-add_delay
<<<<<<< refs/remotes/upstream/main
#						
=======
#
>>>>>>> Revert "enlever le chain de argu"
#set_input_delay	-max $LMS7_IN_MAX_DELAY \
#						-clock 	[get_clocks LMS_MCLK1_VIRT] \
#						-clock_fall \
#									[get_ports {LMS_DIQ2_D[*] LMS_ENABLE_IQSEL2}] \
#						-add_delay
<<<<<<< refs/remotes/upstream/main
#												
=======
#
>>>>>>> Revert "enlever le chain de argu"
#set_input_delay	-min $LMS7_IN_MIN_DELAY \
#						-clock 	[get_clocks LMS_MCLK1_VIRT] \
#						-clock_fall \
#									[get_ports {LMS_DIQ2_D[*] LMS_ENABLE_IQSEL2}] \
#						-add_delay
<<<<<<< refs/remotes/upstream/main
						
# ----------------------------------------------------------------------------
#Output constraints
# ----------------------------------------------------------------------------
#LMS1 when MCLK2 is 160MHz				
set_output_delay	-max $LMS_LMS7_Tsu \
						-clock 	[get_clocks LMS_FCLK1] \
									[get_ports {LMS_DIQ1_D[*] LMS_ENABLE_IQSEL1}]
						
set_output_delay	-min -$LMS_LMS7_Th \
						-clock 	[get_clocks LMS_FCLK1] \
									[get_ports {LMS_DIQ1_D[*] LMS_ENABLE_IQSEL1}]						
						
=======

# ----------------------------------------------------------------------------
#Output constraints
# ----------------------------------------------------------------------------
#LMS1 when MCLK2 is 160MHz
set_output_delay	-max $LMS_LMS7_Tsu \
						-clock 	[get_clocks LMS_FCLK1] \
									[get_ports {LMS_DIQ1_D[*] LMS_ENABLE_IQSEL1}]

set_output_delay	-min -$LMS_LMS7_Th \
						-clock 	[get_clocks LMS_FCLK1] \
									[get_ports {LMS_DIQ1_D[*] LMS_ENABLE_IQSEL1}]

>>>>>>> Revert "enlever le chain de argu"
set_output_delay	-max $LMS_LMS7_Tsu \
						-clock 	[get_clocks LMS_FCLK1] \
						-clock_fall \
									[get_ports { LMS_DIQ1_D[*] LMS_ENABLE_IQSEL1}] \
						-add_delay
<<<<<<< refs/remotes/upstream/main
											
=======

>>>>>>> Revert "enlever le chain de argu"
set_output_delay	-min -$LMS_LMS7_Th \
						-clock 	[get_clocks LMS_FCLK1] \
						-clock_fall \
									[get_ports {LMS_DIQ1_D[*] LMS_ENABLE_IQSEL1}] \
						-add_delay
<<<<<<< refs/remotes/upstream/main
												
#LMS1 when MCLK2 is 5MHz						
=======

#LMS1 when MCLK2 is 5MHz
>>>>>>> Revert "enlever le chain de argu"
#set_output_delay	-max $LMS_LMS7_Tsu \
#						-clock 	[get_clocks LMS_FCLK1_DRCT] \
#									[get_ports {LMS_DIQ1[*] LMS_ENABLE_IQSEL1}] \
#						-add_delay
<<<<<<< refs/remotes/upstream/main
#						
=======
#
>>>>>>> Revert "enlever le chain de argu"
#set_output_delay	-min -$LMS_LMS7_Th \
#						-clock 	[get_clocks LMS_FCLK1_DRCT] \
#									[get_ports {LMS_DIQ1[*] LMS_ENABLE_IQSEL1}] \
#						-add_delay
<<<<<<< refs/remotes/upstream/main
#						
=======
#
>>>>>>> Revert "enlever le chain de argu"
#set_output_delay	-max $LMS_LMS7_Tsu \
#						-clock 	[get_clocks LMS_FCLK1_DRCT] \
#						-clock_fall \
#									[get_ports { LMS_DIQ1[*] LMS_ENABLE_IQSEL1}] \
#						-add_delay
<<<<<<< refs/remotes/upstream/main
#											
=======
#
>>>>>>> Revert "enlever le chain de argu"
#set_output_delay	-min -$LMS_LMS7_Th \
#						-clock 	[get_clocks LMS_FCLK1_DRCT] \
#						-clock_fall \
#									[get_ports {LMS_DIQ1[*] LMS_ENABLE_IQSEL1}] \
#						-add_delay

# ----------------------------------------------------------------------------
#Exceptions
<<<<<<< refs/remotes/upstream/main
# ----------------------------------------------------------------------------											
#Between Center aligned different edge transfers in DIQ2 interface 
=======
# ----------------------------------------------------------------------------
#Between Center aligned different edge transfers in DIQ2 interface
>>>>>>> Revert "enlever le chain de argu"
#(when sampling with PLL phase shifted clock >5MHz)
set_false_path -setup 	-fall_from 	[get_clocks LMS_MCLK2_VIRT] -rise_to \
												[get_clocks RX_C3]
set_false_path -setup 	-rise_from 	[get_clocks LMS_MCLK2_VIRT] -fall_to \
												[get_clocks RX_C3]
set_false_path -hold 	-rise_from 	[get_clocks LMS_MCLK2_VIRT] -rise_to \
												[get_clocks RX_C3]
set_false_path -hold 	-fall_from 	[get_clocks LMS_MCLK2_VIRT] -fall_to \
												[get_clocks RX_C3]
<<<<<<< refs/remotes/upstream/main
											
#Between Edge aligned same edge transfers in DIQ2 interface 
#(When sampling with direct LMS_MCLK2 clock <5MHz)												
=======

#Between Edge aligned same edge transfers in DIQ2 interface
#(When sampling with direct LMS_MCLK2 clock <5MHz)
>>>>>>> Revert "enlever le chain de argu"
#set_false_path -setup 	-rise_from 	[get_clocks LMS_MCLK1_VIRT] -rise_to \
#												[get_clocks LMS_MCLK1]
#set_false_path -setup 	-fall_from 	[get_clocks LMS_MCLK1_VIRT] -fall_to \
#												[get_clocks LMS_MCLK1]
#set_false_path -hold 	-rise_from 	[get_clocks LMS_MCLK1_VIRT] -fall_to \
#												[get_clocks LMS_MCLK1]
#set_false_path -hold 	-fall_from 	[get_clocks LMS_MCLK1_VIRT] -rise_to \
#												[get_clocks LMS_MCLK1]

#Between Center aligned same edge transfers in DIQ1 interface
set_false_path -setup 	-rise_from 	[get_clocks TX_C1] -rise_to \
												[get_clocks LMS_FCLK1]
set_false_path -setup 	-fall_from 	[get_clocks TX_C1] -fall_to \
												[get_clocks LMS_FCLK1]
set_false_path -hold 	-rise_from 	[get_clocks TX_C1] -fall_to \
												[get_clocks LMS_FCLK1]
set_false_path -hold 	-fall_from 	[get_clocks TX_C1] -rise_to \
												[get_clocks LMS_FCLK1]
<<<<<<< refs/remotes/upstream/main
												
=======

>>>>>>> Revert "enlever le chain de argu"
#Between Center aligned same edge transfers in DIQ1 interface (When MCLK2 <5MHz)
#set_false_path -setup 	-rise_from 	[get_clocks LMS_MCLK1] -rise_to \
#												[get_clocks LMS_FCLK1_DRCT]
#set_false_path -setup 	-fall_from 	[get_clocks LMS_MCLK1] -fall_to \
#												[get_clocks LMS_FCLK1_DRCT]
#set_false_path -hold 	-rise_from 	[get_clocks LMS_MCLK1] -fall_to \
#												[get_clocks LMS_FCLK1_DRCT]
#set_false_path -hold 	-fall_from 	[get_clocks LMS_MCLK1] -rise_to \
#												[get_clocks LMS_FCLK1_DRCT]

<<<<<<< refs/remotes/upstream/main
#Clock groups					
=======
#Clock groups
>>>>>>> Revert "enlever le chain de argu"
#Other clock groups are set in top .sdc file
# LMS_FCLK1 clock mux
#set_clock_groups -exclusive 	-group {LMS_FCLK1} \
#										-group {LMS_FCLK1_DRCT}
#
<<<<<<< refs/remotes/upstream/main
## LMS_FCLK2 clock mux										
#set_clock_groups -exclusive 	-group {LMS_FCLK2} \
#										-group {LMS_FCLK2_DRCT}

# LMS_MCLK2 clock mux										
set_clock_groups -exclusive 	-group {LMS_MCLK2} \
										-group {LMS_MCLK1}
										
#False Path between PLL output and clock output ports LMS2_FCLK1 an LMS2_FCLK2
set_false_path -to [get_ports LMS_FCLK*]	



=======
## LMS_FCLK2 clock mux
#set_clock_groups -exclusive 	-group {LMS_FCLK2} \
#										-group {LMS_FCLK2_DRCT}

# LMS_MCLK2 clock mux
set_clock_groups -exclusive 	-group {LMS_MCLK2} \
										-group {LMS_MCLK1}

#False Path between PLL output and clock output ports LMS2_FCLK1 an LMS2_FCLK2
set_false_path -to [get_ports LMS_FCLK*]
>>>>>>> Revert "enlever le chain de argu"
