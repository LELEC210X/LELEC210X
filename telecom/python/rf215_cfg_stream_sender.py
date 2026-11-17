############################################################
# rf215_cfg_stream_sender – envoie des commandes via TCP  #
############################################################
import socket

# Global variables for TCP remote host configuration
TCP_REMOTE_HOST = "localhost"
TCP_REMOTE_PORT = 5100

def ccf0_from_freq(f_hz):        # pas de 25 kHz
    return int(round(f_hz / 25_000.0)) & 0xFFFF

def pll_code_from_freq(f_hz):        # pas de 25 kHz
    return int((f_hz-754e6)/13e6 *2**16) & 0x00FFFFFF

def int_to_hex_str(value: int, num_chars: int) -> str:
    """Convert an integer to a hexadecimal string with a fixed number of characters.

    Args:
        value: The integer to convert.
        num_chars: The desired number of hexadecimal characters.

    Returns:
        The hexadecimal string, padded with leading zeros if needed.
    """
    return f"{value:0{num_chars}x}"

def find_closest_key(input_value, value_dict):
    """
    Returns the integer key in `value_dict` whose float value is closest to `input_value`.

    Args:
        input_value (float): The value to compare against.
        value_dict (dict): A dictionary with integer keys and float values.

    Returns:
        int: The key whose value is closest to `input_value`.
    """
    closest_key = None
    min_distance = float('inf')

    for key, value in value_dict.items():
        distance = abs(value - input_value)
        if distance < min_distance:
            min_distance = distance
            closest_key = key

    return closest_key


R_RST        = "0x0005"
R_PN         = "0x000D"
R_VN         = "0x000E"
RF09_IRQS    = "0x0000"
RF09_STATE   = "0x0102"
R_IQIFC0     = "0x000A" 
R_IQIFC1     = "0x000B"
RF09_CS      = "0x0104"
RF09_CCF0L   = "0x0105"
RF09_CCF0H   = "0x0106"
RF09_CNL     = "0x0107"
RF09_CNM     = "0x0108"
RF09_RXBWC   = "0x0109"
RF09_RXDFE   = "0x010A"
RF09_AGCC    = "0x010B"
RF09_AGCS    = "0x010C"  
RF09_RSSI    = "0x010C"   
RF09_RSSI    = "0x010D" 
RF09_EDC     = "0x010E" 
RF09_EDD     = "0x010F" 
RF09_EDV     = "0x0110" 
RF09_RNDV    = "0x0111" 

rx_bw_dict = {  0x00  : 160e3,
                0x01  : 200e3,
                0x02  : 250e3,
                0x03  : 320e3,
                0x04  : 400e3,
                0x05  : 500e3,
                0x06  : 630e3,
                0x07  : 800e3,
                0x08  : 1000e3,
                0x09  : 1250e3,
                0x0A : 1600e3,
                0x0B : 2000e3}



rx_sr_dict = {  0x01 : 4000e3,
                0x02 : 2000e3,
                0x03 : (4000e3/3),
                0x04 : 1000e3,
                0x05 : 800e3,
                0x06 : (2000e3/3),
                0x08 : 500e3,
                0x0A : 400e3}


rx_avgs_dict = {  0x00 : 8,
                  0x01 : 16,
                  0x02 : 32,
                  0x03 : 64}

rx_agc_target_dict = {  0x00  : -21,
                        0x01  : -24,
                        0x02  : -27,
                        0x03  : -30,
                        0x04  : -33,
                        0x05  : -36,
                        0x06  : -39,
                        0x07  : -42}

