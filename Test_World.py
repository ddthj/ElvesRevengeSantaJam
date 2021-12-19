

def make_world(width, height):
    rows = []
    for x in range(width):
        column = []
        for y in range(height):
            column.append(1)
        rows.append(column)
    return rows


def building_map():
    return [
        ["santa_house", 8, 7],
        ["workshop", 13, 3],
        ["barn", 7, 4],
        ["store", 4, 9],
        ["warehouse", 8, 10],
        ["elf_house", 3, 5],
        ["elf_house", 5, 3],
        ["elf_house", 15, 9],
        ["elf_house", 3, 12],
        ["elf_house", 6, 14],
        ["elf_house", 8, 14],
        ["elf_house", 10, 14],
    ]