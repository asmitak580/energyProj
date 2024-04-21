import os
from l1_cache import L1Cache
from l2_cache import L2Cache
from dram import DRAM


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
    # clock_cycles = 0
    total_access_time = 0 #nsec
    total_energy_consumed = 0
    total_power = 0
    l1_misses = 0
    l2_misses = 0
    for access_type, address, data in addresses:
        # print("current access_type:", access_type)
        # print("current addy:", address)
        # cur_access_time = 0 #nsec
        cur_energy_consumed = 0
        # cur_access_power = 0
        if access_type == '0':  # Read access
            cur_energy_consumed += l1_cache.read_energy()
            # cur_access_time += 0.5
            # cur_access_power += 1 +  0.8 + 0.8 # active l1 and idle l2, dram in W
            l1_hit = l1_cache.access(access_type, address)
            if not l1_hit:
                # print("L1 cache miss read")
                l1_misses += 1
                cur_energy_consumed += l2_cache.read_energy()
                # cur_access_time += 5
                # cur_access_power += 2 + (5 / (1 * 1e12)) + 0.5 + 0.8 #active l2 plus 5pJ plus idle for l1 and dram
                l2_hit = l2_cache.access(access_type, address)
                if not l2_hit:
                    # print("L2 cache miss read")
                    l2_misses += 1
                    # cur_access_time += 50
                    # cur_access_power += 4 + (640 / (1 * 1e12)) + 0.5 + 0.8 #active dram and transfer plus idle l1 and l2
                    cur_energy_consumed += dram.access('0', address)  # Read access to DRAM
        elif access_type == '1':  # Write access
            cur_energy_consumed += l1_cache.write_energy()
            # cur_access_time += 0.5 + 0.5
            # cur_access_power += 1 + 1 + 0.8 + 0.8 # active l1 and idle l2, dram in W
            l1_hit = l1_cache.access(access_type, address)
            if not l1_hit:
                # print("L1 cache miss write")
                l1_misses += 1
                cur_energy_consumed += l2_cache.write_energy()
                # cur_access_time += 5 + 5
                # cur_access_power += 2 + (5 / (1 * 1e12)) + 2 + (5 / (1 * 1e12)) + 0.5 + 0.8 #active l2 plus 5pJ plus idle for l1 and dram
                l2_hit = l2_cache.access(access_type, address)
                if not l2_hit:
                    # print("L2 cache miss write")
                    l2_misses += 1
                    # cur_access_time += 50 + 50
                    # cur_access_power += 4 + (640 / (1 * 1e12)) + 4 + (640 / (1 * 1e12)) + 0.5 + 0.8 #active dram and transfer plus idle l1 and l2
                    cur_energy_consumed += dram.access('1', address)  # Write access to DRAM
        elif access_type == '2':  # Instruction fetch
            cur_energy_consumed += l1_cache.read_energy()
            # cur_access_time += 0.5
            # cur_access_power += 1 +  0.8 + 0.8 # active l1 and idle l2, dram in W
            l1_hit = l1_cache.access(access_type, address)
            if not l1_hit:
                # print("L1 cache miss instr")
                l1_misses += 1
                cur_energy_consumed += l2_cache.read_energy()
                # cur_access_time += 5
                # cur_access_power += 2 + (5 / (1 * 1e12)) + 0.5 + 0.8 #active l2 plus 5pJ plus idle for l1 and dram
                l2_hit = l2_cache.access(access_type, address)
                if not l2_hit:
                    # print("L2 cache miss instr")
                    l2_misses += 1
                    # cur_access_time += 50
                    # cur_access_power += 4 + (640 / (1 * 1e12)) + 0.5 + 0.8 #active dram and transfer plus idle l1 and l2
                    cur_energy_consumed += dram.access('0', address)  # Read access to DRAM

        total_energy_consumed += cur_energy_consumed
        # total_access_time += cur_access_time
        # total_power += cur_access_power

    return total_energy_consumed, total_access_time, total_power, l1_misses, l2_misses

