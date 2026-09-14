`timescale 1ns/1ps

module v_tb();
    reg [6:0] x;
    reg [6:0] y;
    wire [3:0] r, g, b;


    // Instantiate your module  
    v dut (
        .x(x),
        .y(y),
        .vga_r(r),
        .vga_g(g),
        .vga_b(b)
    );

    integer i, j;

    initial begin
        $display("Testing coordinates...");
        for (i = 0; i < 128; i = i + 1) begin
            for (j = 0; j < 128; j = j + 1) begin
                x = i;
                y = j;
                #1; // Wait 1ns
                if (r > 0 || g > 0 || b > 0) begin
                    $display("Pixel found at X=%d, Y=%d | Color: R=%h G=%h B=%h", x, y, r, g, b);
                end
            end
        end
        $finish;
    end
endmodule