# LimeSDR-Mini FPGA gateware

This repository contains the FPGA gateware project for the LimeSDR-Mini board.

The gateware can be built with the free version of the Altera Quartus tools.

## Quartus config

- Go to [the Quartus Download Center](https://fpgasoftware.intel.com/18.1/?edition=lite&platform=windows)
- Download "MAX 10 FPGA device support" (330 MB)

## Compilation

- Launch compilation (play button)
- Specify "No" for the Hardware update popup

## Programming
  1. If it is the first time you are going to program the FPGA, first do an autoprogramming.
  1. Connect the LimeSDR-Mini to an USB port, open LimeSuite GUI and go to Options >> ConnectionSettings. You should see the LimeSDR Mini banner, click on it and then on Connect.
  ![Step 1](LimeSDR-Mini_lms7_lelec210x/doc/readme_programming_1.png)
  1. Go to Modules >> Programming. Once the window open, switch the Programming mode to FPGA FLASH. Click Open and find the stream file named `LimeSDR-Mini_bitstreams/LimeSDR-Mini_lms7_lelec210x_HW_1.2_auto.rpd`. Click Program and wait for the completion and the "Programming Completed!" message.
  ![Step 2](LimeSDR-Mini_lms7_lelec210x/doc/readme_programming_2.png)

## Custom gr-limesdr Installation

## FPGA Register Map

| Address |   Default Value    | Free |                             Description                                 |
| ------- | ------------------ | ---- | ----------------------------------------------------------------------- |
| 0x0000  | 0b0000000000000000 |  00  | Board ID                                                                |
| 0x0001  | 0b0000000000000000 |  00  | GW version                                                              |
| 0x0002  | 0b0000000000000000 |  00  | GW revision                                                             |
| 0x0003  | 0b0000000000000000 |   9  | BOM_VER[6:4],HW_VER[3:0]                                                |
| 0x0004  | 0b0000000000000000 |  16  |                                                                         |
| 0x0005  | 0b0000000000000000 |   0  | drct_clk_en                                                             |
| 0x0006  | 0b0000000000000000 |  16  |                                                                         |
| 0x0007  | 0b0000000000000011 |   0  | ch_en[15:0]                                                             |
| 0x0008  | 0b0000000100000010 |   8  | mimo_int_en,trxiq_pulse,ddr_en,mode,reserved[2:0],smpl_width[1:0]       |
| 0x0009  | 0b0000000000000011 |  14  | txpct_loss_clr,smpl_nr_clr                                              |
| 0x000a  | 0b0000000000000000 |  14  | rx_ptrn_en,rx_en                                                        |
| 0x000b  | 0b0000000011111111 |   0  | dspcfg_PASSTHROUGH_LEN[15:0]                                            |
| 0x000c  | 0b0000000000000000 |   0  | dspcfg_THRESHOLD[31:16]                                                 |
| 0x000d  | 0b0000000000000001 |   0  | dspcfg_THRESHOLD[15:0]                                                  |
| 0x000e  | 0b1000000000000000 |   9  | dspcfg_FILTER_LEN[5:0],{0b000_0000},dspcfg_preamble_en                  |
| 0x000f  | 0x03FC             |  16  |                                                                         |
| 0x0010  | 0x0001             |  16  |                                                                         |
| 0x0011  | 0x0001             |  16  |                                                                         |
| 0x0012  | 0b1111111111111111 |  16  |                                                                         |
| 0x0013  | 0b0110111101101011 |  11  | LMS1_RXEN,LMS1_TXEN,LMS1_TXNRX2,LMS1_TXNRX1,LMS1_CORE_LDO_EN,LMS1_RESET |
| 0x0014  | 0b0000000000000011 |   0  | (Reserved LMS control)                                                  |
| 0x0015  | 0b0000000000000000 |   0  | (Reserved LMS control)                                                  |
| 0x0016  | 0b0000000000000000 |   0  | (Reserved LMS control)                                                  |
| 0x0017  | 0b0001000101000100 |   0  | (Reserved),GPIO[6:0]                                                    |
| 0x0018  | 0b0000000000000000 |  16  | (Reserved)                                                              |
| 0x0019  | 0b0000000000000000 |  16  | (Reserved)                                                              |
| 0x001a  | 0b0000000000000000 |   0  | Reserved[15:8],FPGA_LED1_G,FPGA_LED1_R                                  |
| 0x001b  | 0b0000000000000000 |   0  | Reserved[15:0]                                                          |
| 0x001c  | 0b0000000000000000 |   0  | Reserved[15:4],FX3_LED_CTRL                                             |
| 0x001d  | 0b0000000000001111 |   0  | CLK_ENA[1:0]                                                            |
| 0x001e  | 0x0003             |  16  |                                                                         |
| 0x001f  | 0xD090             |  16  |                                                                         |

## Callstack when writing to Registers (GNURadio --> LimeSuite --> Nios)
### Write to LMS7002 Registers
#### Host:
  - `LMS_WriteParam(lms_device_t *device, struct LMS7Parameter param, uint16_t val)`
  - `LMS7_Device::WriteParam(const struct LMS7Parameter& param, uint16_t val, int chan)`
  - `LMS7002M::Modify_SPI_Reg_bits(const LMS7Parameter &param, const uint16_t value, bool fromChip)`
  - `LMS7002M::Modify_SPI_Reg_bits(const uint16_t address, const uint8_t msb, const uint8_t lsb, const uint16_t value, bool fromChip)`
  - `extern void SPI_write(uint16_t spiAddrReg, uint16_t spiDataReg)`
  - `int LMS64CProtocol::WriteLMS7002MSPI(const uint32_t *writeData, size_t size, unsigned periphID)`
    - `CMD_LMS7002_WR` in packet for NIOS
  - `virtual int TransactSPI(const int addr, const uint32_t *writeData, uint32_t *readData, const size_t size)`
  - `int Write(const unsigned char *buffer, int length, int timeout_ms = 100)`

#### Nios:
  - `main()`
    - `case CMD_LMS7002_WR`
  - `alt_avalon_spi_command(alt_u32 base, alt_u32 slave, alt_u32 write_length, const alt_u8 * write_data, alt_u32 read_length, alt_u8 * read_data, alt_u32 flags)`
    - `PGA_SPI_BASE, SPI_NR_LMS7002M(0)`

### Write to FPGA Registers
#### Host:
  - `API_EXPORT int CALL_CONV LMS_WriteFPGAReg(lms_device_t *device, uint32_t address, uint16_t val)`
  - `int LMS7_Device::WriteFPGAReg(uint16_t address, uint16_t val) const`
  - `int FPGA::WriteRegister(uint32_t addr, uint32_t val)`
    - `cnt=1`
  - `int FPGA::WriteRegisters(const uint32_t *addrs, const uint32_t *data, unsigned cnt)`
  - `int LMS64CProtocol::WriteRegisters(const uint32_t *addrs, const uint32_t *data, const size_t size)`
    - `CMD_BRDSPI_WR in packet for NIOS
  - `virtual int TransactSPI(const int addr, const uint32_t *writeData, uint32_t *readData, const size_t size)`
  - `int Write(const unsigned char *buffer, int length, int timeout_ms = 100)`

#### Nios:
  - `main()`
    - `case CMD_BRDSPI16_WR`
  - `alt_avalon_spi_command(alt_u32 base, alt_u32 slave, alt_u32 write_length, const alt_u8 * write_data, alt_u32 read_length, alt_u8 * read_data, alt_u32 flags)`
    - `FPGA_SPI_BASE, SPI_NR_FPGA(1)`


## Modelsim custom hardware simulation

  1. Generate input stimuli and output prediction by running `fpga-offloading/LimeSDR-Mini_lms7_lelec210x/ip/preamble_detect/testbench/python/input_gen.py` and `output_gen.py`
  1. Open ModelSim, then `fpga-offloading/LimeSDR-Mini_lms7_lelec210x/ip/preamble_detect/testbench/mentor`
  1. In the console, type `source ./run_sim.tcl`
  1. Compare outputs by running `fpga-offloading/LimeSDR-Mini_lms7_lelec210x/ip/preamble_detect/testbench/python/compare.py`

Simulation parameters are contained in `fpga-offloading/LimeSDR-Mini_lms7_lelec210x/ip/preamble_detect/testbench/mentor/msim_setup.tcl` and `run_sim.tcl`.

## Licensing

Please see the COPYING file(s). However, please note that the license terms stated do not extend to any files provided with the Altera design tools and see the relevant files for the associated terms and conditions.

