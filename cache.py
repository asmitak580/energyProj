import random

class Cache:
    def __init__(self, size, associativity, block_size, read_time, write_time, idle_power, active_power):
        self.size = size  # in bytes
        self.associativity = associativity
        self.block_size = block_size
        self.read_time = read_time  # in ns
        self.write_time = write_time  # in ns
        self.idle_power = idle_power  # in W
        self.active_power = active_power  # in W
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
        tag_bits = 64 - (self.log2(self.num_sets) + self.log2(self.block_size))
        index_bits = self.log2(self.num_sets)
        tag = address >> (index_bits + self.log2(self.block_size))
        index = (address >> self.log2(self.block_size)) & ((1 << index_bits) - 1)
        return tag, index, address

    def read_energy(self):
        return self.read_time * self.active_power

    def write_energy(self):
        return self.write_time * self.active_power

    @staticmethod
    def log2(x):
        return x.bit_length() - 1 if x > 0 else 0

class DRAM:
    def __init__(self, read_time, write_time, idle_power, active_power, transfer_energy):
        self.read_time = read_time  # in ns
        self.write_time = write_time  # in ns
        self.idle_power = idle_power  # in W
        self.active_power = active_power  # in W
        self.transfer_energy = transfer_energy  # in pJ
        self.energy_consumed = 0.0

    def access(self, access_type, address, data=None):
        if access_type == '1':  # Write access
            self.energy_consumed += self.write_energy()
        else:
            self.energy_consumed += self.read_energy()

        # Add transfer energy for memory access
        self.energy_consumed += self.transfer_energy

        # Simulate memory access time
        return self.write_time if access_type == '1' else self.read_time

    def read_energy(self):
        return self.active_power * self.read_time * 1e-9  # Convert ns to seconds

    def write_energy(self):
        return self.active_power * self.write_time * 1e-9  # Convert ns to seconds

# L1 Cache: Direct-mapped for Instructions and Data
class L1Cache:
    def __init__(self, size, block_size, read_time, write_time, idle_power, active_power):
        self.cache = Cache(size, 1, block_size, read_time, write_time, idle_power, active_power)

    def access(self, address, is_write=False):
        return self.cache.access(address, is_write)

    def access_instruction(self, address):
        # Instruction fetch is read-only, so is_write is set to False
        return self.cache.access(address, False)

# L2 Cache: Set-associative
class L2Cache:
    def __init__(self, size, associativity, block_size, read_time, write_time, idle_power, active_power):
        self.cache = Cache(size, associativity, block_size, read_time, write_time, idle_power, active_power)

    def access(self, address, is_write=False):
        return self.cache.access(address, is_write)
