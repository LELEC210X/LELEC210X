<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
-- FILE: 	p2d_wr_fsm_tb.vhd
-- DESCRIPTION:	
-- DATE:	March 31, 2017
-- AUTHOR(s):	Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
-- FILE: 	p2d_wr_fsm_tb.vhd
-- DESCRIPTION:
-- DATE:	March 31, 2017
-- AUTHOR(s):	Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.FIFO_PACK.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity p2d_wr_fsm_tb is
end p2d_wr_fsm_tb;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------

architecture tb_behave of p2d_wr_fsm_tb is
constant clk0_period   : time := 10 ns;
<<<<<<< refs/remotes/upstream/main
constant clk1_period   : time := 48 ns; 
   --signals
signal clk0,clk1		: std_logic;
signal reset_n       : std_logic; 
=======
constant clk1_period   : time := 48 ns;
   --signals
signal clk0,clk1		: std_logic;
signal reset_n       : std_logic;
>>>>>>> Revert "enlever le chain de argu"


constant N_BUFF                  : integer := 4;
constant C_PACKET_SIZE           : integer := 48;



<<<<<<< refs/remotes/upstream/main
-- 
=======
--
>>>>>>> Revert "enlever le chain de argu"
constant C_PCT_WR_WIDTH          : integer := 32;
constant C_PCT_RD_WIDTH          : integer := 128;
constant C_PCT_FIFO_SIZE         : integer := 4096; -- packet FIFO size in bytes
constant C_PCT_WRUSEDW_WIDTH     : integer := FIFO_WORDS_TO_Nbits((C_PCT_FIFO_SIZE*8)/C_PCT_WR_WIDTH, true);
<<<<<<< refs/remotes/upstream/main
constant C_PCT_RDUSEDW_WIDTH     : integer := FIFORD_SIZE(C_PCT_WR_WIDTH, C_PCT_RD_WIDTH, C_PCT_WRUSEDW_WIDTH); 

constant C_PACKET_WORDS          : integer := (C_PACKET_SIZE*8)/C_PCT_WR_WIDTH;

   
--dut0 signals
signal dut0_wrreq                : std_logic;  
signal dut0_data                 : std_logic_vector(C_PCT_WR_WIDTH-1 downto 0);
signal dut0_wrempty              : std_logic;
  
=======
constant C_PCT_RDUSEDW_WIDTH     : integer := FIFORD_SIZE(C_PCT_WR_WIDTH, C_PCT_RD_WIDTH, C_PCT_WRUSEDW_WIDTH);

constant C_PACKET_WORDS          : integer := (C_PACKET_SIZE*8)/C_PCT_WR_WIDTH;


--dut0 signals
signal dut0_wrreq                : std_logic;
signal dut0_data                 : std_logic_vector(C_PCT_WR_WIDTH-1 downto 0);
signal dut0_wrempty              : std_logic;

>>>>>>> Revert "enlever le chain de argu"
--dut1
signal dut1_in_pct_rdy           : std_logic;
signal dut1_pct_size             : std_logic_vector(15 downto 0) := std_logic_vector(to_unsigned((C_PACKET_SIZE*8)/C_PCT_RD_WIDTH,16));
signal dut1_in_pct_rdreq         : std_logic;
signal dut1_pct_data_wrreq       : std_logic_vector(N_BUFF-1 downto 0);
signal dut1_pct_buff_rdy         : std_logic_vector(N_BUFF-1 downto 0) := "1111";
<<<<<<< refs/remotes/upstream/main
   
signal dut0_q                    : std_logic_vector(C_PCT_RD_WIDTH-1 downto 0);
signal dut0_rdusedw              : std_logic_vector(C_PCT_RDUSEDW_WIDTH-1 downto 0);
   
  

begin 
  
=======

signal dut0_q                    : std_logic_vector(C_PCT_RD_WIDTH-1 downto 0);
signal dut0_rdusedw              : std_logic_vector(C_PCT_RDUSEDW_WIDTH-1 downto 0);



begin

>>>>>>> Revert "enlever le chain de argu"
      clock0: process is
	begin
		clk0 <= '0'; wait for clk0_period/2;
		clk0 <= '1'; wait for clk0_period/2;
	end process clock0;

   	clock: process is
	begin
		clk1 <= '0'; wait for clk1_period/2;
		clk1 <= '1'; wait for clk1_period/2;
	end process clock;
<<<<<<< refs/remotes/upstream/main
	
=======

>>>>>>> Revert "enlever le chain de argu"
		res: process is
	begin
		reset_n <= '0'; wait for 20 ns;
		reset_n <= '1'; wait;
	end process res;
<<<<<<< refs/remotes/upstream/main
   
   process is 
   begin
      dut0_wrreq <= '0';
      wait until rising_edge(clk0) AND reset_n = '1';
         if dut0_wrempty = '1' then 
            for i in 0 to C_PACKET_WORDS loop 