def new_simulate_cache(addresses, l1_cache, l2_cache, dram):
    total_l1_energy = 0
    total_l2_energy = 0
    total_dram_energy = 0
    total_energy = 0
    total_time = 0
    l1_misses = 0
    l2_misses = 0
    #loop through all the addresses
    #for each address
    for access_type, address, data in addresses:
        #if it is a read == '0' or instruction fetch '2'
        if access_type == '0' or access_type == '2':
            #l1 access
            hit, l1_active_energy = l1_cache.access(access_type, address, data)

            total_l1_energy += l1_active_energy
            total_energy += l1_active_energy
            total_time += l1_cache.time_to_read_write()
            #if miss
            if not hit:
                l1_misses += 1
                #l2 access
                hit, l2_active_energy = l2_cache.access(access_type, address, data)

                total_l2_energy += l2_active_energy
                total_energy += l2_active_energy
                total_time += l2_cache.time_to_read_write()
                #if miss
                if not hit:
                    l2_misses += 1
                    #dram access
                    dram_active_energy = dram.access(access_type, address, data)

                    total_dram_energy += dram_active_energy
                    total_energy += dram_active_energy
                    total_time += dram.time_to_read_write()

                    #l2 cache miss handler
                    update_dram, l2_cache_miss_energy = l2_cache.cache_miss_handler(access_type, address, data)

                    total_l2_energy += l2_cache_miss_energy
                    total_energy += l2_cache_miss_energy
                    total_time += l2_cache.time_to_read_write()
                #l1 cache miss handler
                l1_cache_miss_energy = l1_cache.cache_miss_handler(access_type, address, data)

                total_l1_energy += l1_cache_miss_energy
                total_energy += l1_cache_miss_energy
                total_time += l1_cache.time_to_read_write()
        else: #if write == '1' - write through l1 -> l2, write-back l2 -> dram
            #l1 access
            hit, l1_active_energy = l1_cache.access(access_type, address, data)

            total_l1_energy += l1_active_energy
            total_energy += l1_active_energy
            total_time += l1_cache.time_to_read_write()
            #if miss
            if not hit:
                l1_misses += 1
                #l2 access
                hit, l2_active_energy = l2_cache.access(access_type, address, data)

                total_l2_energy += l2_active_energy
                total_energy += l2_active_energy
                total_time += l2_cache.time_to_read_write()
                #if miss
                if not hit:
                    l2_misses += 1
                    #dram access
                    dram_active_energy = dram.access(access_type, address, data)

                    total_dram_energy += dram_active_energy
                    total_energy += dram_active_energy
                    total_time += dram.time_to_read_write()
                    #l2 cache miss handler
                    write_to_dram, l2_cache_miss_energy = l2_cache.cache_miss_handler(access_type, address, data)

                    total_l2_energy += l2_cache_miss_energy
                    total_energy += l2_cache_miss_energy
                    total_time += l2_cache.time_to_read_write()

                    #if dirty bit - need to write to dram
                    if write_to_dram:
                        #dram access
                        dram_active_energy = dram.access(access_type, address, data)

                        total_dram_energy += dram_active_energy
                        total_energy += dram_active_energy
                        total_time += dram.time_to_read_write()
                #l1 cache miss handler
                l1_cache_miss_energy = l1_cache.cache_miss_handler(access_type, address, data)

                total_l1_energy += l1_cache_miss_energy
                total_energy += l1_cache_miss_energy
                total_time += l1_cache.time_to_read_write()
            else: #if hit
                #l2 access - write to l2, immediate write thorugh with l1 write
                hit, l2_active_energy = l2_cache.access(access_type, address, data)

                total_l2_energy += l2_active_energy
                total_energy += l2_active_energy
                total_time += l2_cache.time_to_read_write()
                #DO WE NEED THIS CHECK OR CAN WE ASSUME IF IT IS IN L2 CACHE SINCE IT WAS IN L1
                #if miss
                if not hit:
                    l2_misses += 1
                    #dram access
                    dram_active_energy = dram.access(access_type, address, data)

                    total_dram_energy += dram_active_energy
                    total_energy += dram_active_energy
                    total_time += dram.time_to_read_write()

                    #l2 cache miss handler - write-back only if replaced cache line hasn't been written to dram yet
                    write_to_dram, l2_cache_miss_energy = l2_cache.cache_miss_handler(access_type, address, data)

                    total_l2_energy += l2_cache_miss_energy
                    total_energy += l2_cache_miss_energy
                    total_time += l2_cache.time_to_read_write()

                    #if dirty bit - need to write to dram
                    if write_to_dram:
                        #dram access
                        dram_active_energy = dram.access(access_type, address, data)

                        total_dram_energy += dram_active_energy
                        total_energy += dram_active_energy
                        total_time += dram.time_to_read_write()



    return total_energy, total_time, total_l1_energy, total_l2_energy, total_dram_energy, l1_misses, l2_misses

