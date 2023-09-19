-- ----------------------------------------------------------------------------	
-- FILE:    rx_path_top.vhd
-- DESCRIPTION:   describe file
-- DATE: March 27, 2017
-- AUTHOR(s):  Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------	
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity rx_path_top is
   generic( 
      dev_family           : string := "Cyclone IV E";
      iq_width             : integer := 12;
      invert_input_clocks  : string := "OFF";
      smpl_buff_rdusedw_w  : integer := 11; --bus width in bits 
      pct_buff_wrusedw_w   : integer := 12  --bus width in bits 
      );
   port (
      clk                  : in std_logic;
      reset_n              : in std_logic;
      test_ptrn_en         : in std_logic;
      --Mode settings
      sample_width         : in std_logic_vector(1 downto 0); --"10"-12bit, "01"-14bit, "00"-16bit;
      mode                 : in std_logic; -- JESD207: 1; TRXIQ: 0
      trxiqpulse           : in std_logic; -- trxiqpulse on: 1; trxiqpulse off: 0
      ddr_en               : in std_logic; -- DDR: 1; SDR: 0
      mimo_en              : in std_logic; -- SISO: 1; MIMO: 0
      ch_en                : in std_logic_vector(1 downto 0); --"01" - Ch. A, "10" - Ch. B, "11" - Ch. A and Ch. B. 
      fidm                 : in std_logic; -- External Frame ID mode. Frame start at fsync = 0, when 0. Frame start at fsync = 1, when 1.
		--DSP settings
		dspcfg_preamble_en     : in  std_logic  := 'X'; -- dspcfg_preamble_en
		dspcfg_FILTER_LEN      : in  std_logic_vector(5 downto 0)  := (others => 'X'); -- dspcfg_FILTER_LEN
      dspcfg_PASSTHROUGH_LEN : in  std_logic_vector(15 downto 0) := (others => 'X'); -- dspcfg_PASSTHROUGH_LEN
      dspcfg_THRESHOLD       : in  std_logic_vector(31 downto 0) := (others => 'X'); -- dspcfg_THRESHOLD
      dspcfg_sum             : out std_logic_vector(31 downto 0) := (others => 'X'); -- dspcfg_sum
      dspcfg_count           : out std_logic_vector(31 downto 0) := (others => 'X'); -- dspcfg_count
      --Rx interface data 
      DIQ                  : in std_logic_vector(iq_width-1 downto 0);
      fsync                : in std_logic;
      --samples
      smpl_fifo_wrreq_out  : out std_logic;
      --Packet fifo ports 
      pct_fifo_wusedw      : in std_logic_vector(pct_buff_wrusedw_w-1 downto 0);
      pct_fifo_wrreq       : out std_logic;
      pct_fifo_wdata       : out std_logic_vector(63 downto 0);
      pct_hdr_cap          : out std_logic;
      --sample nr
      clr_smpl_nr          : in std_logic;
      ld_smpl_nr           : in std_logic;
      smpl_nr_in           : in std_logic_vector(63 downto 0);
      --sample compare
      smpl_cmp_start       : in std_logic;
      smpl_cmp_length      : in std_logic_vector(15 downto 0);
      smpl_cmp_done        : out std_logic;
      smpl_cmp_err         : out std_logic
     
   );
end rx_path_top;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of rx_path_top is
--declare signals,  components here


--sync registers
signal test_ptrn_en_sync      : std_logic;
signal reset_n_sync           : std_logic;
signal sample_width_sync      : std_logic_vector(1 downto 0); 
signal mode_sync              : std_logic;
signal trxiqpulse_sync        : std_logic; 
signal ddr_en_sync            : std_logic; 
signal mimo_en_sync           : std_logic;
signal ch_en_sync             : std_logic_vector(1 downto 0);
signal fidm_sync              : std_logic;
signal clr_smpl_nr_sync       : std_logic;
signal ld_smpl_nr_sync        : std_logic;
signal smpl_nr_in_sync        : std_logic_vector(63 downto 0);	

