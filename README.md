To run run.sh and the cache simulator:

Python must be installed to run the program

The program assumes that there is a folder ‘Traces’ in the same directory as the cache_sim. 
The ‘Traces’ folder also contains a folder ‘Spec_Benchmark’ that contains all the .din trace files 

To change the trace file directory path, change cache_sim.py line 115 in the main method

l1_cache.py, l2_cache.py, and dram.py must be in the same directory as cache_sim.py, these paths can be changed in the imports for cache_sim.py

If permission is denied to run the script file, execute 'chmod +x run.sh'

Each trace file output the data for a L2 associtavity of 2, 4 and 8 and the information is what was specified on ed discussion post #167

Each trace file output the data for a L2 associtavity of 2, 4 and 8 and the information is what was specified on ed discussion post #167

Example output:

OUTPUT FOR TRACE FILE: 048.ora.din

SIMULATION COMPLETE

L2 Associativity:  2

Total time: 827748.9999829654 ns

Total energy consumption 0.0024362131350079484 J


L1 cache energy consumption 0.0013007644000086022 J

L1 data cache energy consumption 0.00026060190000089977 J

L1 total data cache access: 200231

L1 data cache misses: 232

L1 instruction cache energy consumption 0.0010401625000066724 J

L1 total instruction cache access: 799771

L1 instruction cache misses: 354



L2 cache energy consumption 0.000991471854999346 J

L2 total access: 59529

L2 cache misses: 542



DRAM energy consumption 0.00014397687999999988 J

DRAM total access: 542



SIMULATION COMPLETE

L2 Associativity:  4

Total time: 827748.9999829654 ns

Total energy consumption 0.0024362131350079484 J



L1 cache energy consumption 0.0013007644000086022 J

L1 data cache energy consumption 0.00026060190000089977 J

L1 total data cache access: 200231

L1 data cache misses: 232

L1 instruction cache energy consumption 0.0010401625000066724 J

L1 total instruction cache access: 799771

L1 instruction cache misses: 354



L2 cache energy consumption 0.000991471854999346 J

L2 total access: 59529


L2 cache misses: 542



DRAM energy consumption 0.00014397687999999988 J

DRAM total access: 542



SIMULATION COMPLETE

L2 Associativity:  8

Total time: 827748.9999829654 ns

Total energy consumption 0.0024362131350079484 J



L1 cache energy consumption 0.0013007644000086022 J

L1 data cache energy consumption 0.00026060190000089977 J

L1 total data cache access: 200231

L1 data cache misses: 232

L1 instruction cache energy consumption 0.0010401625000066724 J

L1 total instruction cache access: 799771

L1 instruction cache misses: 354



L2 cache energy consumption 0.000991471854999346 J

L2 total access: 59529

L2 cache misses: 542



DRAM energy consumption 0.00014397687999999988 J

DRAM total access: 542
