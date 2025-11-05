
`timescale 1 ps / 1 ps

`define tb packet_presence_detection_tb_gen_tb_inst
`define dut `tb.packet_presence_detection_tb_gen_inst
`define clk `tb.packet_presence_detection_tb_gen_inst_clock_bfm
`define rst `tb.packet_presence_detection_tb_gen_inst_reset_bfm
`define input `tb.packet_presence_detection_tb_gen_inst_sink_bfm
`define output `tb.packet_presence_detection_tb_gen_inst_source_bfm
`define cfg    `tb.packet_presence_detection_tb_gen_inst_cfg_bfm

module test_program();

int input_fd, output_fd;
reg [23:0] input_data, output_data;

int count;
int count_allSamples;


initial
begin

    
    `cfg.set_cfg_enable_ppd(1'b1);
    `cfg.set_cfg_clear_rs(1'b1);
    `cfg.set_cfg_pass_sum_signal(1'b0);
    `cfg.set_cfg_red_sum_signal(1'b0);
    `cfg.set_cfg_enable_fir(1'b0);
    `cfg.set_cfg_threshold(16'd20);
    `cfg.set_cfg_passthrough_len(16'd100);

    `input.set_transaction_data(0);

    // Reset DUT
    $display("Hello ModelSim!");
    $display("SIM START");
    wait(`dut.rst_controller_reset_out_reset == 0 );
    $display("RST ARRIVED ");

    
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

    `cfg.set_cfg_clear_rs(1'b1);
    #100000
    `cfg.set_cfg_clear_rs(1'b0);

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
 
    $display("SIM FINISHED");

    // Close files
    $fclose(input_fd);
    $fclose(output_fd);
    $finish();
end

endmodule
