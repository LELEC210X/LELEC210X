
`timescale 1 ps / 1 ps

`define tb packet_presence_detection_tb_gen_tb_inst
`define dut `tb.packet_presence_detection_tb_gen_inst
`define clk `tb.packet_presence_detection_tb_gen_inst_clock_bfm
`define rst `tb.packet_presence_detection_tb_gen_inst_reset_bfm
`define input `tb.packet_presence_detection_tb_gen_inst_sink_bfm
`define output `tb.packet_presence_detection_tb_gen_inst_source_bfm
`define cfg    `tb.packet_presence_detection_tb_gen_inst.conduit_bfm_0

module test_program();

int input_fd, output_fd;
reg [23:0] input_data, output_data;

int count;
int count_allSamples;

int samples_p_packet   = 900;
int passthrough_len    = 100;
int n_packet = 2;
int state_clear_rs;

initial
begin

    
    `cfg.set_cfg_enable(1'b1);
    `cfg.set_cfg_clear_rs(1'b0);
    `cfg.set_cfg_threshold(16'd12);
    `cfg.set_cfg_passthrough_len(16'd100);

    state_clear_rs = 1;
    // Reset DUT
    $display("Hello ModelSim!");
    wait(`dut.reset_reset == 0);
    count            = 0;
    count_allSamples = 0;

    // Reset I/F
    `input.init();
    `output.init();

    // Open input file
    input_fd = $fopen("./mentor/input_fpga.txt","r");
    output_fd = $fopen("./mentor/output_fpga.txt","w+");

    if (!input_fd)
        $display("Could not open \"input_fpga.txt\"");

    if (!output_fd)
        $display("Could not open \"output_fpga.txt\"");

    if (!input_fd || !output_fd)
        $finish();

    // Send all
    begin
        // Read/Write I/O of the DUT
        while(!$feof(input_fd)) begin
            // Read file
            $fscanf(input_fd, "%h", input_data);
            // Set input
            `input.set_transaction_data(input_data);
            `input.push_transaction();

            count  =  count+ 1;
        end
    end
    count_allSamples = count;
    count =0;
    // Receive all
    begin
        while (count_allSamples >= 0) begin
            wait (`output.signal_transaction_received.triggered); #1;
            // Read output
            `output.pop_transaction();
            output_data = `output.get_transaction_data();
            $fwrite(output_fd, "%h\n", output_data);
            count_allSamples = count_allSamples - 1;
            count = count+1; 
        end
    end

    // Close files
    $fclose(input_fd);
    $fclose(output_fd);
    $finish();
end

endmodule