def main():
    directory = 'Traces/Spec_Benchmark'
    filename = "Traces/Spec_Benchmark/048.ora.din" 
    print("Output for trace file:", filename)
    # Define memory subsystem parameters
    l1_instr_size = 32 * 1024  # 32 KB
    l1_data_size = 32 * 1024  # 32 KB
    l2_size = 256 * 1024  # 256 KB
    associativity = 4
    block_size = 64  # 64 bytes
    # dram_size = 8 * 1024 * 1024 * 1024  # 8GB
    l1_cache_read_write_time = 0.5  # in ns
    l1_cache_idle_power = 0.5  # in W
    l1_cache_active_power = 1  # in W
    l2_cache_read_write_time = 5  # in ns
    l2_access_cost = 5 # 5pJ
    l2_cache_idle_power = 0.8  # in W
    l2_cache_active_power = 2  # in W
    dram_access_time = 50  # in ns
    dram_idle_power = 0.8  # in W
    dram_active_power = 4  # in W
    dram_transfer_energy = 640  # in pJ

    # Create cache and memory objects
    l1_cache = L1Cache(l1_data_size, l1_instr_size, block_size, l1_cache_read_write_time,
                    l1_cache_idle_power, l1_cache_active_power, l2_cache_idle_power, dram_idle_power)
    l2_cache = L2Cache(l2_size, associativity, block_size, l2_cache_read_write_time,
                    l2_cache_idle_power, l2_cache_active_power, l2_access_cost, l1_cache_idle_power, dram_idle_power)
    dram = DRAM(dram_access_time, dram_idle_power, dram_active_power, dram_transfer_energy, l1_cache_idle_power, l2_cache_idle_power)

    # Read addresses from trace file
    addresses = read_addresses(filename)

    energy, time, l1_energy, l2_energy, dram_energy, l1_miss, l2_miss = new_simulate_cache(addresses, l1_cache, l2_cache, dram)

    print("Simulation completed.")
    print("Total time:", time * 1e9, "ns")
    # print("Total power consumption:", power, "W")
    print("Total energy consumption", energy, "J")
    print("L1 cache energy consumption", l1_energy, "J")
    print("L2 cache energy consumption", l2_energy, "J")
    print("DRAM energy consumption", dram_energy, "J")
    print("L1 misses:", l1_miss)
    print("L2 misses:", l2_miss)
    print()

    # List all files and directories in the specified directory
    # for filename in os.listdir(directory):
    #     # Check if the entry is a file
    #     if os.path.isfile(os.path.join(directory, filename)):
    #     #  filename = "048.ora.din"
    #         print("Output for trace file:", filename)
    #         filename = "Traces/Spec_Benchmark/" + filename
    #         # Define memory subsystem parameters
    #         l1_instr_size = 32 * 1024  # 32 KB
    #         l1_data_size = 32 * 1024  # 32 KB
    #         l2_size = 256 * 1024  # 256 KB
    #         associativity = 4
    #         block_size = 64  # 64 bytes
    #         # dram_size = 8 * 1024 * 1024 * 1024  # 8GB
    #         l1_cache_read_write_time = 0.5  # in ns
    #         l1_cache_idle_power = 0.5  # in W
    #         l1_cache_active_power = 1  # in W
    #         l2_cache_read_write_time = 5  # in ns
    #         l2_access_cost = 5 # 5pJ
    #         l2_cache_idle_power = 0.8  # in W
    #         l2_cache_active_power = 2  # in W
    #         dram_access_time = 50  # in ns
    #         dram_idle_power = 0.8  # in W
    #         dram_active_power = 4  # in W
    #         dram_transfer_energy = 640  # in pJ

    #         # Create cache and memory objects
    #         l1_cache = L1Cache(l1_data_size, l1_instr_size, block_size, l1_cache_read_write_time,
    #                         l1_cache_idle_power, l1_cache_active_power, l2_cache_idle_power, dram_idle_power)
    #         l2_cache = L2Cache(l2_size, associativity, block_size, l2_cache_read_write_time,
    #                         l2_cache_idle_power, l2_cache_active_power, l2_access_cost, l1_cache_idle_power, dram_idle_power)
    #         dram = DRAM(dram_access_time, dram_idle_power, dram_active_power, dram_transfer_energy, l1_cache_idle_power, l2_cache_idle_power)

    #         # Read addresses from trace file
    #         addresses = read_addresses(filename)

    #         energy, time, l1_energy, l2_energy, dram_energy = new_simulate_cache(addresses, l1_cache, l2_cache, dram)

    #         print("Simulation completed.")
    #         print("Total time:", time, "s")
    #         # print("Total power consumption:", power, "W")
    #         print("Total energy consumption", energy, "J")
    #         print("L1 cache energy consumption", l1_energy)
    #         print("L2 cache energy consumption", l2_energy)
    #         print("DRAM energy consumption", dram_energy)
    #         print()


if __name__ == "__main__":
    main()
