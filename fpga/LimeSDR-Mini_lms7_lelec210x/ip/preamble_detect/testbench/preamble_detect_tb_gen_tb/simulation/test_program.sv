
`timescale 1 ps / 1 ps

`define tb preamble_detect_tb_gen_tb_inst
`define dut `tb.preamble_detect_tb_gen_inst
`define clk `tb.clock_bfm_inst
`define rst `tb.reset_bfm_inst
`define input `tb.sink_bfm_inst
`define output `tb.source_bfm_inst

module test_program();

int input_fd, output_fd;
reg [23:0] input_data, output_data;

int count;

initial
begin
    // Reset DUT
    $display("Hello ModelSim!");
    wait(`dut.reset_reset == 0);
    count = 0;

    // Reset I/F
    `input.init();
    `output.init();

    // Open input file
    input_fd = $fopen("input_fpga.txt","r");
    output_fd = $fopen("output_fpga.txt","w+");

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

            count = count + 1;
        end
    end

    // Receive all
    begin
        while (count >= 0) begin
            wait (`output.signal_transaction_received.triggered); #1;
            // Read output
            `output.pop_transaction();
            output_data = `output.get_transaction_data();
            $fwrite(output_fd, "%h\n", output_data);
            count = count - 1;
        end
    end

    // Close files
    $fclose(input_fd);
    $fclose(output_fd);
    $finish();
end

endmodule
