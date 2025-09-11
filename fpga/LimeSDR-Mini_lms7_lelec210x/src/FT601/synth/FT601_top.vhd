-- ----------------------------------------------------------------------------	
-- FILE: 	FT601_top.vhd
-- DESCRIPTION:	top module for FT601
-- DATE:	May 13, 2016
-- AUTHOR(s):	Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------	
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.FIFO_PACK.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity FT601_top is
   generic(
      FT_data_width        : integer := 32;
      FT_be_width          : integer := 4;
      EP02_rdusedw_width   : integer := 11; 
      EP02_rwidth          : integer := 8;
      EP82_wrusedw_width   : integer := 11;
      EP82_wwidth          : integer := 8;
      EP82_wsize           : integer := 64;  --packet size in bytes, has to be multiple of 4 bytes
      EP83_wrusedw_width   : integer := 12;
      EP83_wwidth          : integer := 64;
      EP83_wsize           : integer := 2048 --packet size in bytes, has to be multiple of 4 bytes	
   );
   port (
      --input ports 
      clk            : in std_logic;   --FTDI CLK
      reset_n        : in std_logic;
      --FTDI external ports
      FT_wr_n        : out std_logic;
      FT_rxf_n       : in std_logic;
      FT_data        : inout std_logic_vector(FT_data_width-1 downto 0);
      FT_be          : inout std_logic_vector(FT_be_width-1 downto 0);
      FT_txe_n       : in std_logic;
      --controll endpoint fifo PC->FPGA 
      EP02_rdclk     : in std_logic;
      EP02_rd        : in std_logic;
      EP02_rdata     : out std_logic_vector(EP02_rwidth-1 downto 0);
      EP02_rempty    : out std_logic;
      --controll endpoint fifo FPGA->PC
      EP82_wclk      : in std_logic;
      EP82_aclrn     : in std_logic;
      EP82_wr        : in std_logic;
      EP82_wdata     : in std_logic_vector(EP82_wwidth-1 downto 0);
      EP82_wfull     : out std_logic;
      --stream endpoint fifo FPGA->PC
      EP83_wclk      : in std_logic;
      EP83_aclrn     : in std_logic;
      EP83_wr        : in std_logic;
      EP83_wdata     : in std_logic_vector(EP83_wwidth-1 downto 0);
      EP83_wfull     : out std_logic;
      EP83_wrusedw   : out std_logic_vector(EP83_wrusedw_width-1 downto 0)
   );
end FT601_top;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of FT601_top is
--declare signals,  components here

--EP02 fifo signals 
signal EP02_wrempty        : std_logic;
signal EP02_wr             : std_logic; 
signal EP02_wdata          : std_logic_vector(FT_data_width-1 downto 0);

--EP82 fifo signals
signal EP82_fifo_rdusedw   : std_logic_vector(FIFORD_SIZE(EP82_wwidth, FT_data_width, EP82_wrusedw_width)-1 downto 0);
signal EP82_fifo_q         : std_logic_vector(FT_data_width-1 downto 0);
signal EP82_fifo_rdreq     : std_logic;

--EP83 fifo signals
signal EP83_fifo_rdusedw   : std_logic_vector(FIFORD_SIZE(EP83_wwidth, FT_data_width, EP83_wrusedw_width)-1 downto 0);
signal EP83_fifo_q         : std_logic_vector(FT_data_width-1 downto 0);
signal EP83_fifo_rdreq     : std_logic;

--arbiter signals
signal arb_en              : std_logic; 
signal arb_rd_wr           : std_logic;
signal arb_nth_ch          : std_logic_vector(3 downto 0);

--fsm signals
signal fsm_rdy             : std_logic;
signal fsm_rd_data_valid   : std_logic;
signal fsm_rd_data         : std_logic_vector(FT_data_width-1 downto 0);
signal fsm_wr_data_req     : std_logic;
signal fsm_wr_data         : std_logic_vector(FT_data_width-1 downto 0);
  
begin
   

-- ----------------------------------------------------------------------------
-- FTDI endpoint fifos
-- ----------------------------------------------------------------------------
-- control PC->FPGA 
   EP02_fifo : entity work.fifo_inst   
   generic map(
      dev_family     => "MAX 10",
      wrwidth        => FT_data_width,       --32 bits ftdi side, 
      wrusedw_witdth => FIFOWR_SIZE(FT_data_width, EP02_rwidth, EP02_rdusedw_width),
      rdwidth        => EP02_rwidth,
      rdusedw_width  => EP02_rdusedw_width,  
      show_ahead     => "OFF"
   )
   port map(
      reset_n  => reset_n, 
      wrclk    => clk,
      wrreq    => EP02_wr,
      data     => EP02_wdata,
      wrfull   => open,
      wrempty  => EP02_wrempty,
      wrusedw  => open,
      rdclk    => EP02_rdclk,
      rdreq    => EP02_rd,
      q        => EP02_rdata,
      rdempty  => EP02_rempty,
      rdusedw  => open             
   );