signal smpl_cmp_start_sync    : std_logic;
signal smpl_cmp_length_sync   : std_logic_vector(15 downto 0);



--inst0 
signal inst0_fifo_wrreq       : std_logic;
signal inst0_fifo_wdata       : std_logic_vector(iq_width*4-1 downto 0);
--inst11 
signal inst11_fifo_wrreq      : std_logic;
signal inst11_fifo_wdata      : std_logic_vector(iq_width*4-1 downto 0);
--inst1
signal inst1_wrfull           : std_logic;
signal inst1_q                : std_logic_vector(iq_width*4-1 downto 0);
signal inst1_rdusedw          : std_logic_vector(smpl_buff_rdusedw_w-1 downto 0);
--inst2
signal inst2_pct_hdr_0        : std_logic_vector(63 downto 0);
signal inst2_pct_hdr_1        : std_logic_vector(63 downto 0);
signal inst2_smpl_buff_rdreq  : std_logic;
signal inst2_smpl_buff_rddata : std_logic_vector(63 downto 0);
--inst3
signal inst3_q                : std_logic_vector(63 downto 0);

--internal signals
type my_array is array (0 to 5) of std_logic_vector(63 downto 0);
signal delay_chain   : my_array;

signal tx_pct_loss_detect     : std_logic;



component lms_dsp is
  port (
		clk_clk                             : in  std_logic                     := 'X';             -- clk
      preamble_detect_cfg_enable          : in  std_logic                     := 'X';             -- dspcfg_enable
		preamble_detect_cfg_FILTER_LEN      : in  std_logic_vector(5 downto 0)  := (others => 'X'); -- dspcfg_FILTER_LEN
      preamble_detect_cfg_PASSTHROUGH_LEN : in  std_logic_vector(15 downto 0) := (others => 'X'); -- dspcfg_PASSTHROUGH_LEN
      preamble_detect_cfg_THRESHOLD       : in  std_logic_vector(31 downto 0) := (others => 'X'); -- dspcfg_THRESHOLD
      preamble_detect_debug_sum           : out std_logic_vector(31 downto 0) := (others => 'X'); -- dspcfg_sum
      preamble_detect_debug_count         : out std_logic_vector(31 downto 0) := (others => 'X'); -- dspcfg_count
		fifo_in_wdata                       : in  std_logic_vector(47 downto 0) := (others => 'X'); -- wdata
		fifo_in_wrreq                       : in  std_logic                     := 'X';             -- wrreq
		fifo_out_wrdata                     : out std_logic_vector(47 downto 0);                    -- wrdata
		fifo_out_wrreq                      : out std_logic;                                        -- wrreq
		reset_reset_n                       : in  std_logic                     := 'X'              -- reset_n
  );
end component lms_dsp;


begin


sync_reg0 : entity work.sync_reg 
port map(clk, '1', reset_n, reset_n_sync);

sync_reg3 : entity work.sync_reg 
port map(clk, '1', mode, mode_sync);

sync_reg4 : entity work.sync_reg 
port map(clk, '1', trxiqpulse, trxiqpulse_sync);

sync_reg5 : entity work.sync_reg 
port map(clk, '1', ddr_en, ddr_en_sync);

sync_reg6 : entity work.sync_reg 
port map(clk, '1', mimo_en, mimo_en_sync);

sync_reg7 : entity work.sync_reg 
port map(clk, '1', fidm, fidm_sync);

sync_reg8 : entity work.sync_reg 
port map(clk, '1', clr_smpl_nr, clr_smpl_nr_sync);

sync_reg9 : entity work.sync_reg 
port map(clk, '1', ld_smpl_nr, ld_smpl_nr_sync);

sync_reg10 : entity work.sync_reg 
port map(clk, '1', test_ptrn_en, test_ptrn_en_sync);

sync_reg11 : entity work.sync_reg 
port map(clk, '1', smpl_cmp_start, smpl_cmp_start_sync);


bus_sync_reg0 : entity work.bus_sync_reg
generic map (2)
port map(clk, '1', sample_width, sample_width_sync);

