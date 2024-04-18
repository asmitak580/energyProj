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
        self.data_cache = [[CacheLine() for _ in range(self.num_data_sets)]]
        self.num_instr_sets = data_size // (block_size)
        self.instruction_cache = [[CacheLine() for _ in range(self.num_instr_sets)]]
        self.energy_consumed = 0.0

    def access(self, access_type, address, data=None):
        

        if access_type == '1': #it's a write, check both caches
            # for block in self.instruction_cache:
            cache_line = self.instruction_cache[index]
            if cache_line.tag == tag:
                cache_line.dirt = True
                self.energy_consumed += self.write_energy()
                return True, self.energy_consumed
            # for block in self.data_cache:
            set_cache = self.data_cache[index]
            for cache_line in set_cache:
                if cache_line.tag == tag:
                    cache_line.dirty = True
                    self.energy_consumed += self.write_energy()
                    return True, self.energy_consumed
        else: #it is a read
            if access_type == '2':  # Instruction fetch
                tag, index, _ = self.extract_address(address)
                set_cache = self.instruction_cache[index]
            else:  # Data read or write
                tag, index, _ = self.extract_address(address)
                set_cache = self.data_cache[index]
        
            for cache_line in set_cache:
                if cache_line.tag == tag:  # tag match, cache hit
                    self.energy_consumed += self.read_energy()
                    return True, self.energy_consumed
        return False, self.energy_consumed
    
    def cache_miss_handler(self, access_type, address, data=None):
        # Cache miss
        if access_type == '2':  # Instruction fetch
            tag, index, _ = self.extract_address(address)
            set_cache = self.instruction_cache[index]
        else:  # Data read or write
            tag, index, _ = self.extract_address(address)
            set_cache = self.data_cache[index]

        if access_type == '1':  # Write access
            self.energy_consumed += self.write_energy()
        else:  # Read access
            self.energy_consumed += self.read_energy()

        #random cache replacement policy
        if len(set_cache) < self.associativity:  # if set is not full
            set_cache.append([tag, True])  # Append a new block and mark it as dirty
        else:
            # Apply random replacement policy
            random_index = random.randint(0, self.associativity - 1)
            replaced_block = set_cache[random_index]
            if replaced_block[1]:  # If the replaced block is dirty, write it back to the next level
                self.energy_consumed += self.write_energy()
                replaced_block[1] = False  # Mark the replaced block as clean
            set_cache[random_index] = [tag, True]  # Replace the block and mark it as dirty
        
        return self.energy_consumed


    def extract_address(self, address):
        index_bits = self.log2(self.num_sets)
        block_offset_bits = self.log2(self.block_size)
        tag_bits = 64 - index_bits - block_offset_bits
        
        # print("ADDY: ", address)
        # print("Index Bits:", index_bits)
        # print("Block Offset Bits:", block_offset_bits)
        # print("Tag Bits:", tag_bits)
        
        tag = address >> (index_bits + block_offset_bits)
        index = (address >> block_offset_bits) & ((1 << index_bits) - 1)
        
        # print("Tag:", tag)
        # print("Index:", index)
        
        return tag, index, address

    def read_energy(self):
        return self.read_write_time * (self.active_power + self.l2_cache_idle_power + self.dram_idle_power)

    def write_energy(self):
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
    def __init__(self, tag=None, dirty=False):
        self.tag = tag
        self.dirty = dirty