-- control FPGA->PC
   EP82_fifo : entity work.fifo_inst   
   generic map(
      dev_family     => "MAX 10",
      wrwidth        => EP82_wwidth,
      wrusedw_witdth => EP82_wrusedw_width,  --12=2048 words (2048kB)
      rdwidth        => FT_data_width,       --32 bits ftdi side, 
      rdusedw_width  => FIFORD_SIZE(EP82_wwidth, FT_data_width, EP82_wrusedw_width),--EP82_wrusedw_width,
      show_ahead     => "ON"
   )
   port map(
      reset_n  => EP82_aclrn, 
      wrclk    => EP82_wclk,
      wrreq    => EP82_wr,
      data     => EP82_wdata,
      wrfull   => EP82_wfull,
      wrempty  => open,
      wrusedw  => open,
      rdclk    => clk,
      rdreq    => EP82_fifo_rdreq,
      q        => EP82_fifo_q,
      rdempty  => open,
      rdusedw  => EP82_fifo_rdusedw           
   );
   
-- stream FPGA->PC
   EP83_fifo : entity work.fifo_inst   
   generic map(
      dev_family     => "MAX 10",
      wrwidth        => EP83_wwidth,
      wrusedw_witdth => EP83_wrusedw_width,  --12=2024 words x EP83_wwidth (16384KB)
      rdwidth        => FT_data_width,       --32 bits ftdi side, 
      rdusedw_width  => FIFORD_SIZE(EP83_wwidth, FT_data_width, EP83_wrusedw_width),   
      show_ahead     => "ON"
   )
   port map(
      reset_n  => EP83_aclrn, 
      wrclk    => EP83_wclk,
      wrreq    => EP83_wr,
      data     => EP83_wdata,
      wrfull   => EP83_wfull,
      wrempty  => open,
      wrusedw  => EP83_wrusedw,
      rdclk    => clk,
      rdreq    => EP83_fifo_rdreq,
      q        => EP83_fifo_q,
      rdempty  => open,
      rdusedw  => EP83_fifo_rdusedw           
   );
      
-- ----------------------------------------------------------------------------
-- FTDI arbiter
-- ----------------------------------------------------------------------------		
   ftdi_arbiter : entity work.FT601_arb
   generic map(
      FT_data_width     => FT_data_width,
      EP82_fifo_rwidth  => FIFORD_SIZE(EP82_wwidth, FT_data_width, EP82_wrusedw_width),
      EP82_wsize        => EP82_wsize,
      EP83_fifo_rwidth  => FIFORD_SIZE(EP83_wwidth, FT_data_width, EP83_wrusedw_width),
      EP83_wsize        => EP83_wsize
   )
   port map(
      clk               => clk, 
      reset_n           => reset_n,
      enable            => '1',
      EP02_fifo_data    => EP02_wdata, 
      EP02_fifo_wr      => EP02_wr, 
      EP02_fifo_wrempty => EP02_wrempty,
      EP82_fifo_data    => EP82_fifo_q,
      EP82_fifo_rd      => EP82_fifo_rdreq,
      EP82_fifo_rdusedw => EP82_fifo_rdusedw,
      EP83_fifo_data    => EP83_fifo_q,
      EP83_fifo_rd      => EP83_fifo_rdreq,	
      EP83_fifo_rdusedw => EP83_fifo_rdusedw,
      
      fsm_epgo          => arb_en, 
      fsm_rdwr          => arb_rd_wr,
      fsm_ch            => arb_nth_ch, 
      fsm_rdy           => fsm_rdy, 
      fsm_rddata_valid  => fsm_rd_data_valid,
      fsm_rddata        => fsm_rd_data,
      fsm_wrdata_req    => fsm_wr_data_req,
      fsm_wrdata        => fsm_wr_data,
      ep_status         => FT_data(15 downto 8)       
   );

-- ----------------------------------------------------------------------------
-- FTDI fsm 
-- ----------------------------------------------------------------------------		  
   ft_fsm : entity work.FT601
   generic map(
      FT_data_width  => FT_data_width,
      FT_be_width    => FT_be_width,  
      EP82_wsize     => EP82_wsize,
      EP83_wsize     => EP83_wsize 
   )
   port map (
      clk            => clk,
      reset_n        => reset_n,
      trnsf_en       => arb_en,
      ready          => fsm_rdy,
      rd_wr          => arb_rd_wr,
      ch_n           => arb_nth_ch,
      RD_data_valid  => fsm_rd_data_valid, 
      RD_data        => fsm_rd_data,
      WR_data_req    => fsm_wr_data_req,
      WR_data        => fsm_wr_data,  
      wr_n           => FT_wr_n,
      rxf_n          => FT_rxf_n,
      data           => FT_data,
      be             => FT_be,
      txe_n          => FT_txe_n
   );
  
end arch;





