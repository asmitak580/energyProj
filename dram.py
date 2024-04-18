class DRAM:
    def __init__(self, read_write_time, idle_power, active_power, transfer_energy, l1_idle, l2_idle):
        self.read_write_time = read_write_time / 1e9  # convert to seconds
        self.idle_power = idle_power  # in W
        self.active_power = active_power  # in W
        self.transfer_energy = transfer_energy  / (1 * 1e12) # in W
        self.l1_idle = l1_idle
        self.l2_idle = l2_idle
        self.energy_consumed = 0.0

    def access(self, access_type, address, data=None):
        if access_type == '1':  # Write access
            self.energy_consumed += self.write_energy()
        else:
            self.energy_consumed += self.read_energy()

        return self.energy_consumed
    
    #return energy used to read from dram including idle l1 and l2 power
    def read_energy(self):
        return (self.active_power + self.transfer_energy + self.l1_idle + self.l2_idle) * self.read_write_time  # Convert ns to seconds

    #return energy used to write from dram including idle l1 and l2 power
    def write_energy(self):
        return (self.active_power + self.transfer_energy + self.l1_idle + self.l2_idle) * self.read_write_time  # Convert ns to seconds
    
    #return time it takes to read/write in seconds
    def time_to_read_write(self):
        return self.read_write_time
    
    #return power used by dram for memory accesses in W
    def dram_access_power(self):
        return self.active_power + self.transfer_energy