=======

   process is
   begin
      dut0_wrreq <= '0';
      wait until rising_edge(clk0) AND reset_n = '1';
         if dut0_wrempty = '1' then
            for i in 0 to C_PACKET_WORDS loop
>>>>>>> Revert "enlever le chain de argu"
               wait until rising_edge(clk0);
               dut0_wrreq <= '1';
            end loop;
         end if;
<<<<<<< refs/remotes/upstream/main
      
   end process;
   
   proc_name : process(clk0, reset_n)
   begin
      if reset_n = '0' then 
         dut0_data <= (others=>'0');
      elsif (clk0'event AND clk0='1') then 
         if dut0_wrreq = '1' then 
            dut0_data <= std_logic_vector(unsigned(dut0_data)+1);
         else 
=======

   end process;

   proc_name : process(clk0, reset_n)
   begin
      if reset_n = '0' then
         dut0_data <= (others=>'0');
      elsif (clk0'event AND clk0='1') then
         if dut0_wrreq = '1' then
            dut0_data <= std_logic_vector(unsigned(dut0_data)+1);
         else
>>>>>>> Revert "enlever le chain de argu"
            dut0_data <= (others=>'0');
         end if;
      end if;
   end process;
<<<<<<< refs/remotes/upstream/main
    
    
    
=======



>>>>>>> Revert "enlever le chain de argu"
   dut0_fifo_inst : entity work.fifo_inst
   generic map(
      dev_family     => "Cyclone IV E",
      wrwidth        => C_PCT_WR_WIDTH,
<<<<<<< refs/remotes/upstream/main
      wrusedw_witdth => C_PCT_WRUSEDW_WIDTH, 
      rdwidth        => C_PCT_RD_WIDTH,
      rdusedw_width  => C_PCT_RDUSEDW_WIDTH,
      show_ahead     => "OFF"
   )  
  port map(
      --input ports 
=======
      wrusedw_witdth => C_PCT_WRUSEDW_WIDTH,
      rdwidth        => C_PCT_RD_WIDTH,
      rdusedw_width  => C_PCT_RDUSEDW_WIDTH,
      show_ahead     => "OFF"
   )
  port map(
      --input ports
>>>>>>> Revert "enlever le chain de argu"
      reset_n  => reset_n,
      wrclk    => clk0,
      wrreq    => dut0_wrreq,
      data     => dut0_data,
      wrfull   => open,
      wrempty  => dut0_wrempty,
      wrusedw  => open,
      rdclk    => clk1,
      rdreq    => dut1_in_pct_rdreq,
      q        => dut0_q,
      rdempty  => open,
      rdusedw  => dut0_rdusedw
   );
<<<<<<< refs/remotes/upstream/main
   
   dut1_in_pct_rdy <= '1' when unsigned(dut0_rdusedw) = (C_PACKET_SIZE*8)/C_PCT_RD_WIDTH else '0';
 

  
=======

   dut1_in_pct_rdy <= '1' when unsigned(dut0_rdusedw) = (C_PACKET_SIZE*8)/C_PCT_RD_WIDTH else '0';



>>>>>>> Revert "enlever le chain de argu"
  p2d_wr_fsm_dut1 : entity work.p2d_wr_fsm
   generic map(
      N_BUFF            => N_BUFF,
      PCT_SIZE          => C_PACKET_SIZE
   )
   port map(
      clk               => clk1,
      reset_n           => reset_n,
<<<<<<< refs/remotes/upstream/main
      
=======

>>>>>>> Revert "enlever le chain de argu"
      in_pct_rdreq      => dut1_in_pct_rdreq,
      in_pct_data       => dut0_q,
      in_pct_rdy        => dut1_in_pct_rdy,

      pct_hdr_0         => open,
      pct_hdr_0_valid   => open,

      pct_hdr_1         => open,
      pct_hdr_1_valid   => open,
<<<<<<< refs/remotes/upstream/main
      
      pct_data          => open,
      pct_data_wrreq    => dut1_pct_data_wrreq,
      
      pct_buff_rdy      => dut1_pct_buff_rdy
      );
      
   gen : for i in 0 to N_BUFF-1 generate
      process 
=======

      pct_data          => open,
      pct_data_wrreq    => dut1_pct_data_wrreq,

      pct_buff_rdy      => dut1_pct_buff_rdy
      );

   gen : for i in 0 to N_BUFF-1 generate
      process
>>>>>>> Revert "enlever le chain de argu"
      begin
         wait until rising_edge(dut1_pct_data_wrreq(i));
         dut1_pct_buff_rdy(i) <= not dut1_pct_buff_rdy(i);
      end process;
   end generate gen;
<<<<<<< refs/remotes/upstream/main
      
	end tb_behave;
  
  


  
=======

	end tb_behave;
>>>>>>> Revert "enlever le chain de argu"
