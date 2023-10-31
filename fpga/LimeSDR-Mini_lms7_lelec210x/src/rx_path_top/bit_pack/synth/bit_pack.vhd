-- ----------------------------------------------------------------------------
-- FILE:     bit_pack.vhd
-- DESCRIPTION:    packs data from 12 or 14 bit samples to 16 bit data
-- DATE:    Nov 15, 2016
-- AUTHOR(s):    Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity bit_pack is

  port (
<<<<<<< refs/remotes/upstream/main
        --input ports 
=======
        --input ports
>>>>>>> Revert "enlever le chain de argu"
        clk             : in std_logic;
        reset_n         : in std_logic;
        data_in         : in std_logic_vector(63 downto 0);
        data_in_valid   : in std_logic;
        sample_width    : in std_logic_vector(1 downto 0); --"10"-12bit, "01"-14bit, "00"-16bit;
<<<<<<< refs/remotes/upstream/main
        --output ports 
        data_out        : out std_logic_vector(63 downto 0);
        data_out_valid  : out std_logic       
=======
        --output ports
        data_out        : out std_logic_vector(63 downto 0);
        data_out_valid  : out std_logic
>>>>>>> Revert "enlever le chain de argu"
        );
end bit_pack;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of bit_pack is
--Declare signals,  components here


--inst0 signals
signal inst0_data64_out       : std_logic_vector(63 downto 0);
signal inst0_data48_in        : std_logic_vector(47 downto 0);
signal inst0_data_out_valid   : std_logic;

--inst1 signals
signal inst1_data64_out       : std_logic_vector(63 downto 0);
signal inst1_data56_in        : std_logic_vector(55 downto 0);
signal inst1_data_out_valid   : std_logic;

--mux signals
signal mux0_data64            : std_logic_vector(63 downto 0);
signal mux0_data_out_valid    : std_logic;
signal mux0_sel               : std_logic;

signal mux0_data64_reg        : std_logic_vector(63 downto 0);
signal mux0_data_out_valid_reg: std_logic;

--mux signals
signal mux1_data64            : std_logic_vector(63 downto 0);
signal mux1_data_out_valid    : std_logic;
signal mux1_sel               : std_logic;

signal mux1_data64_reg        : std_logic_vector(63 downto 0);
signal mux1_data_out_valid_reg: std_logic;



component pack_48_to_64 is
  port (
<<<<<<< refs/remotes/upstream/main
      --input ports 
=======
      --input ports
>>>>>>> Revert "enlever le chain de argu"
      clk               : in std_logic;
      reset_n           : in std_logic;
      data_in_wrreq     : in std_logic;
      data48_in         : in std_logic_vector(47 downto 0);
      data64_out        : out std_logic_vector(63 downto 0);
<<<<<<< refs/remotes/upstream/main
      data_out_valid    : out std_logic       
=======
      data_out_valid    : out std_logic
>>>>>>> Revert "enlever le chain de argu"
        );
end component;


component pack_56_to_64 is
  port (
<<<<<<< refs/remotes/upstream/main
      --input ports 
=======
      --input ports
>>>>>>> Revert "enlever le chain de argu"
      clk               : in std_logic;
      reset_n           : in std_logic;
      data_in_wrreq     : in std_logic;
      data56_in         : in std_logic_vector(55 downto 0);
      data64_out        : out std_logic_vector(63 downto 0);
<<<<<<< refs/remotes/upstream/main
      data_out_valid    : out std_logic       
        );
end component;
  
=======
      data_out_valid    : out std_logic
        );
end component;

>>>>>>> Revert "enlever le chain de argu"
begin


-- ----------------------------------------------------------------------------
-- Component instances
-- ----------------------------------------------------------------------------

<<<<<<< refs/remotes/upstream/main
inst0_data48_in <=   data_in(63 downto 52) & 
=======
inst0_data48_in <=   data_in(63 downto 52) &
>>>>>>> Revert "enlever le chain de argu"
                     data_in(47 downto 36) &
                     data_in(31 downto 20) &
                     data_in(15 downto 4);

<<<<<<< refs/remotes/upstream/main
inst0 : pack_48_to_64 
=======
inst0 : pack_48_to_64
>>>>>>> Revert "enlever le chain de argu"
port map (
      clk               => clk,
      reset_n           => reset_n,
      data_in_wrreq     => data_in_valid,
      data48_in         => inst0_data48_in,
      data64_out        => inst0_data64_out,
      data_out_valid    => inst0_data_out_valid
);