class rf215_cfg_stream_sender:
    """
    Manages RF215 configuration commands and sends them via TCP.
    
    This class (NOT a GNU Radio block) handles parameter changes and 
    transmits commands to a remote device via TCP connection.
    
    """
    def __init__(self,
                 cf=868e6,
                 chunk=1024,
                 rx_ifshift=1,
                 rxbw=1,
                 rxdfe_cut=1,
                 rxdfe_sr=5,
                 agc_on=0,
                 agc_input =0,
                 agc_target=4,
                 agc_avgs = 8,
                 rx_gain=17,
                 ip_address=TCP_REMOTE_HOST,
                 port= TCP_REMOTE_PORT,
                 r_rx_gain = 0,
                 r_rssi = 0):
        
        self.cf          = float(cf)
        self.chunk       = int(chunk)
        self.rx_ifshift  = int(rx_ifshift)
        self.rxbw        = rxbw 
        self.rxdfe_cut   = int(rxdfe_cut) & 0x07
        self.rxdfe_sr    = rxdfe_sr
        self.agc_input   = int(agc_input)
        self.agc_on      = int(agc_on)
        self.agc_target  = agc_target
        self.agc_avgs    = int(agc_avgs)
        self.rx_gain     = int(rx_gain) & 0x1F
        self.ip_address  = ip_address
        self.port        = port

        # TCP socket for remote transmission
        self._tcp_socket = None
        self._tcp_connected = False
        
        # Attempt to connect on initialization
        self._connect_tcp()

        self.init_configuration()

        

    def _connect_tcp(self):
        """Attempt to connect to the remote TCP host."""
        try:
            self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tcp_socket.connect((self.ip_address, self.port))
            self._tcp_connected = True
            print(f"[rf215_cfg] Connected to TCP {self.ip_address}:{self.port}", flush=True)
        except Exception as e:
            print(f"[rf215_cfg] Failed to connect to TCP {self.ip_address}:{self.port}: {e}", flush=True)
            self._tcp_connected = False
            if self._tcp_socket:
                try:
                    self._tcp_socket.close()
                except:
                    pass
                self._tcp_socket = None

    def _send_command(self, cmd_data):
        """Send a command via TCP to the remote host."""
        if self._tcp_connected and self._tcp_socket:
            try:
                self._tcp_socket.sendall(cmd_data)
                print(f"[rf215_cfg] TCP sent: {cmd_data}", flush=True)
            except Exception as e:
                print(f"[rf215_cfg] TCP send error: {e}", flush=True)
                # Close socket and mark as disconnected
                try:
                    self._tcp_socket.close()
                except:
                    pass
                self._tcp_socket = None
                self._tcp_connected = False
                
                # Attempt to reconnect
                self._connect_tcp()
        else:
            print(f"[rf215_cfg] Not connected to TCP, command not sent: {cmd_data}", flush=True)    


######################################################################################
    def set_cf(self, cf, verbose=True):
        #Set Frequency generation with PLL
        self.cf = pll_code_from_freq(float(cf)) 

        cf_high_byte = (self.cf>>16) & 0xFF
        cmd = f"W{RF09_CCF0H}={int_to_hex_str(cf_high_byte, 2)}mFF".encode()
        self._send_command(cmd)
        cf_mid_byte = (self.cf>>8) & 0xFF
        cmd = f"W{RF09_CCF0L}={int_to_hex_str(cf_mid_byte, 2)}mFF".encode()
        self._send_command(cmd)
        cmd = f"W{RF09_CNM}={int_to_hex_str(2<<6, 2)}mC0".encode()
        self._send_command(cmd)

        cf_low_byte = (self.cf) & 0xFF
        cmd = f"W{RF09_CNL}={int_to_hex_str(cf_low_byte, 2)}mFF".encode()
        self._send_command(cmd)
        cmd = f"W{RF09_CNM}={int_to_hex_str(2<<6, 2)}mC0".encode()
        self._send_command(cmd)


        if verbose:
            print(f"[rf21_cmd] set_cf({self.cf}) - sent", flush=True)

######################################################################################
    def set_ifshift(self, rx_ifshift, verbose=True):
        self.rx_ifshift = rx_ifshift & 0x01

        cmd = f"W{RF09_RXBWC}={int_to_hex_str(self.rx_ifshift<<4, 2)}m10".encode()
        self._send_command(cmd)
        if verbose:
            print(f"[rf21_cmd] set_ifshift({self.cf}) - sent", flush=True)

######################################################################################
    def set_rxbw(self, rxbw, verbose=True):
        self.rxbw = rxbw
        rxbw_reg = find_closest_key(self.rxbw,rx_bw_dict) & 0x0F

        cmd = f"W{RF09_RXBWC}={int_to_hex_str(rxbw_reg, 2)}m0F".encode()
        self._send_command(cmd)
        if verbose:
            print(f"[rf21_cmd] set_rxbw({self.cf}) - sent", flush=True)

######################################################################################
    def set_rxdfe_cut(self, rxdfe_cut, verbose=True):
        self.rxdfe_cut = rxdfe_cut & 0x07

        cmd = f"W{RF09_RXDFE}={int_to_hex_str(self.rxdfe_cut<<5, 2)}mE0".encode()
        self._send_command(cmd)
        if verbose:
            print(f"[rf21_cmd] set_rxdfe_cut({self.cf}) - sent", flush=True)
    

