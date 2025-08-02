"""
A Python wrapper for the cubiomes C library using ctypes.

This module provides access to Minecraft biome and structure generation functions
from the cubiomes library.

To use this module, you must first compile the C library into a shared object,
for example by running `make` or `cmake . && make` in the root directory.

This wrapper does not cover all the functions available in cubiomes, but it
provides the foundation for extending it further.
"""

import ctypes
from ctypes import c_int, c_uint32, c_uint64, c_byte, POINTER, byref
import os

# Load the shared library
# Assuming the script is run from the root of the cubiomes directory
lib_path = os.path.abspath("build/libcubiomes.so")
try:
    cubiomes = ctypes.CDLL(lib_path)
except OSError as e:
    print(f"Error loading library at '{lib_path}'")
    print("Please make sure you have compiled the library (e.g., 'make' or 'cmake . && make')")
    exit(1)

# ==============================================================================
# Enums and Constants
# ==============================================================================

# MCVersion enum from biomes.h
MC_1_18 = 29

# Dimension enum from biomes.h
DIM_NETHER = -1
DIM_OVERWORLD = 0
DIM_END = 1

# BiomeID enum from biomes.h
ocean = 0
plains = 1
desert = 2
mountains = 3
forest = 4
taiga = 5
swamp = 6
river = 7
nether_wastes = 8
the_end = 9
frozen_ocean = 10
frozen_river = 11
snowy_tundra = 12
snowy_mountains = 13
mushroom_fields = 14
mushroom_field_shore = 15
beach = 16
desert_hills = 17
wooded_hills = 18
taiga_hills = 19
mountain_edge = 20
jungle = 21
jungle_hills = 22
jungle_edge = 23
deep_ocean = 24
stone_shore = 25
snowy_beach = 26
birch_forest = 27
birch_forest_hills = 28
dark_forest = 29
snowy_taiga = 30
snowy_taiga_hills = 31
giant_tree_taiga = 32
giant_tree_taiga_hills = 33
wooded_mountains = 34
savanna = 35
savanna_plateau = 36
badlands = 37
wooded_badlands_plateau = 38
badlands_plateau = 39
warm_ocean = 44
lukewarm_ocean = 45
cold_ocean = 46
deep_warm_ocean = 47
deep_lukewarm_ocean = 48
deep_cold_ocean = 49
deep_frozen_ocean = 50
the_void = 127
meadow = 177
grove = 178
snowy_slopes = 179
jagged_peaks = 180
frozen_peaks = 181
stony_peaks = 182

# StructureType enum from finders.h
Feature = 0
Desert_Pyramid = 1
Jungle_Temple = 2
Swamp_Hut = 3
Igloo = 4
Village = 5
Ocean_Ruin = 6
Shipwreck = 7
Monument = 8
Mansion = 9
Outpost = 10
Ruined_Portal = 11
Ruined_Portal_N = 12
Ancient_City = 13
Treasure = 14
Mineshaft = 15
Desert_Well = 16
Geode = 17
Fortress = 18
Bastion = 19
End_City = 20
End_Gateway = 21
End_Island = 22
Trail_Ruins = 23
Trial_Chambers = 24


# ==============================================================================
# Structures
# ==============================================================================

GENERATOR_SIZE = 27592
class Generator(ctypes.Structure):
    """Opaque structure for the biome generator."""
    _fields_ = [("data", c_byte * GENERATOR_SIZE)]

class Pos(ctypes.Structure):
    """Represents a 2D position (x, z)."""
    _fields_ = [("x", c_int), ("z", c_int)]

# ==============================================================================
# Function Signatures
# ==============================================================================

# void setupGenerator(Generator *g, int mc, uint32_t flags);
setupGenerator = cubiomes.setupGenerator
setupGenerator.argtypes = [POINTER(Generator), c_int, c_uint32]
setupGenerator.restype = None
setupGenerator.__doc__ = "Sets up a biome generator for a given MC version."

# void applySeed(Generator *g, int dim, uint64_t seed);
applySeed = cubiomes.applySeed
applySeed.argtypes = [POINTER(Generator), c_int, c_uint64]
applySeed.restype = None
applySeed.__doc__ = "Initializes the generator for a given dimension and seed."

# int getBiomeAt(const Generator *g, int scale, int x, int y, int z);
getBiomeAt = cubiomes.getBiomeAt
getBiomeAt.argtypes = [POINTER(Generator), c_int, c_int, c_int, c_int]
getBiomeAt.restype = c_int
getBiomeAt.__doc__ = "Gets the biome for a specified scaled position."

# int getStructurePos(int structureType, int mc, uint64_t seed, int regX, int regZ, Pos *pos);
getStructurePos = cubiomes.getStructurePos
getStructurePos.argtypes = [c_int, c_int, c_uint64, c_int, c_int, POINTER(Pos)]
getStructurePos.restype = c_int
getStructurePos.__doc__ = "Finds the block position of the structure generation attempt in a given region."

# int isViableStructurePos(int structType, Generator *g, int blockX, int blockZ, uint32_t flags);
isViableStructurePos = cubiomes.isViableStructurePos
isViableStructurePos.argtypes = [c_int, POINTER(Generator), c_int, c_int, c_uint32]
isViableStructurePos.restype = c_int
isViableStructurePos.__doc__ = "Performs a biome check to determine if a structure could spawn."


# ==============================================================================
# Example Usage
# ==============================================================================

if __name__ == "__main__":
    print("Running Python wrapper for cubiomes...")
    mc_version = MC_1_18
    g = Generator()
    setupGenerator(byref(g), mc_version, 0)

    # Example 1: Find biome for a known seed
    print("\\nExample 1: Checking biome for seed 262.")
    seed = 262
    applySeed(byref(g), DIM_OVERWORLD, seed)
    biome_id = getBiomeAt(byref(g), 1, 0, 63, 0)
    if biome_id == mushroom_fields:
        print(f"  SUCCESS: Seed {seed} has biome {biome_id} (mushroom_fields) at (0, 0).")
    else:
        print(f"  FAILURE: Seed {seed} has biome {biome_id}, expected {mushroom_fields}.")

    # Example 2: Check for a structure at a known seed
    print("\\nExample 2: Checking for Buried Treasure on seed 4.")
    seed = 4
    applySeed(byref(g), DIM_OVERWORLD, seed)
    pos = Pos()
    # Check for a treasure in region (0, 0)
    if getStructurePos(Treasure, mc_version, seed, 0, 0, byref(pos)):
        print(f"  Structure position for Treasure on seed {seed} is ({pos.x}, {pos.z}).")
        if isViableStructurePos(Treasure, byref(g), pos.x, pos.z, 0):
            print("  SUCCESS: Biome is viable for Buried Treasure.")
        else:
            print("  FAILURE: Biome is not viable for Buried Treasure.")
    else:
        print(f"  FAILURE: Could not get structure position for Treasure on seed {seed}.")

    print("\\nWrapper test complete.")