bus_sync_reg1 : entity work.bus_sync_reg
generic map (2)
port map(clk, '1', ch_en, ch_en_sync);

bus_sync_reg2 : entity work.bus_sync_reg
generic map (64)
port map(clk, '1', smpl_nr_in, smpl_nr_in_sync);

bus_sync_reg3 : entity work.bus_sync_reg
generic map (16)
port map(clk, '1', smpl_cmp_length, smpl_cmp_length_sync);





-- ----------------------------------------------------------------------------
-- diq2fifo instance
-- ----------------------------------------------------------------------------
diq2fifo_inst0 : entity work.diq2fifo
   generic map( 
      dev_family           => dev_family,
      iq_width             => iq_width,
      invert_input_clocks  => invert_input_clocks
      )
   port map(
      clk               => clk,
      reset_n           => reset_n_sync,
      --Mode settings
      test_ptrn_en      => test_ptrn_en_sync,
      mode              => mode_sync, -- JESD207: 1; TRXIQ: 0
      trxiqpulse        => trxiqpulse_sync, -- trxiqpulse on: 1; trxiqpulse off: 0
      ddr_en            => ddr_en_sync, -- DDR: 1; SDR: 0
      mimo_en           => mimo_en_sync, -- SISO: 1; MIMO: 0
      ch_en             => ch_en_sync, --"01" - Ch. A, "10" - Ch. B, "11" - Ch. A and Ch. B. 
      fidm              => fidm_sync, -- External Frame ID mode. Frame start at fsync = 0, when 0. Frame start at fsync = 1, when 1.
      --Rx interface data 
      DIQ               => DIQ,
      fsync             => fsync,
      --fifo ports 
      fifo_wfull        => inst1_wrfull,
      fifo_wrreq        => inst11_fifo_wrreq,
      fifo_wdata        => inst11_fifo_wdata, 
      smpl_cmp_start    => smpl_cmp_start_sync,
      smpl_cmp_length   => smpl_cmp_length_sync,
      smpl_cmp_done     => smpl_cmp_done,
      smpl_cmp_err      => smpl_cmp_err
        );
        
        
smpl_fifo_wrreq_out <= inst0_fifo_wrreq; 
        

-- ----------------------------------------------------------------------------
-- DSP Subsystem
-- ----------------------------------------------------------------------------

dspcfg_subsystem_inst11 : component lms_dsp
  port map (
		clk_clk                             => clk,                    --      clk.clk
		preamble_detect_cfg_enable          => dspcfg_preamble_en,     -- preamble_detect.cfg_enable
		preamble_detect_cfg_FILTER_LEN      => dspcfg_FILTER_LEN,      --                .cfg_FILTER_LEN
      preamble_detect_cfg_PASSTHROUGH_LEN => dspcfg_PASSTHROUGH_LEN, --                .cfg_PASSTHROUGH_LEN
      preamble_detect_cfg_THRESHOLD       => dspcfg_THRESHOLD,       --                .cfg_THRESHOLD
      preamble_detect_debug_sum           => dspcfg_sum,       --                      .cfg_THRESHOLD
      preamble_detect_debug_count         => dspcfg_count,       --                    .cfg_THRESHOLD
		fifo_in_wdata                       => inst11_fifo_wdata,      --  fifo_in.wdata
		fifo_in_wrreq                       => inst11_fifo_wrreq,      --         .wrreq
		fifo_out_wrdata                     => inst0_fifo_wdata,       -- fifo_out.wrdata
		fifo_out_wrreq                      => inst0_fifo_wrreq,       --         .wrreq
		reset_reset_n                       => reset_n_sync            --    reset.reset_n
  );