######################################################################################
    def set_sr(self, rxdfe_sr, verbose=True):
        self.rxdfe_sr = rxdfe_sr 
        rxbw_reg = find_closest_key(self.rxdfe_sr,rx_sr_dict) & 0x0F

        cmd = f"W{RF09_RXDFE}={int_to_hex_str(rxbw_reg, 2)}m0F".encode()
        self._send_command(cmd)
        if verbose:
            print(f"[rf21_cmd] set_sr({self.self.rxdfe_sr}) - sent", flush=True)


######################################################################################
    def set_agc_input(self, agc_input, verbose=True):
        self.agc_input = int(agc_input)  & 0x01

        cmd = f"W{RF09_AGCC}={int_to_hex_str(self.agc_on<<6, 2)}m40".encode()
        self._send_command(cmd)
        if verbose:
            print(f"[rf21_cmd] set_agc_input({self.agc_input}) - sent", flush=True)
######################################################################################

    def set_agc_avgs(self, avgs, verbose=True):
        self.agc_avgs = int(avgs)
        avgs_reg = find_closest_key(self.agc_avgs,rx_avgs_dict) & 0x03

        cmd = f"W{RF09_AGCC}={int_to_hex_str(avgs_reg<<4, 2)}m30".encode()
        self._send_command(cmd)
        if verbose:
            print(f"[rf21_cmd] set_agc_avgs({self.agc_avgs}) - sent", flush=True)

######################################################################################
    def set_agc_on(self, agc_on, verbose=True):
        self.agc_on = int(agc_on)  & 0x01

        cmd = f"W{RF09_AGCC}={int_to_hex_str(self.agc_on<<0, 2)}m01".encode()
        self._send_command(cmd)
        if verbose:
            print(f"[rf21_cmd] set_agc_on({self.agc_on}) - sent", flush=True)



######################################################################################
    def set_agc_target(self, agc_target, verbose=True):
        self.agc_target = agc_target
        agc_target_reg = find_closest_key(agc_target,rx_agc_target_dict) & 0x07

        cmd = f"W{RF09_AGCS}={int_to_hex_str(agc_target_reg<<5, 2)}mE0".encode()
        self._send_command(cmd)
        if verbose:
            print(f"[rf21_cmd] set_agc_target({self.agc_target}) - sent", flush=True)


######################################################################################
    def set_rx_gain(self, rx_gain, verbose=True):
        self.rx_gain = int(rx_gain) & 0x1F
        cmd = f"W{RF09_AGCS}={int_to_hex_str(self.rx_gain, 2)}m1F".encode()
        self._send_command(cmd)
        if verbose:
            print(f"[rf21_cmd] set_rx_gain({self.rx_gain}) - sent", flush=True)

######################################################################################
    def read_rx_gain(self,r_rx_gain,  verbose=True):
        if r_rx_gain == 1:
            cmd = f"R{RF09_AGCS}=00m1F".encode()
            self._send_command(cmd)
            if verbose:
                print(f"[rf21_cmd] read_rx_gain sent", flush=True)

######################################################################################
    def read_rssi(self, r_rssi, verbose=True):
        if r_rssi == 1:
            cmd = f"R{RF09_RSSI}=00mFF".encode()
            self._send_command(cmd)
            if verbose:
                print(f"[rf21_cmd] read_rssi sent", flush=True)
######################################################################################

    def init_configuration(self):
            
        print(f"[rf215_cfg] Initial configuartion ")
        self.set_cf         (self.cf           , False)
        self.set_ifshift    (self.rx_ifshift   , False)
        self.set_rxbw       (self.rxbw         , False)
        self.set_rxdfe_cut  (self.rxdfe_cut    , False)
        self.set_sr         (self.rxdfe_sr     , False)
        self.set_agc_on     (self.agc_on       , False)
        self.set_agc_target (self.agc_target   , False)
        self.set_rx_gain    (self.rx_gain      , False)


    # ------------------------------------------------------------
    def close(self):
        """Close the TCP connection."""
        print("[rf215_cfg] Closing TCP connection", flush=True)
        if self._tcp_socket:
            try:
                self._tcp_socket.close()
                print("[rf215_cfg] TCP connection closed", flush=True)
            except Exception as e:
                print(f"[rf215_cfg] Error closing TCP connection: {e}", flush=True)
            self._tcp_socket = None
            self._tcp_connected = False

    # Destructor to clean up
    def __del__(self):
        self.close()
