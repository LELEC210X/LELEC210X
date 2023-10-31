
`timescale 1 ps / 1 ps

`define tb fir_tb_gen_tb_inst
`define dut `tb.fir_tb_gen_inst
`define clk `tb.fir_tb_gen_inst_clk_bfm
`define rst `tb.fir_tb_gen_inst_reset_bfm
`define input `tb.fir_tb_gen_inst_fir_compiler_ii_0_avalon_streaming_sink_bfm
`define output `tb.fir_tb_gen_inst_fir_compiler_ii_0_avalon_streaming_source_bfm

module test_program();

int input_fd, output_fd;
reg [23:0] input_data, output_data;

int count, count_rcv;
localparam WAIT_CYCLES = 5;

initial
begin
    // Reset DUT
    $display("Hello ModelSim!");
    wait(`dut.reset_reset_n == 1);
    count = 0;
    count_rcv = 0;

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
            if (count < WAIT_CYCLES) begin
                `input.set_transaction_data(24'b0);
            end
            else begin
                // Read file
                $fscanf(input_fd, "%h", input_data);
                // Set input
                `input.set_transaction_data(input_data);
            end
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
            if (count_rcv >= WAIT_CYCLES - 2) begin
                $fwrite(output_fd, "%h\n", output_data);
            end
            count = count - 1;
            count_rcv = count_rcv + 1;
        end
    end

    // Close files
    $fclose(input_fd);
    $fclose(output_fd);
    $finish();
end

endmodule