-- ----------------------------------------------------------------------------
-- FIFO for storing samples
-- ----------------------------------------------------------------------------       
smpl_fifo_inst1 : entity work.fifo_inst
  generic map(
      dev_family      => dev_family, 
      wrwidth         => (iq_width*4),
      wrusedw_witdth  => smpl_buff_rdusedw_w,
      rdwidth         => (iq_width*4),
      rdusedw_width   => smpl_buff_rdusedw_w,
      show_ahead      => "OFF"
  ) 

  port map(
      --input ports 
      reset_n        => reset_n_sync,
      wrclk          => clk,
      wrreq          => inst0_fifo_wrreq,
      data           => inst0_fifo_wdata(23 downto 0) & inst0_fifo_wdata(47 downto 24),
      wrfull         => inst1_wrfull,
      wrempty        => open,
      wrusedw        => open,
      rdclk          => clk,
      rdreq          => inst2_smpl_buff_rdreq,
      q              => inst1_q,
      rdempty        => open,
      rdusedw        => inst1_rdusedw  
        );
 
--samples are placed to MSb LSb ar filled with zeros 
inst2_smpl_buff_rddata <=  inst1_q(47 downto 36) & "0000" & 
                           inst1_q(35 downto 24) & "0000" & 
                           inst1_q(23 downto 12) & "0000" & 
                           inst1_q(11 downto 0) & "0000";
    
    
--packet reserved bits  
  inst2_pct_hdr_0(15 downto 0)   <="0000000000000" & pct_fifo_wusedw(pct_buff_wrusedw_w-1 downto pct_buff_wrusedw_w-3);
  inst2_pct_hdr_0(31 downto 16)  <=x"0201";
  inst2_pct_hdr_0(47 downto 32)  <=x"0403";
  inst2_pct_hdr_0(63 downto 48)  <=x"0605";
        
        
-- ----------------------------------------------------------------------------
-- Instance for packing samples to packets
-- ----------------------------------------------------------------------------       
data2packets_top_inst2 : entity work.data2packets_top
   generic map(
      smpl_buff_rdusedw_w => smpl_buff_rdusedw_w,  --bus width in bits 
      pct_buff_wrusedw_w  => pct_buff_wrusedw_w    --bus width in bits            
   )
   port map(
      clk               => clk,
      reset_n           => reset_n_sync,
      sample_width      => sample_width_sync,
      pct_hdr_0         => inst2_pct_hdr_0,
      pct_hdr_1         => inst2_pct_hdr_1,
      pct_buff_wrusedw  => pct_fifo_wusedw,
      pct_buff_wrreq    => pct_fifo_wrreq,
      pct_buff_wrdata   => pct_fifo_wdata,
      pct_hdr_cap       => pct_hdr_cap,
      smpl_buff_rdusedw => inst1_rdusedw,
      smpl_buff_rdreq   => inst2_smpl_buff_rdreq,
      smpl_buff_rddata  => inst2_smpl_buff_rddata   
        );
        
-- ----------------------------------------------------------------------------
-- Instance for packing sample counter for packet forming
-- ----------------------------------------------------------------------------        
smpl_cnt_inst3 : entity work.smpl_cnt
   generic map(
      cnt_width   => 64
   )
   port map(

      clk         => clk,
      reset_n     => reset_n_sync,
      mode        => mode_sync,
      trxiqpulse  => trxiqpulse_sync,
      ddr_en      => ddr_en_sync,
      mimo_en     => mimo_en_sync,
      ch_en       => ch_en_sync,
      sclr        => clr_smpl_nr_sync,
      sload       => ld_smpl_nr_sync,
      data        => smpl_nr_in_sync,
      cnt_en      => inst2_smpl_buff_rdreq,
      q           => inst3_q        
        );
        
-- ----------------------------------------------------------------------------
-- There is 6 clock cycle latency from smpl_fifo_inst1 to packet formation
-- and smpl_cnt has to be delayed 6 cycles
-- ----------------------------------------------------------------------------  

delay_chain_inst5 : entity work.delay_chain
   generic map(
      delay   => 6,
		data_width => 64
   )
   port map(
      clk         => clk,
      reset_n     => reset_n_sync,
      data_in     => inst3_q,
      data_out    => inst2_pct_hdr_1
);    
  
end arch;   