inst1_data56_in <=   data_in(63 downto 50) &
<<<<<<< refs/remotes/upstream/main
                     data_in(47 downto 34) & 
                     data_in(31 downto 18) & 
                     data_in(15 downto 2);

inst1 : pack_56_to_64 
=======
                     data_in(47 downto 34) &
                     data_in(31 downto 18) &
                     data_in(15 downto 2);

inst1 : pack_56_to_64
>>>>>>> Revert "enlever le chain de argu"
port map (
      clk            => clk,
      reset_n        => reset_n,
      data_in_wrreq  => data_in_valid,
      data56_in      => inst1_data56_in,
      data64_out     => inst1_data64_out,
      data_out_valid => inst1_data_out_valid
);

-- ----------------------------------------------------------------------------
<<<<<<< refs/remotes/upstream/main
-- MUX 0 
=======
-- MUX 0
>>>>>>> Revert "enlever le chain de argu"
-- ----------------------------------------------------------------------------

mux0_sel                <= sample_width(1);

<<<<<<< refs/remotes/upstream/main
mux0_data64             <= inst0_data64_out when mux0_sel='1' else 
                        inst1_data64_out;
               
mux0_data_out_valid     <= inst0_data_out_valid when mux0_sel='1' else 
=======
mux0_data64             <= inst0_data64_out when mux0_sel='1' else
                        inst1_data64_out;

mux0_data_out_valid     <= inst0_data_out_valid when mux0_sel='1' else
>>>>>>> Revert "enlever le chain de argu"
                        inst1_data_out_valid;

-- ----------------------------------------------------------------------------
-- MUX 0 registers
-- ----------------------------------------------------------------------------
process(clk, reset_n)
<<<<<<< refs/remotes/upstream/main
begin 
   if reset_n = '0' then 
      mux0_data64_reg         <= (others=> '0');
      mux0_data_out_valid_reg <= '0';
   elsif (clk'event AND clk = '1') then 
=======
begin
   if reset_n = '0' then
      mux0_data64_reg         <= (others=> '0');
      mux0_data_out_valid_reg <= '0';
   elsif (clk'event AND clk = '1') then
>>>>>>> Revert "enlever le chain de argu"
      mux0_data64_reg         <= mux0_data64;
      mux0_data_out_valid_reg <= mux0_data_out_valid;
   end if;
end process;

-- ----------------------------------------------------------------------------
<<<<<<< refs/remotes/upstream/main
-- MUX 1 
-- ----------------------------------------------------------------------------
mux1_sel                <= sample_width(1) OR sample_width(0);

mux1_data64             <= mux0_data64_reg         when mux1_sel='1' else 
                        data_in;

mux1_data_out_valid     <= mux0_data_out_valid_reg when mux1_sel='1' else 
=======
-- MUX 1
-- ----------------------------------------------------------------------------
mux1_sel                <= sample_width(1) OR sample_width(0);

mux1_data64             <= mux0_data64_reg         when mux1_sel='1' else
                        data_in;

mux1_data_out_valid     <= mux0_data_out_valid_reg when mux1_sel='1' else
>>>>>>> Revert "enlever le chain de argu"
                        data_in_valid;

-- ----------------------------------------------------------------------------
-- MUX 1 registers
<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------                                    
process(clk, reset_n)
begin 
   if reset_n = '0' then 
      mux1_data64_reg         <= (others=> '0');
      mux1_data_out_valid_reg <= '0';
   elsif (clk'event AND clk = '1') then 
=======
-- ----------------------------------------------------------------------------
process(clk, reset_n)
begin
   if reset_n = '0' then
      mux1_data64_reg         <= (others=> '0');
      mux1_data_out_valid_reg <= '0';
   elsif (clk'event AND clk = '1') then
>>>>>>> Revert "enlever le chain de argu"
      mux1_data64_reg         <= mux1_data64;
      mux1_data_out_valid_reg <= mux1_data_out_valid;
   end if;
end process;

-- ----------------------------------------------------------------------------
-- Registers to output ports
-- ----------------------------------------------------------------------------

data_out       <= mux1_data64_reg;
data_out_valid <= mux1_data_out_valid_reg;




<<<<<<< refs/remotes/upstream/main
end arch;   

=======
end arch;
>>>>>>> Revert "enlever le chain de argu"
