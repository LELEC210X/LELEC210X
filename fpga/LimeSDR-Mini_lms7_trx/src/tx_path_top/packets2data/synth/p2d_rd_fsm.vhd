<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
-- FILE:          p2d_rd_fsm.vhd
-- DESCRIPTION:   FSM for data reading from packets.
-- DATE:          April 6, 2017
-- AUTHOR(s):     Lime Microsystems
-- REVISIONS:
<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"

-- ----------------------------------------------------------------------------
-- Notes:
-- ----------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity p2d_rd_fsm is
   generic (
      pct_size_w           : integer := 16;
      n_buff               : integer := 2 -- 2,4 valid values
   );
   port (
      clk                  : in std_logic;
      reset_n              : in std_logic;
<<<<<<< refs/remotes/upstream/main
      pct_size             : in std_logic_vector(pct_size_w-1 downto 0);   --Whole packet size in 
                                                                           --in_pct_data_w words
     
=======
      pct_size             : in std_logic_vector(pct_size_w-1 downto 0);   --Whole packet size in
                                                                           --in_pct_data_w words

>>>>>>> Revert "enlever le chain de argu"
      pct_data_buff_full   : in std_logic;
      pct_data_rdreq       : out std_logic_vector(n_buff-1 downto 0);
      pct_data_rdstate     : out std_logic_vector(n_buff-1 downto 0);

      pct_buff_rdy         : in std_logic_vector(n_buff-1 downto 0);   --assert only one bit at the same time
<<<<<<< refs/remotes/upstream/main
      
      rd_fsm_rdy           : out std_logic; -- status of FSM
      rd_fsm_rd_done       : out std_logic
      
=======

      rd_fsm_rdy           : out std_logic; -- status of FSM
      rd_fsm_rd_done       : out std_logic

>>>>>>> Revert "enlever le chain de argu"
        );
end p2d_rd_fsm;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of p2d_rd_fsm is
--declare signals,  components here

type state_type is (idle, sel_buff, rd_buff, rd_hold, rd_done);
<<<<<<< refs/remotes/upstream/main
signal current_state, next_state : state_type;   
=======
signal current_state, next_state : state_type;
>>>>>>> Revert "enlever le chain de argu"

signal pct_buff_rdy_int    : std_logic;
signal pct_buff_sel        : std_logic_vector(n_buff-1 downto 0);

<<<<<<< refs/remotes/upstream/main
signal pct_size_rd_limit   : unsigned(pct_size_w-1 downto 0); 
=======
signal pct_size_rd_limit   : unsigned(pct_size_w-1 downto 0);
>>>>>>> Revert "enlever le chain de argu"
signal rd_cnt              : unsigned(pct_size_w-1 downto 0);

signal rd_sig              : std_logic;



begin

