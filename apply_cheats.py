import os
import shutil
from src.gb import GBFile

def unlock_all_levels(gb_file: GBFile):
    gb_file.write(0x18C, b'\x07')


if __name__ == "__main__":
    game_name = "sod"
    if not os.path.exists(f"{game_name}.gb"):
        exit(1)
    if os.path.exists(f"{game_name}.mod.gb"):
        os.remove(f"{game_name}.mod.gb")
    shutil.copyfile(f"{game_name}.gb", f"{game_name}.mod.gb")

    file = GBFile(f"{game_name}.mod.gb")
    unlock_all_levels(file)
