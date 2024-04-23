import os
import statistics
from l1_cache import L1Cache
from l2_cache import L2Cache
from dram import DRAM

#returns a ist containing all the access type, address, and data for each line
#in a dinero trace file
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

#simulates the energy consumed for L1, L2 caches and DRAM read/writes for a given list of memory accesses
#and returns the total time in seconds
def simulate_cache(addresses, l1_cache, l2_cache, dram):

    total_time = 0

    #loop through all the addresses
    #for each address
    for access_type, address, data in addresses:
        #if it is a read == '0' or instruction fetch '2'
        if access_type == '0' or access_type == '2':
            #l1 access
            hit = l1_cache.access(access_type, address, data)

            total_time += l1_cache.time_to_read_write()
            #if miss
            if not hit:
                #l2 access
                hit = l2_cache.access(access_type, address, data)

                total_time += l2_cache.time_to_read_write()
                #if miss
                if not hit:
                    #dram access
                    dram.access(access_type, address, data)

                    total_time += dram.time_to_read_write()

                    #l2 cache miss handler
                    update_dram = l2_cache.cache_miss_handler(access_type, address, data)

                    total_time += l2_cache.time_to_read_write()
                #l1 cache miss handler
                l1_cache.cache_miss_handler(access_type, address, data)

                total_time += l1_cache.time_to_read_write()
        else: #if write == '1' - write through l1 -> l2, write-back l2 -> dram
            #l1 access
            hit = l1_cache.access(access_type, address, data)

            total_time += l1_cache.time_to_read_write()
            #if miss
            if not hit:
                #l2 access
                hit = l2_cache.access(access_type, address, data)

                total_time += l2_cache.time_to_read_write()
                #if miss
                if not hit:
                    #dram access
                    dram.access(access_type, address, data)

                    total_time += dram.time_to_read_write()
                    #l2 cache miss handler
                    write_to_dram = l2_cache.cache_miss_handler(access_type, address, data)

                    total_time += l2_cache.time_to_read_write()

                    #if dirty bit - need to write to dram
                    if write_to_dram:
                        #dram access
                        dram.access(access_type, address, data)

                        total_time += dram.time_to_read_write()
                #l1 cache miss handler
                l1_cache.cache_miss_handler(access_type, address, data)

                total_time += l1_cache.time_to_read_write()
            else: #if hit
                #l2 access - write to l2, immediate write thorugh with l1 write
                hit = l2_cache.access(access_type, address, data)

                total_time += l2_cache.time_to_read_write()
                #if miss
                if not hit:
                    #dram access
                    dram.access(access_type, address, data)

                    total_time += dram.time_to_read_write()

                    #l2 cache miss handler - write-back only if replaced cache line hasn't been written to dram yet
                    write_to_dram = l2_cache.cache_miss_handler(access_type, address, data)

                    total_time += l2_cache.time_to_read_write()

                    #if dirty bit - need to write to dram
                    if write_to_dram:
                        #dram access
                        dram.access(access_type, address, data)

                        total_time += dram.time_to_read_write()
    return total_time

def main():
    directory = 'Traces/Spec_Benchmark'

    # List all files and directories in the specified directory
    asc = [2,4,8]
    for filename in os.listdir(directory):
        #Check if the entry is a file
        if os.path.isfile(os.path.join(directory, filename)):
            print("OUTPUT FOR TRACE FILE:", filename)
            filename = directory + "/" + filename

            for associativity in asc:
                # Define memory subsystem parameters
                l1_instr_size = 32 * 1024  # 32 KB
                l1_data_size = 32 * 1024  # 32 KB
                l2_size = 256 * 1024  # 256 KB
                block_size = 64  # 64 bytes
                l1_cache_read_write_time = 0.5  # in ns
                l1_cache_idle_power = 0.5  # in W
                l1_cache_active_power = 1  # in W
                l2_cache_read_write_time = 5  # in ns
                l2_transfer_energy = 5 # 5pJ
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
                                l2_cache_idle_power, l2_cache_active_power, l2_transfer_energy, l1_cache_idle_power, dram_idle_power)
                dram = DRAM(dram_access_time, dram_idle_power, dram_active_power, dram_transfer_energy, l1_cache_idle_power, l2_cache_idle_power)

                # Read addresses from trace file
                addresses = read_addresses(filename)

                time = simulate_cache(addresses, l1_cache, l2_cache, dram)
                energy = l1_cache.energy_consumed + l2_cache.energy_consumed + dram.energy_consumed

                print("SIMULATION COMPLETE")
                print("L2 Associativity: ", associativity)
                print("Total time:", time * 1e9, "ns")
                print("Total energy consumption", energy, "J")
                print()
                print("L1 cache energy consumption", l1_cache.energy_consumed, "J")
                print("L1 data cache energy consumption", l1_cache.data_energy_consumed, "J")
                print("L1 total data cache access:", l1_cache.data_access_count)
                print("L1 data cache misses:", l1_cache.data_miss_count)
                print("L1 instruction cache energy consumption", l1_cache.instruction_energy_consumed, "J")
                print("L1 total instruction cache access:", l1_cache.instruction_access_count)
                print("L1 instruction cache misses:", l1_cache.instruction_miss_count)
                print()
                print("L2 cache energy consumption", l2_cache.energy_consumed, "J")
                print("L2 total access:", l2_cache.access_count)
                print("L2 cache misses:", l2_cache.miss_count)
                print()
                print("DRAM energy consumption", dram.energy_consumed, "J")
                print("DRAM total access:", dram.access_count)
                print()

        print()
        print()


if __name__ == "__main__":
    main()
