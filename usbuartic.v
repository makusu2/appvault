module AppVault(
    input C_CC1,
    input C_CC2,
    inout C_USB_TP, //D+
    inout C_USB_TN, //D-
    inout C_USB_BP, //D+
    inout C_USB_BN, //D-
    inout C_SBU1,
    inout C_SBU2);
    wire C_CC1, C_CC2, C_USB_TP, C_USB_TN, C_USB_BP, C_USB_BN, C_SBU1, C_SBU2;
    wire [9:1]GPIO;
    wire VDDIO, VIN_3V3, VOUT_3V3, RESETZ, MRESET, HRESET, BUSPOWERZ, R_OSC, I2C_ADDR, I2C_SDA1Z, I2C_SCL1Z, I2C_IRQ1Z, I2C_SDA2Z, I2C_SCL2Z, I2C_IRQ2Z, SPI_MOSI, SPI_MISO, SPI_SSZ, SPI_CLK, SWD_DATA, SWD_CLK, DEBUG_CTL1, DEBUG_CTL2, UART_RX, UART_TX,  LSX_R2P, LSX_P2R, AUX_P, AUX_N, USB_RP_P, USB_RP_N, DEBUG1, DEBUG2, DEBUG3, DEBUG4, GND, RPD_G2, RPD_G1, LDO_3V3, LDO_1V8A, LDO_1V8D, LDO_BMC;
    USBCPortOut connector(C_CC1,C_CC2,C_USB_TP,C_USB_TN,C_USB_BP,C_USB_BN,C_SBU1,C_SBU2);
    TPS65983B usbcontroller(VDDIO, VIN_3V3, VOUT_3V3, RESETZ, MRESET, HRESET, BUSPOWERZ, R_OSC, I2C_ADDR, GPIO, I2C_SDA1Z, I2C_SCL1Z, I2C_IRQ1Z, I2C_SDA2Z, I2C_SCL2Z, I2C_IRQ2Z, SPI_MOSI, SPI_MISO, SPI_SSZ, SPI_CLK, SWD_DATA, SWD_CLK, DEBUG_CTL1, DEBUG_CTL2, UART_RX, UART_TX,  LSX_R2P, LSX_P2R, AUX_P, AUX_N, USB_RP_P, USB_RP_N, DEBUG1, DEBUG2, DEBUG3, DEBUG4, GND, C_SBU1, C_SBU2, C_USB_BP, C_USB_BN, C_USB_TP, C_USB_TN, RPD_G2, C_CC2, RPD_G1, C_CC1, LDO_3V3, LDO_1V8A, LDO_1V8D, LDO_BMC);
    
endmodule
module PacketAnalyzer(
    input wire [63:0] inPacket,
    output wire [31:0] outPacket //These packets will be VERY different, they just have the same name
    );
    /*
    TODO:
        Get metadata and encrypted data from packet
        Unencrypt data
        Execute data using RISC-V processor module
        Capture loads/stores and any IO operations from the processor module and return its representative form in a packet (outPacket).
    */
endmodule
/*
We'll also have a RISC-V processor module, which gets used by PacketAnalyzer.
*/
module Decoder(
    input wire [7:0]encoded_data, //Can change bus size to whatever, even different than the size of decoded
    output wire [7:0] decoded_data
    );
    assign decoded_data = encoded_data; //TODO this is where it'll be encoded
endmodule
module Encoder(
    input wire [7:0] decoded_data,
    output wire [7:0] encoded_data
    );
    assign encoded_data = decoded_data;
endmodule
    
module USBCPortOut(
    inout C_CC1,
    inout C_CC2,
    inout C_USB_TP, //D+
    inout C_USB_TN, //D-
    inout C_USB_BP, //D+
    inout C_USB_BN, //D-
    inout C_SBU1,
    inout C_SBU2);
endmodule
        
module TPS65983B(
    input VDDIO,
    input VIN_3V3,
    output VOUT_3V3,
    output RESETZ,
    input MRESET,
    input HRESET,
    input BUSPOWERZ,
    inout R_OSC,
    inout I2C_ADDR,
    inout wire [9:1]GPIO,
    inout I2C_SDA1Z,
    inout I2C_SCL1Z,
    inout I2C_IRQ1Z,
    inout I2C_SDA2Z,
    inout I2C_SCL2Z,
    inout I2C_IRQ2Z,
    inout SPI_MOSI,
    inout SPI_MISO,
    inout SPI_SSZ,
    inout SPI_CLK,
    inout SWD_DATA,
    inout SWD_CLK,
    inout DEBUG_CTL1,
    inout DEBUG_CTL2,
    input UART_RX,
    output UART_TX, 
    inout LSX_R2P,
    inout LSX_P2R,
    inout AUX_P,
    inout AUX_N,
    inout USB_RP_P,
    inout USB_RP_N,
    inout DEBUG1,
    inout DEBUG2,
    inout DEBUG3,
    inout DEBUG4,
    input GND,
    inout C_SBU1,
    inout C_SBU2,
    inout C_USB_BP,
    inout C_USB_BN,
    inout C_USB_TP,
    inout C_USB_TN,
    inout RPD_G2,
    inout C_CC2,
    inout RPD_G1,
    inout C_CC1,
    output LDO_3V3,
    output LDO_1V8A,
    output LDO_1V8D,
    output LDO_BMC);
    /*
    Need to tie lots of the unused inputs/outputs to what it says in the datasheet.
    */
endmodule