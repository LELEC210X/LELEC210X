	component unnamed is
		port (
			cfg_PASSTHROUGH_LEN           : in  std_logic_vector(15 downto 0) := (others => 'X'); -- cfg_passthrough_len
			cfg_THRESHOLD                 : in  std_logic_vector(7 downto 0)  := (others => 'X'); -- cfg_threshold
			cfg_clear_rs                  : in  std_logic                     := 'X';             -- cfg_clear_rs
			cfg_enable                    : in  std_logic                     := 'X';             -- cfg_enable
			debug_count                   : out std_logic_vector(31 downto 0);                    -- debug_count
			debug_long_sum                : out std_logic_vector(31 downto 0);                    -- debug_long_sum
			debug_short_sum               : out std_logic_vector(31 downto 0);                    -- debug_short_sum
			avalon_streaming_sink_data    : in  std_logic_vector(23 downto 0) := (others => 'X'); -- data
			avalon_streaming_sink_valid   : in  std_logic                     := 'X';             -- valid
			avalon_streaming_source_data  : out std_logic_vector(23 downto 0);                    -- data
			avalon_streaming_source_valid : out std_logic;                                        -- valid
			clock_sink_clk                : in  std_logic                     := 'X';             -- clk
			reset_sink_reset              : in  std_logic                     := 'X'              -- reset
		);
	end component unnamed;

	u0 : component unnamed
		port map (
			cfg_PASSTHROUGH_LEN           => CONNECTED_TO_cfg_PASSTHROUGH_LEN,           --                     cfg.cfg_passthrough_len
			cfg_THRESHOLD                 => CONNECTED_TO_cfg_THRESHOLD,                 --                        .cfg_threshold
			cfg_clear_rs                  => CONNECTED_TO_cfg_clear_rs,                  --                        .cfg_clear_rs
			cfg_enable                    => CONNECTED_TO_cfg_enable,                    --                        .cfg_enable
			debug_count                   => CONNECTED_TO_debug_count,                   --                        .debug_count
			debug_long_sum                => CONNECTED_TO_debug_long_sum,                --                        .debug_long_sum
			debug_short_sum               => CONNECTED_TO_debug_short_sum,               --                        .debug_short_sum
			avalon_streaming_sink_data    => CONNECTED_TO_avalon_streaming_sink_data,    --   avalon_streaming_sink.data
			avalon_streaming_sink_valid   => CONNECTED_TO_avalon_streaming_sink_valid,   --                        .valid
			avalon_streaming_source_data  => CONNECTED_TO_avalon_streaming_source_data,  -- avalon_streaming_source.data
			avalon_streaming_source_valid => CONNECTED_TO_avalon_streaming_source_valid, --                        .valid
			clock_sink_clk                => CONNECTED_TO_clock_sink_clk,                --              clock_sink.clk
			reset_sink_reset              => CONNECTED_TO_reset_sink_reset               --              reset_sink.reset
		);

