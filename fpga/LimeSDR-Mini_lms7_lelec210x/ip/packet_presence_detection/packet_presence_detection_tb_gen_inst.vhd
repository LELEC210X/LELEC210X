	component packet_presence_detection_tb_gen is
		port (
			sink_valid              : in  std_logic                     := 'X';             -- valid
			sink_data               : in  std_logic_vector(23 downto 0) := (others => 'X'); -- data
			source_data             : out std_logic_vector(23 downto 0);                    -- data
			source_valid            : out std_logic;                                        -- valid
			clk_clk                 : in  std_logic                     := 'X';             -- clk
			reset_reset_n           : in  std_logic                     := 'X';             -- reset_n
			cfg_cfg_passthrough_len : in  std_logic_vector(15 downto 0) := (others => 'X'); -- cfg_passthrough_len
			cfg_cfg_threshold       : in  std_logic_vector(7 downto 0)  := (others => 'X'); -- cfg_threshold
			cfg_cfg_clear_rs        : in  std_logic                     := 'X';             -- cfg_clear_rs
			cfg_debug_count         : out std_logic_vector(31 downto 0);                    -- debug_count
			cfg_debug_long_sum      : out std_logic_vector(31 downto 0);                    -- debug_long_sum
			cfg_debug_short_sum     : out std_logic_vector(31 downto 0);                    -- debug_short_sum
			cfg_cfg_enable_fir      : in  std_logic                     := 'X';             -- cfg_enable_fir
			cfg_cfg_enable_ppd      : in  std_logic                     := 'X';             -- cfg_enable_ppd
			cfg_cfg_pass_sum_signal : in  std_logic                     := 'X';             -- cfg_pass_sum_signal
			cfg_cfg_red_sum_signal  : in  std_logic                     := 'X'              -- cfg_red_sum_signal
		);
	end component packet_presence_detection_tb_gen;

	u0 : component packet_presence_detection_tb_gen
		port map (
			sink_valid              => CONNECTED_TO_sink_valid,              --   sink.valid
			sink_data               => CONNECTED_TO_sink_data,               --       .data
			source_data             => CONNECTED_TO_source_data,             -- source.data
			source_valid            => CONNECTED_TO_source_valid,            --       .valid
			clk_clk                 => CONNECTED_TO_clk_clk,                 --    clk.clk
			reset_reset_n           => CONNECTED_TO_reset_reset_n,           --  reset.reset_n
			cfg_cfg_passthrough_len => CONNECTED_TO_cfg_cfg_passthrough_len, --    cfg.cfg_passthrough_len
			cfg_cfg_threshold       => CONNECTED_TO_cfg_cfg_threshold,       --       .cfg_threshold
			cfg_cfg_clear_rs        => CONNECTED_TO_cfg_cfg_clear_rs,        --       .cfg_clear_rs
			cfg_debug_count         => CONNECTED_TO_cfg_debug_count,         --       .debug_count
			cfg_debug_long_sum      => CONNECTED_TO_cfg_debug_long_sum,      --       .debug_long_sum
			cfg_debug_short_sum     => CONNECTED_TO_cfg_debug_short_sum,     --       .debug_short_sum
			cfg_cfg_enable_fir      => CONNECTED_TO_cfg_cfg_enable_fir,      --       .cfg_enable_fir
			cfg_cfg_enable_ppd      => CONNECTED_TO_cfg_cfg_enable_ppd,      --       .cfg_enable_ppd
			cfg_cfg_pass_sum_signal => CONNECTED_TO_cfg_cfg_pass_sum_signal, --       .cfg_pass_sum_signal
			cfg_cfg_red_sum_signal  => CONNECTED_TO_cfg_cfg_red_sum_signal   --       .cfg_red_sum_signal
		);