-- ----------------------------------------------------------------------------
-- To know when to terminate read process
-- ----------------------------------------------------------------------------
process(clk, reset_n)
begin
<<<<<<< refs/remotes/upstream/main
   if reset_n = '0' then 
      pct_size_rd_limit <= (others=>'0');
   elsif (clk'event AND clk='1') then 
=======
   if reset_n = '0' then
      pct_size_rd_limit <= (others=>'0');
   elsif (clk'event AND clk='1') then
>>>>>>> Revert "enlever le chain de argu"
      pct_size_rd_limit <= unsigned(pct_size) - 1;
   end if;
end process;

-- ----------------------------------------------------------------------------
-- Read counter
-- ----------------------------------------------------------------------------
process(clk, reset_n)
begin
<<<<<<< refs/remotes/upstream/main
   if reset_n = '0' then 
      rd_cnt <= (others=>'0');
   elsif (clk'event AND clk='1') then
      if current_state = rd_buff OR current_state = rd_hold then 
         if rd_sig = '1' then
            rd_cnt <= rd_cnt + 1;
         else 
            rd_cnt <= rd_cnt;
         end if;
      else 
=======
   if reset_n = '0' then
      rd_cnt <= (others=>'0');
   elsif (clk'event AND clk='1') then
      if current_state = rd_buff OR current_state = rd_hold then
         if rd_sig = '1' then
            rd_cnt <= rd_cnt + 1;
         else
            rd_cnt <= rd_cnt;
         end if;
      else
>>>>>>> Revert "enlever le chain de argu"
         rd_cnt <= (others=>'0');
      end if;
   end if;
end process;



-- ----------------------------------------------------------------------------
-- To select buffer from which to read
-- ----------------------------------------------------------------------------
in_reg0 : process(clk, reset_n)
begin
<<<<<<< refs/remotes/upstream/main
   if reset_n = '0' then 
      pct_buff_sel <= (others=>'0');
   elsif (clk'event AND clk='1') then 
      if pct_buff_rdy_int = '1' AND current_state= idle then 
         pct_buff_sel <= pct_buff_rdy;
      else 
=======
   if reset_n = '0' then
      pct_buff_sel <= (others=>'0');
   elsif (clk'event AND clk='1') then
      if pct_buff_rdy_int = '1' AND current_state= idle then
         pct_buff_sel <= pct_buff_rdy;
      else
>>>>>>> Revert "enlever le chain de argu"
         pct_buff_sel <= pct_buff_sel;
      end if;
   end if;
end process;

-- ----------------------------------------------------------------------------
-- To know that at least one buffer is ready
-- ----------------------------------------------------------------------------
process(pct_buff_rdy)
<<<<<<< refs/remotes/upstream/main
begin 
   if unsigned(pct_buff_rdy) > 0 then 
      pct_buff_rdy_int <= '1';
   else 
=======
begin
   if unsigned(pct_buff_rdy) > 0 then
      pct_buff_rdy_int <= '1';
   else
>>>>>>> Revert "enlever le chain de argu"
      pct_buff_rdy_int <= '0';
   end if;
end process;

-- ----------------------------------------------------------------------------
--state machine
-- ----------------------------------------------------------------------------
fsm_f : process(clk, reset_n)
begin
   if(reset_n = '0')then
      current_state <= idle;
   elsif(clk'event and clk = '1')then
      current_state <= next_state;
   end if;
end process;

-- ----------------------------------------------------------------------------
--state machine combo
-- ----------------------------------------------------------------------------
fsm : process(current_state, pct_buff_rdy_int, pct_data_buff_full, rd_cnt, pct_size_rd_limit) begin
   next_state <= current_state;
   case current_state is
<<<<<<< refs/remotes/upstream/main
   
      when idle =>
         if pct_buff_rdy_int = '1'  AND pct_data_buff_full = '0' then 
            next_state <= rd_buff;
         else 
            next_state <= idle;
         end if;
         
      when rd_buff => 
         if rd_cnt < pct_size_rd_limit then
            if pct_data_buff_full = '1' then 
               next_state <= rd_hold; 
            else 
=======

      when idle =>
         if pct_buff_rdy_int = '1'  AND pct_data_buff_full = '0' then
            next_state <= rd_buff;
         else
            next_state <= idle;
         end if;

      when rd_buff =>
         if rd_cnt < pct_size_rd_limit then
            if pct_data_buff_full = '1' then
               next_state <= rd_hold;
            else
>>>>>>> Revert "enlever le chain de argu"
               next_state <= rd_buff;
            end if;
         else
            next_state <= rd_done;
<<<<<<< refs/remotes/upstream/main
         end if; 
         
      when rd_hold => 
         if pct_data_buff_full = '1' then 
            next_state <= rd_hold; 
         else 
            next_state <= rd_buff;
         end if;         
         
      when rd_done => 
         next_state <= idle;
     
      when others => 
=======
         end if;

      when rd_hold =>
         if pct_data_buff_full = '1' then
            next_state <= rd_hold;
         else
            next_state <= rd_buff;
         end if;

      when rd_done =>
         next_state <= idle;

      when others =>
>>>>>>> Revert "enlever le chain de argu"
         next_state <= idle;
   end case;
end process;

-- ----------------------------------------------------------------------------
--Read signal register
-- ----------------------------------------------------------------------------
process (current_state)
<<<<<<< refs/remotes/upstream/main
begin 
   if current_state = rd_buff then 
      rd_sig <= '1';
      pct_data_rdreq <= pct_buff_sel;
   else 
=======
begin
   if current_state = rd_buff then
      rd_sig <= '1';
      pct_data_rdreq <= pct_buff_sel;
   else
>>>>>>> Revert "enlever le chain de argu"
      rd_sig <= '0';
      pct_data_rdreq <= (others =>'0');
   end if;
end process;

out_reg2 : process(clk, reset_n)
begin
<<<<<<< refs/remotes/upstream/main
   if reset_n = '0' then 
      pct_data_rdstate <= (others=>'0');
   elsif (clk'event AND clk='1') then 
      if current_state = idle then 
         pct_data_rdstate <= (others=>'0');
      else 
         pct_data_rdstate <= pct_buff_sel;         
=======
   if reset_n = '0' then
      pct_data_rdstate <= (others=>'0');
   elsif (clk'event AND clk='1') then
      if current_state = idle then
         pct_data_rdstate <= (others=>'0');
      else
         pct_data_rdstate <= pct_buff_sel;
>>>>>>> Revert "enlever le chain de argu"
      end if;
   end if;
end process;


<<<<<<< refs/remotes/upstream/main
process(current_state, pct_data_buff_full) 
begin 
   if current_state = idle AND pct_data_buff_full = '0' then 
      rd_fsm_rdy <= '1';
   else 
=======
process(current_state, pct_data_buff_full)
begin
   if current_state = idle AND pct_data_buff_full = '0' then
      rd_fsm_rdy <= '1';
   else
>>>>>>> Revert "enlever le chain de argu"
      rd_fsm_rdy <= '0';
   end if;
end process;

<<<<<<< refs/remotes/upstream/main
process(current_state) 
begin 
   if current_state = rd_done then 
      rd_fsm_rd_done <= '1';
   else 
=======
process(current_state)
begin
   if current_state = rd_done then
      rd_fsm_rd_done <= '1';
   else
>>>>>>> Revert "enlever le chain de argu"
      rd_fsm_rd_done <= '0';
   end if;
end process;




<<<<<<< refs/remotes/upstream/main
end arch;   

=======
end arch;
>>>>>>> Revert "enlever le chain de argu"
