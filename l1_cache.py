import random

class L1Cache:
    def __init__(self, data_size, instruction_size, block_size, read_write_time, idle_power, active_power, l2_cache_idle_power, dram_idle_power):
        self.data_size = data_size  # in bytes
        self.instruction_size = instruction_size
        self.block_size = block_size
        self.read_write_time = read_write_time / 1e9  # convert to seconds
        self.idle_power = idle_power  # in W
        self.active_power = active_power  # in W
        self.l2_cache_idle_power = l2_cache_idle_power
        self.dram_idle_power = dram_idle_power
        self.num_data_sets = data_size // (block_size)
        self.data_cache = [CacheLine() for _ in range(self.num_data_sets)]
        self.num_instr_sets = data_size // (block_size)
        self.instruction_cache = [CacheLine() for _ in range(self.num_instr_sets)]

    #accessing a address in the cache, returns if it was a miss or hit and the energy consumed
    def access(self, access_type, address, data=None):
        tag, index, _ = self.extract_address(address)
        if access_type == '2':  # Instruction fetch
            cache_line = self.instruction_cache[index]
        else:  # Data read or write
            cache_line = self.data_cache[index]

        if access_type == '1': #it's a write      
            cache_line = self.data_cache[index]
            if cache_line.tag == tag:
                return True, self.read_write_energy()
        else: #it is a read
            if cache_line.tag == tag:  # tag match, cache hit
                return True, self.read_write_energy()
        return False, self.read_write_energy()
    
    #handles putting an address in the cache and writing to it if there was a miss
    def cache_miss_handler(self, access_type, address, data=None):
        # Cache miss
        tag, index, _ = self.extract_address(address)
        if access_type == '2':  # Instruction fetch
            set_cache = self.instruction_cache
        else:  # Data read or write
            set_cache = self.data_cache

        replaced_cache_line = set_cache[index]

        # Update cache line with new tag
        replaced_cache_line.tag = tag
        # replaced_cache_line.dirty = (access_type == '1')  # Set dirty bit if it's a write access
        
        return self.read_write_energy()

    #returns the tag and index for a memory address
    def extract_address(self, address):
        index_bits = self.log2(self.num_data_sets)
        block_offset_bits = self.log2(self.block_size)
        tag = address >> (index_bits + block_offset_bits)
        index = (address >> block_offset_bits) & ((1 << index_bits) - 1)
        
        return tag, index, address

    #return the active L1 energy consumption with idle L2 and DRAM
    def read_write_energy(self):
        return self.read_write_time * (self.active_power + self.l2_cache_idle_power + self.dram_idle_power)
    
    #return time it takes to read/write in seconds
    def time_to_read_write(self):
        return self.read_write_time
    
    #return power used by dram for memory accesses in W
    def l1_access_power(self):
        return self.active_power

    @staticmethod
    def log2(x):
        return x.bit_length() - 1 if x > 0 else 0
    
class CacheLine:
    def __init__(self, tag=None):
        self.tag = tag
