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

    def access(self, address, is_write=False):
        tag, index, _ = self.extract_address(address)
        set_cache = self.cache[index]

        for block in set_cache:
            if block[0] == tag:  # tag match, cache hit
                if is_write:
                    self.energy_consumed += self.write_energy()
                else:
                    self.energy_consumed += self.read_energy()
                return True

        # Cache miss
        if is_write:
            self.energy_consumed += self.write_energy()
        else:
            self.energy_consumed += self.read_energy()

        if len(set_cache) < self.associativity:  # if set is not full
            set_cache.append((tag, address))
        else:
            # Apply random replacement policy
            random_index = random.randint(0, self.associativity - 1)
            set_cache[random_index] = (tag, address)

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
    def __init__(self, size, access_time, idle_power, active_power, transfer_energy):
        self.size = size  # in bytes
        self.access_time = access_time  # in ns
        self.idle_power = idle_power  # in W
        self.active_power = active_power  # in W
        self.transfer_energy = transfer_energy  # in pJ
        self.energy_consumed = 0.0

    def access(self, address):
        self.energy_consumed += self.access_energy()
        return self.access_time

    def access_energy(self):
        return self.transfer_energy + self.access_time * self.active_power

# L1 Cache: Direct-mapped for Instructions and Data
class L1Cache:
    def __init__(self, size, block_size, read_time, write_time, idle_power, active_power):
        self.cache = Cache(size, 1, block_size, read_time, write_time, idle_power, active_power)

    def access(self, address, is_write=False):
        return self.cache.access(address, is_write)

# L2 Cache: Set-associative
class L2Cache:
    def __init__(self, size, associativity, block_size, read_time, write_time, idle_power, active_power):
        self.cache = Cache(size, associativity, block_size, read_time, write_time, idle_power, active_power)

    def access(self, address, is_write=False):
        return self.cache.access(address, is_write)

# Example usage
l1_instr_size = 32 * 1024  # 32 KB
l1_data_size = 32 * 1024    # 32 KB
l2_size = 256 * 1024        # 256 KB
associativity = 4
block_size = 64             # 64 bytes
dram_size = 8 * 1024 * 1024 * 1024  # 8GB
processor_clock_speed = 2e9  # 2 GHz
processor_cycle_time = 1 / processor_clock_speed  # in seconds
processor_cycle_time_ns = processor_cycle_time * 1e9  # in ns
l1_cache_read_time = 0.5  # in ns
l1_cache_write_time = 0.5  # in ns
l1_cache_idle_power = 0.5  # in W
l1_cache_active_power = 1  # in W
l2_cache_read_time = 5  # in ns
l2_cache_write_time = 5  # in ns
l2_cache_idle_power = 0.8  # in W
l2_cache_active_power = 2  # in W
l2_cache_transfer_energy = 5  # in pJ
dram_access_time = 50  # in ns
dram_idle_power = 0.8  # in W
dram_active_power = 4  # in W
dram_transfer_energy = 640  # in pJ

l1_cache = L1Cache(l1_instr_size + l1_data_size, block_size, l1_cache_read_time, l1_cache_write_time, l1_cache_idle_power, l1_cache_active_power)
l2_cache = L2Cache(l2_size, associativity, block_size, l2_cache_read_time, l2_cache_write_time, l2_cache_idle_power, l2_cache_active_power)
dram = DRAM(dram_size, dram_access_time, dram_idle_power, dram_active_power, dram_transfer_energy)