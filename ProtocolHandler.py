import Live

class ProtocolHandler:
    def __init__(self):
        self.PREFIX = [0xF0, 0x00, 0x32, 0x09]
        self.ROUTING = [0x00, 0x00, 0x40, 0x02]

    def encode_7bit(self, val, count):
        return [(val >> (7 * i)) & 0x7F for i in range(count)]

    def compute_crc(self, data):
        crc, n = 0, 4
        for byte in data:
            rotated = ((byte >> (n % 8)) | (byte << (8 - (n % 8)))) & 0xFF
            crc += rotated  # Let it accumulate without masking
            n += 1
        return 0xFF - (crc & 0xFF)

    def build_packet(self, addr, bit_len, val, mode=0x59):
        addr_blocks = self.encode_7bit(addr, 4)
        len_blocks = self.encode_7bit(bit_len * 2, 4)
        
        # Determine raw bytes for CRC
        num_bytes = (bit_len + 6) // 7
        raw_val_bytes = [(val >> (7 * i)) & 0x7F for i in range(num_bytes)]
        
        crc_data = self.ROUTING + addr_blocks + len_blocks + raw_val_bytes
        crc = self.compute_crc(crc_data)
        
        # Glue CRC (Value | CRC << bit_len)
        combined = val | (crc << bit_len)
        block_count = 3 if bit_len == 8 else 5
        val_blocks = self.encode_7bit(combined, block_count)
        
        return self.PREFIX + [mode] + self.ROUTING + addr_blocks + len_blocks + val_blocks + [0xF7]

    def get_pad_addr(self, index, shifted=False):
        # Base 126, Stride 74. Shifted starts at index 16.
        actual_index = index + 16 if shifted else index
        return 126 + (actual_index * 74)

    def get_knob_addr(self, index, shifted=False):
        # Base 0x1E, Stride 6. Shifted starts at index 8.
        actual_index = index + 8 if shifted else index
        return 0x1E + (actual_index * 6)
    
    # Add this method to your existing ProtocolHandler class
    def build_pad_config_messages(self, pad_index, shifted, note_num):
        addr = self.get_pad_addr(pad_index, shifted=shifted)
        msgs = []
        # Parameters: Type(0=Note), Chan(0), NoteNum, MinVel(0), MaxVel(127)
        config_values = [0, 0, note_num, 0, 127]
        for offset, val in enumerate(config_values):
            msgs.append(self.build_packet(addr + offset, 8, val, mode=0x49))
        return msgs