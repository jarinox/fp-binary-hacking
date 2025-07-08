from PIL import Image
from src.gb import GBFile

PALETTE = [
    (0xFF, 0xFF, 0xFF),  # White
    (0xC0, 0xC0, 0xC0),  # Light Gray
    (0x40, 0x40, 0x40),  # Dark Gray
    (0x00, 0x00, 0x00),  # Black
]

def read_tile(gb_file: GBFile, index: int) -> Image.Image:
    img = Image.new('P', (8, 8))
    img.putpalette([c for color in PALETTE for c in color])
    tile_data = gb_file.read(index, 16)

    for y in range(8):
        for x in range(8):
            byte_index = y * 2
            bit_index = 7 - x
            color_index = ((tile_data[byte_index] >> bit_index) & 1) | \
                          (((tile_data[byte_index + 1] >> bit_index) & 1) << 1)
            img.putpixel((x, y), color_index)
    
    return img   
    
def write_tile(gb_file: GBFile, index: int, tile: Image.Image):
    if tile.size != (8, 8):
        raise ValueError("Tile must be 8x8 pixels")
    
    tile_data = bytearray(16)
    
    for y in range(8):
        for x in range(8):
            color_index = tile.getpixel((x, y))
            byte_index = y * 2
            bit_index = 7 - x
            
            if color_index & 1:
                tile_data[byte_index] |= (1 << bit_index)
            if color_index & 2:
                tile_data[byte_index + 1] |= (1 << bit_index)
    
    gb_file.write(index, bytes(tile_data))

def read_multi_tile(gb_file: GBFile, index: int, size: tuple, mapping: list, jump_to: list|None = None) -> Image.Image:
    img = Image.new('P', (size[0]*8, size[1]*8))
    img.putpalette([c for color in PALETTE for c in color])
    
    for i in range(size[0] * size[1]):
        if jump_to:
            if jump_to[i]:
                index = jump_to[i]
        tile = read_tile(gb_file, index + mapping[i] * 16)
        x = (i % size[0]) * 8
        y = (i // size[0]) * 8
        img.paste(tile, (x, y))
    
    return img

def write_multi_tile(gb_file: GBFile, index: int, img: Image.Image, size: tuple, mapping: list, jump_to: list|None = None):
    if img.size != (size[0] * 8, size[1] * 8):
        raise ValueError("Image size does not match the specified tile size")
    
    for i in range(size[0] * size[1]):
        if jump_to:
            if jump_to[i]:
                index = jump_to[i]
        tile = Image.new('P', (8, 8))
        tile.putpalette([c for color in PALETTE for c in color])
        
        for y in range(8):
            for x in range(8):
                color_index = img.getpixel((x + (i % size[0]) * 8, y + (i // size[0]) * 8))
                tile.putpixel((x, y), color_index)
        
        write_tile(gb_file, index + mapping[i] * 16, tile)
