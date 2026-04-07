def grid_to_iso(grid_x, grid_y, tile_width, tile_height):
    iso_x = (grid_x - grid_y) * (tile_width / 2)
    iso_y = (grid_x + grid_y) * (tile_height / 2)
    return iso_x, iso_y

def iso_to_grid(screen_x, screen_y, tile_width, tile_height, scroll_x=0, scroll_y=0):
    adj_x = screen_x - scroll_x
    adj_y = screen_y - scroll_y
    half_w = tile_width / 2
    half_h = tile_height / 2
    grid_y = (adj_y / half_h - adj_x / half_w) / 2
    grid_x = (adj_y / half_h + adj_x / half_w) / 2
    return int(grid_x), int(grid_y)
