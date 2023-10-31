-- ----------------------------------------------------------------------------
-- FILE:          one_pct_tb.vhd
<<<<<<< refs/remotes/upstream/main
-- DESCRIPTION:   
=======
-- DESCRIPTION:
>>>>>>> Revert "enlever le chain de argu"
-- DATE:          12:22 PM Tuesday, January 15, 2019
-- AUTHOR(s):     Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- NOTES:
-- ----------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity one_pct_tb is
end one_pct_tb;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------

architecture tb_behave of one_pct_tb is
   constant clk0_period    : time := 10 ns;
   constant clk1_period    : time := 62 ns;
<<<<<<< refs/remotes/upstream/main
   
   --signals
   signal clk0,clk1        : std_logic;
   signal reset_n          : std_logic; 
   
   --inst0
   type integer_array is array (0 to 2) of integer;
   constant words_to_write    : integer_array := (6,10,1024);
   signal pct_cnt             : integer := 0; 
=======

   --signals
   signal clk0,clk1        : std_logic;
   signal reset_n          : std_logic;

   --inst0
   type integer_array is array (0 to 2) of integer;
   constant words_to_write    : integer_array := (6,10,1024);
   signal pct_cnt             : integer := 0;
>>>>>>> Revert "enlever le chain de argu"
   signal wr_cnt              : integer := 0;
   signal inst0_wrreq         : std_logic;
   signal inst0_data          : std_logic_vector(31 downto 0);
   signal inst0_rdreq         : std_logic;
   signal inst0_wrempty       : std_logic;
   signal inst0_q             : std_logic_vector(31 downto 0);
   signal inst0_rdempty       : std_logic;
<<<<<<< refs/remotes/upstream/main
   
=======

>>>>>>> Revert "enlever le chain de argu"
   --inst1
   signal inst1_infifo_rdreq  : std_logic;
   signal inst1_pct_wrreq     : std_logic;
   signal inst1_pct_data      : std_logic_vector(31 downto 0);
   signal inst1_pct_rdy       : std_logic;
   signal inst1_pct_header    : std_logic_vector(127 downto 0);
   signal inst1_pct_data_rdempty : std_logic;
   signal inst1_pct_data_rdreq   : std_logic;
   --inst2
   signal inst2_wrempty       : std_logic;
   signal inst2_rdreq         : std_logic;
   signal inst2_rdempty       : std_logic;
<<<<<<< refs/remotes/upstream/main
   
   
   
  
begin 
  
=======




begin

>>>>>>> Revert "enlever le chain de argu"
      clock0: process is
   begin
      clk0 <= '0'; wait for clk0_period/2;
      clk0 <= '1'; wait for clk0_period/2;
   end process clock0;

      clock1: process is
   begin
      clk1 <= '0'; wait for clk1_period/2;
      clk1 <= '1'; wait for clk1_period/2;
   end process clock1;
<<<<<<< refs/remotes/upstream/main
   
=======

>>>>>>> Revert "enlever le chain de argu"
      res: process is
   begin
      reset_n <= '0'; wait for 20 ns;
      reset_n <= '1'; wait;
   end process res;
<<<<<<< refs/remotes/upstream/main
   
   wr_fifo_proc : process is 
=======

   wr_fifo_proc : process is
>>>>>>> Revert "enlever le chain de argu"
   begin
      inst0_wrreq <= '0';
      wait until reset_n = '1';
      for i in 0 to 2 loop
         wait until rising_edge(clk0) AND inst0_wrempty='1';
<<<<<<< refs/remotes/upstream/main
         
=======

>>>>>>> Revert "enlever le chain de argu"
         for j in 0 to words_to_write(i)-1 loop
            inst0_wrreq <= '1';
            wait until rising_edge(clk0);
         end loop;
         inst0_wrreq <= '0';
      end loop;
   end process;
<<<<<<< refs/remotes/upstream/main
   
   wr_cnt_proc : process is 
=======

   wr_cnt_proc : process is
>>>>>>> Revert "enlever le chain de argu"
   begin
      wait until rising_edge(inst0_wrreq);
      wr_cnt <= 0;
      while inst0_wrreq = '1' loop
         wait until rising_edge(clk0);
         wr_cnt <= wr_cnt + 1;
      end loop;
   end process;
<<<<<<< refs/remotes/upstream/main
   
   pct_cnt_proc : process is 
   begin 
