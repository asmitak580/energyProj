import random
import time
from cache import Cache, L1Cache, L2Cache, DRAM

# Class definitions for Cache and L1Cache
# You can use the previously defined Cache class and modify it for L1Cache as necessary

# Class definition for L2Cache
# Similar to L1Cache but with different size, associativity, and energy consumption parameters

# Class definition for DRAM
# DRAM class to simulate memory access time and energy consumption


def read_addresses(trace_file):
    addresses = []
    with open(trace_file, 'r', encoding='ascii') as file:
        for line in file:
            if line.startswith(' ') or line.startswith('\n'):
                continue
            parts = line.split()
            if parts[0] == 'r' or parts[0] == 'w':
                address = int(parts[1], 16)
                addresses.append((parts[0], address))
    return addresses


def simulate_cache(addresses, l1_cache, l2_cache, dram):
    clock_cycles = 0
    # print("starting cache simulator")
    for access_type, address in addresses:
        # Simulate L1 cache access
        # print("current line access type: ", access_type)
        # print("current line address: ", address)
        l1_hit = l1_cache.access(address, access_type == 'w')
        if not l1_hit:
            l2_hit = l2_cache.access(address, access_type == 'w')
            if not l2_hit:
                dram_access_time = dram.access(address)
                clock_cycles += dram_access_time
            else:
                clock_cycles += l2_cache.cache.read_time
        else:
            clock_cycles += l1_cache.cache.read_time

        # Advance clock cycle
        clock_cycles += 1  # Assuming each access takes 1 cycle (2GHz processor)

    return clock_cycles


def main():
    # Define cache and memory parameters
    l1_cache_size = 32 * 1024  # 32KB
    l1_block_size = 64  # bytes
    l1_read_time = 0.5  # ns
    l1_write_time = 0.5  # ns
    l1_idle_power = 0.5  # W
    l1_active_power = 1  # W
    l1_associativity = 1  # Direct-mapped

    l2_cache_size = 256 * 1024  # 256KB
    l2_block_size = 64  # bytes
    l2_read_time = 5  # ns
    l2_write_time = 5  # ns
    l2_idle_power = 0.8  # W
    l2_active_power = 2  # W
    l2_associativity = 4  # Set-associative with set associativity of 4

    dram_read_time = 50  # ns
    dram_write_time = 50  # ns
    dram_idle_power = 0.8  # W
    dram_active_power = 4  # W
    dram_transfer_energy = 640  # in pJ

    # Create cache and memory objects
    l1_cache = L1Cache(l1_cache_size, l1_block_size, l1_read_time, l1_write_time,
                       l1_idle_power, l1_active_power)
    l2_cache = L2Cache(l2_cache_size, l2_associativity, l2_block_size, l2_read_time, l2_write_time,
                       l2_idle_power, l2_active_power)
    dram = DRAM(dram_read_time, dram_write_time, dram_idle_power, dram_active_power, dram_transfer_energy)

    # Read addresses from trace file
    trace_file = "Traces/Spec_Benchmark/008.espresso.din"
    addresses = read_addresses(trace_file)
    print("ADDRESS AFTER READING FILE")
    print(addresses)
    # Simulate cache environment
    start_time = time.time()
    clock_cycles = simulate_cache(addresses, l1_cache, l2_cache, dram)
    end_time = time.time()

    # Calculate simulation time
    simulation_time = end_time - start_time

    # Calculate energy consumption
    total_l1_energy = l1_cache.cache.energy_consumed
    total_l2_energy = l2_cache.cache.energy_consumed
    total_dram_energy = dram.energy_consumed

    # Calculate power consumption (assuming simulation time is in seconds)
    l1_power = (total_l1_energy / simulation_time) + l1_cache.cache.idle_power
    l2_power = (total_l2_energy / simulation_time) + l2_cache.cache.idle_power
    dram_power = (total_dram_energy / simulation_time) + dram.idle_power

    print("Simulation completed.")
    print("Total clock cycles:", clock_cycles)
    print("Simulation time:", simulation_time, "seconds")
    print("L1 Cache power consumption:", l1_power, "W")
    print("L2 Cache power consumption:", l2_power, "W")
    print("DRAM power consumption:", dram_power, "W")


if __name__ == "__main__":
    main()
