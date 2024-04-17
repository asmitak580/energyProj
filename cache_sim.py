# import random
# import time
import os
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
            parts = line.split()
            if len(parts) == 3:
                access_type = parts[0]
                address = int(parts[1], 16)
                data = int(parts[2], 16)
                addresses.append((access_type, address, data))
    return addresses


def simulate_cache(addresses, l1_cache, l2_cache, dram):
    clock_cycles = 0
    for access_type, address, data in addresses:
        if access_type == '0':  # Read access
            l1_hit = l1_cache.access(address)
            if not l1_hit:
                l2_hit = l2_cache.access(address)
                if not l2_hit:
                    clock_cycles += dram.access('0', address)  # Read access to DRAM
                else:
                    clock_cycles += l2_cache.cache.read_time
            else:
                clock_cycles += l1_cache.cache.read_time
        elif access_type == '1':  # Write access
            l1_hit = l1_cache.access(address, is_write=True)
            if not l1_hit:
                l2_hit = l2_cache.access(address, is_write=True)
                if not l2_hit:
                    clock_cycles += dram.access('1', address)  # Write access to DRAM
                else:
                    clock_cycles += l2_cache.cache.write_time
            else:
                clock_cycles += l1_cache.cache.write_time
        elif access_type == '2':  # Instruction fetch
            l1_hit = l1_cache.access_instruction(address)
            if not l1_hit:
                l2_hit = l2_cache.access(address)
                if not l2_hit:
                    clock_cycles += dram.access('0', address)  # Read access to DRAM
                else:
                    clock_cycles += l2_cache.cache.read_time
            else:
                clock_cycles += l1_cache.cache.read_time

        # Advance clock cycle
        clock_cycles += 1

    return clock_cycles


def main():
    # Define memory subsystem parameters
    l1_instr_size = 32 * 1024  # 32 KB
    l1_data_size = 32 * 1024  # 32 KB
    l2_size = 256 * 1024  # 256 KB
    associativity = 4
    block_size = 64  # 64 bytes
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
    dram_access_time = 50  # in ns
    dram_idle_power = 0.8  # in W
    dram_active_power = 4  # in W
    dram_transfer_energy = 640  # in pJ

    # Create cache and memory objects
    l1_cache = L1Cache(l1_instr_size + l1_data_size, block_size, l1_cache_read_time, l1_cache_write_time,
                       l1_cache_idle_power, l1_cache_active_power)
    l2_cache = L2Cache(l2_size, associativity, block_size, l2_cache_read_time, l2_cache_write_time,
                       l2_cache_idle_power, l2_cache_active_power)
    dram = DRAM(dram_access_time, dram_access_time, dram_idle_power, dram_active_power, dram_transfer_energy)

    # Read addresses from trace file
    trace_file = "Traces/Spec_Benchmark/008.espresso.din"
    addresses = read_addresses(trace_file)
    # print("ADDRESS AFTER READING FILE")
    # print(addresses)
    # Simulate cache environment
    # start_time = time.time()
    clock_cycles = simulate_cache(addresses, l1_cache, l2_cache, dram)
    # end_time = time.time()

    # Calculate simulation time
    # simulation_time = end_time - start_time

    total_l1_energy = l1_cache.cache.energy_consumed
    total_l2_energy = l2_cache.cache.energy_consumed
    total_dram_energy = dram.energy_consumed

    # Calculate simulation time
    simulation_time = clock_cycles * processor_cycle_time_ns

    # Calculate power consumption
    l1_power = (total_l1_energy / simulation_time) + l1_cache.cache.idle_power
    l2_power = (total_l2_energy / simulation_time) + l2_cache.cache.idle_power
    dram_power = (total_dram_energy / simulation_time) + dram.idle_power

    print("Simulation completed.")
    print("Total clock cycles:", clock_cycles)
    print("Simulation time:", simulation_time, "ns")
    print("L1 Cache power consumption:", l1_power, "W")
    print("L2 Cache power consumption:", l2_power, "W")
    print("DRAM power consumption:", dram_power, "W")
    print("Total power consumption:", dram_power + l1_power + l2_power, "W")


if __name__ == "__main__":
    main()
