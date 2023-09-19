	component preamble_detect_tb_gen is
		port (
			clock_clk    : in  std_logic                     := 'X';             -- clk
			reset_reset  : in  std_logic                     := 'X';             -- reset
			sink_data    : in  std_logic_vector(23 downto 0) := (others => 'X'); -- data
			sink_valid   : in  std_logic                     := 'X';             -- valid
			source_data  : out std_logic_vector(23 downto 0);                    -- data
			source_valid : out std_logic                                         -- valid
		);
	end component preamble_detect_tb_gen;

	u0 : component preamble_detect_tb_gen
		port map (
			clock_clk    => CONNECTED_TO_clock_clk,    --  clock.clk
			reset_reset  => CONNECTED_TO_reset_reset,  --  reset.reset
			sink_data    => CONNECTED_TO_sink_data,    --   sink.data
			sink_valid   => CONNECTED_TO_sink_valid,   --       .valid
			source_data  => CONNECTED_TO_source_data,  -- source.data
			source_valid => CONNECTED_TO_source_valid  --       .valid
		);