=======

   pct_cnt_proc : process is
   begin
>>>>>>> Revert "enlever le chain de argu"
      pct_cnt <= 0;
      loop
      wait until falling_edge(inst0_wrreq);
      pct_cnt <= pct_cnt+1;
<<<<<<< refs/remotes/upstream/main
      if pct_cnt = 5 then 
         exit;
      end if;
      end loop;    
   end process;
   
   data_proc : process (wr_cnt, pct_cnt) 
   begin 
=======
      if pct_cnt = 5 then
         exit;
      end if;
      end loop;
   end process;

   data_proc : process (wr_cnt, pct_cnt)
   begin
>>>>>>> Revert "enlever le chain de argu"
      if wr_cnt = 0 then
         inst0_data <= (others=>'0');
         inst0_data(23 downto 8) <= std_logic_vector(to_unsigned((words_to_write(pct_cnt)-4)*32/8,16));
      elsif wr_cnt = 1 then
         inst0_data <= (others=>'0');
<<<<<<< refs/remotes/upstream/main
      else 
         inst0_data <= std_logic_vector(to_unsigned(wr_cnt,32));
      end if;
   end process;
   
   
   -- Data fifo instance
   inst0_fifo : entity work.fifo_inst   
=======
      else
         inst0_data <= std_logic_vector(to_unsigned(wr_cnt,32));
      end if;
   end process;


   -- Data fifo instance
   inst0_fifo : entity work.fifo_inst
>>>>>>> Revert "enlever le chain de argu"
      generic map(
      dev_family     => "Cyclone IV",
      wrwidth        => 32,
      wrusedw_witdth => 10,
      rdwidth        => 32,
<<<<<<< refs/remotes/upstream/main
      rdusedw_width  => 10,   
=======
      rdusedw_width  => 10,
>>>>>>> Revert "enlever le chain de argu"
      show_ahead     => "OFF"
   )
   port map(
      reset_n     => reset_n,
      wrclk       => clk0,
      wrreq       => inst0_wrreq,
      data        => inst0_data,
      wrfull      => open,
      wrempty     => inst0_wrempty,
      wrusedw     => open,
      rdclk       => clk0,
      rdreq       => inst1_infifo_rdreq,
      q           => inst0_q,
      rdempty     => inst0_rdempty,
<<<<<<< refs/remotes/upstream/main
      rdusedw     => open             
   );
   
   
=======
      rdusedw     => open
   );


>>>>>>> Revert "enlever le chain de argu"
   inst1_one_pct_fifo : entity work.one_pct_fifo
   generic map(
      dev_family              => "Cyclone IV",
      g_INFIFO_DATA_WIDTH     => 32,
      g_PCTFIFO_SIZE          => 4096,
      g_PCTFIFO_RDATA_WIDTH   => 32
   )
<<<<<<< refs/remotes/upstream/main
   port map( 
=======
   port map(
>>>>>>> Revert "enlever le chain de argu"
      clk               => clk0,
      reset_n           => reset_n,
      infifo_rdreq      => inst1_infifo_rdreq,
      infifo_data       => inst0_q,
      infifo_rdempty    => inst0_rdempty,
      pct_rdclk         => clk1,
      pct_aclr_n        => reset_n,
      pct_rdy           => inst1_pct_rdy,
<<<<<<< refs/remotes/upstream/main
      pct_header        => inst1_pct_header, 
=======
      pct_header        => inst1_pct_header,
>>>>>>> Revert "enlever le chain de argu"
      pct_data_rdreq    => inst1_pct_data_rdreq,
      pct_data          => inst1_pct_data,
      pct_data_rdempty  => inst1_pct_data_rdempty
   );
<<<<<<< refs/remotes/upstream/main
   
   
   process is 
=======


   process is
>>>>>>> Revert "enlever le chain de argu"
      variable n :  integer := 0;
   begin
      inst1_pct_data_rdreq <= '0';
      wait until rising_edge(inst1_pct_rdy);
      n := to_integer(unsigned(inst1_pct_header(23 downto 10)));
      for i in 0 to n-1 loop
         inst1_pct_data_rdreq <= '1';
         wait until rising_edge(clk1);
      end loop;
   end process;
<<<<<<< refs/remotes/upstream/main
   

end tb_behave;

=======


end tb_behave;
>>>>>>> Revert "enlever le chain de argu"
