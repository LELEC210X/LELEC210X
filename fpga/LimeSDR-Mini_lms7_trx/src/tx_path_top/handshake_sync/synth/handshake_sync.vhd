<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
-- FILE: 	handshake_sync.vhd
-- DESCRIPTION:	
-- DATE:	April 13, 2017
-- AUTHOR(s):	Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
-- FILE: 	handshake_sync.vhd
-- DESCRIPTION:
-- DATE:	April 13, 2017
-- AUTHOR(s):	Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity handshake_sync is
   port (
      src_clk        : in std_logic;
      src_reset_n    : in std_logic;
      src_in         : in std_logic;
      src_busy       : out std_logic;
<<<<<<< refs/remotes/upstream/main
      
      dst_clk        : in std_logic;
      dst_reset_n    : in std_logic;
      dst_out        : out std_logic     
=======

      dst_clk        : in std_logic;
      dst_reset_n    : in std_logic;
      dst_out        : out std_logic
>>>>>>> Revert "enlever le chain de argu"
        );
end handshake_sync;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of handshake_sync is
--declare signals,  components here

signal src_sync_req              : std_logic;
signal dst_sync_ack              : std_logic;
signal dst_sync_ack_reg          : std_logic;

signal src_sync_req_sync_to_dest : std_logic;
signal dst_sync_ack_sync_to_src  : std_logic;


signal src_in_reg                : std_logic;
signal src_in_hold               : std_logic;
signal src_in_hold_sync_to_dest  : std_logic;
signal src_busy_sync_to_dest     : std_logic;

signal dest_ack                  : std_logic;
signal dest_ack_sync_to_src      : std_logic;

<<<<<<< refs/remotes/upstream/main
  
begin

process(src_clk)
begin 
=======

begin

process(src_clk)
begin
>>>>>>> Revert "enlever le chain de argu"
if (src_clk'event AND src_clk='1') then
   src_in_reg <= src_in;
end if;
end process;

process(src_clk, src_reset_n)
begin
<<<<<<< refs/remotes/upstream/main
   if src_reset_n = '0' then 
      src_in_hold <= '0';
   elsif (src_clk'event AND src_clk='1') then 
      if src_sync_req = '0' then 
=======
   if src_reset_n = '0' then
      src_in_hold <= '0';
   elsif (src_clk'event AND src_clk='1') then
      if src_sync_req = '0' then
>>>>>>> Revert "enlever le chain de argu"
         src_in_hold <= src_in;
      else
         src_in_hold <= src_in_hold;
      end if;
   end if;
end process;

src_busy <= src_sync_req OR dst_sync_ack_sync_to_src;





<<<<<<< refs/remotes/upstream/main
src_sync_reg0 : entity work.sync_reg 
=======
src_sync_reg0 : entity work.sync_reg
>>>>>>> Revert "enlever le chain de argu"
port map(src_clk, src_reset_n, dst_sync_ack, dst_sync_ack_sync_to_src);

process(src_clk, src_reset_n)
begin
<<<<<<< refs/remotes/upstream/main
   if src_reset_n = '0' then 
      src_sync_req <= '0';
   elsif (src_clk'event AND src_clk='1') then
      if (src_in XOR src_in_reg) = '1' then 
         src_sync_req <= '1';
      elsif dst_sync_ack_sync_to_src = '1' then 
=======
   if src_reset_n = '0' then
      src_sync_req <= '0';
   elsif (src_clk'event AND src_clk='1') then
      if (src_in XOR src_in_reg) = '1' then
         src_sync_req <= '1';
      elsif dst_sync_ack_sync_to_src = '1' then
>>>>>>> Revert "enlever le chain de argu"
         src_sync_req <= '0';
      else
         src_sync_req <= src_sync_req;
      end if;
   end if;
end process;

<<<<<<< refs/remotes/upstream/main
dst_sync_reg0 : entity work.sync_reg 
port map(dst_clk, dst_reset_n, src_sync_req, src_sync_req_sync_to_dest);

dst_sync_reg1 : entity work.sync_reg 
=======
dst_sync_reg0 : entity work.sync_reg
port map(dst_clk, dst_reset_n, src_sync_req, src_sync_req_sync_to_dest);

dst_sync_reg1 : entity work.sync_reg
>>>>>>> Revert "enlever le chain de argu"
port map(dst_clk, dst_reset_n, src_in_hold, src_in_hold_sync_to_dest);

process(dst_clk, dst_reset_n)
begin
<<<<<<< refs/remotes/upstream/main
   if dst_reset_n = '0' then 
      dst_sync_ack      <= '0';
      dst_sync_ack_reg  <= '0';
   elsif (dst_clk'event AND dst_clk='1') then
      if src_sync_req_sync_to_dest = '1' then 
         dst_sync_ack <= '1';
      else 
=======
   if dst_reset_n = '0' then
      dst_sync_ack      <= '0';
      dst_sync_ack_reg  <= '0';
   elsif (dst_clk'event AND dst_clk='1') then
      if src_sync_req_sync_to_dest = '1' then
         dst_sync_ack <= '1';
      else
>>>>>>> Revert "enlever le chain de argu"
         dst_sync_ack <= '0';
      end if;
      dst_sync_ack_reg <= dst_sync_ack;
   end if;
end process;


process(dst_clk, dst_reset_n)
begin
<<<<<<< refs/remotes/upstream/main
   if dst_reset_n = '0' then 
      dst_out <= '0';
   elsif (dst_clk'event AND dst_clk='1') then
      if dst_sync_ack_reg = '0' AND dst_sync_ack = '1' then 
         dst_out <= '1';
      else 
=======
   if dst_reset_n = '0' then
      dst_out <= '0';
   elsif (dst_clk'event AND dst_clk='1') then
      if dst_sync_ack_reg = '0' AND dst_sync_ack = '1' then
         dst_out <= '1';
      else
>>>>>>> Revert "enlever le chain de argu"
         dst_out <= '0';
      end if;
   end if;
end process;






<<<<<<< refs/remotes/upstream/main
  
end arch;
=======

end arch;
>>>>>>> Revert "enlever le chain de argu"
