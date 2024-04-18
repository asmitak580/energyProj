import random

class L2Cache:
    def __init__(self, size, associativity, block_size, read_write_time, idle_power, active_power, transfer_energy, l1_cache_idle_power, dram_idle_power):
        self.size = size  # in bytes
        self.associativity = associativity
        self.block_size = block_size
        self.read_write_time = read_write_time / 1e9  # convert to seconds
        self.idle_power = idle_power  # in W
        self.active_power = active_power  # in W
        self.transfer_energy = transfer_energy / (1 * 1e12) # in W
        self.l1_cache_idle_power = l1_cache_idle_power
        self.dram_idle_power = dram_idle_power
        self.num_sets = size // (associativity * block_size)
        self.cache = [[] for _ in range(self.num_sets)]
        self.energy_consumed = 0.0

    def access(self, access_type, address, data=None):
        tag, index, _ = self.extract_address(address)
        set_cache = self.cache[index]
        for block in set_cache:
            if block[0] == tag:  # tag match, cache hit
                if access_type == '1':  # Write access
                    block[1] = True  # Mark the block as dirty
                    self.energy_consumed += self.write_energy()
                else:
                    self.energy_consumed += self.read_energy()
                return True

        # Cache miss
        if access_type == '1':  # Write access
            self.energy_consumed += self.write_energy()
        else:
            self.energy_consumed += self.read_energy()

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

        return False

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
        return self.read_write_time * (self.active_power + self.transfer_energy + self.l1_cache_idle_power + self.dram_idle_power)

    def write_energy(self):
        return self.read_write_time * (self.active_power + self.transfer_energy + self.l1_cache_idle_power + self.dram_idle_power)
    
    #return time it takes to read/write in seconds
    def time_to_read_write(self):
        return self.read_write_time
    
    #return power used by dram for memory accesses in W
    def l2_access_power(self):
        return self.active_power + self.transfer_energy

    @staticmethod
    def log2(x):
        return x.bit_length() - 1 if x > 0 else 0
