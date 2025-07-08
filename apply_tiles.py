from src.tile import read_tile, write_tile, read_multi_tile, write_multi_tile
from PIL import Image
from src.gb import GBFile

file = GBFile("sod.mod.gb")
#tile = read_tile(file, 0x18495)
#tile.save("tile.png")

#tile = Image.open("a_small.png")
#write_tile(file, 0x18495, tile)

dog_a = read_multi_tile(file, 0x11262, (5, 2), [0, 2, 4, 6, 8, 1, 3, 5, 7, 9])
dog_a.save("dog_a.png")

dog_b = read_multi_tile(file, 0x10C00, (3, 2), [0, 2, 0, 1, 3, 1], [0x10C00, 0x10C00, 0x111C0, 0x10C00, 0x10C00, 0x111C0])
dog_b.save("dog_b.png")

dog_c = read_multi_tile(file, 0x111E0, (4, 2), [0, 2, 4, 6, 1, 3, 5, 7])
dog_c.save("dog_c.png")

#pig_a = Image.open("pig_a.png")
#write_multi_tile(file, 0x11262, pig_a, (5, 2), [0, 2, 4, 6, 8, 1, 3, 5, 7, 9])
#pig_b = Image.open("pig_b.png")
#write_multi_tile(file, 0x10C00, pig_b, (3, 2), [0, 2, 0, 1, 3, 1], [0x10C00, 0x10C00, 0x111C0, 0x10C00, 0x10C00, 0x111C0])
#pig_c = Image.open("pig_c.png")
#write_multi_tile(file, 0x111E0, pig_c, (4, 2), [0, 2, 4, 6, 1, 3, 5, 7])
