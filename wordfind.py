import numpy as np

from collections import defaultdict, deque


FILE_NAME_ORIG = "worddictorig.txt"
FILE_NAME = "worddict.txt"
ADJ = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


def read_worddict(filename):
    words = []
    line = ""
    with open(filename, "r") as text:
        line = text.readline()
        while line:
            words.append(line.strip().lower())
            line = text.readline()
    return words


def remove_len_2(word_list):
    return [word for word in word_list if len(word) > 2]


def write_lines(word_list):
    with open("worddict.txt", "w+") as new_file:
        for word in word_list:
            new_file.write(word + "\n")


def check_locations(curr, next):
    if curr[0] == -1:
        return True

    if curr == next:
        return False

    for i in range(2):
        if abs(curr[i] - next[i]) > 1:
            return False

    return True


def eval_word(stri, locations):
    char_loc = []
    str_len = len(stri)

    for i in range(str_len):
        new_char = locations[stri[i]]
        if len(new_char) == 0:
            return False
        char_loc.append(locations[stri[i]])

    loc_index = np.zeros(str_len, dtype=np.uint8)

    current = (-1, -1)
    prev_locs = deque()
    prev_locs.append(current)

    i = 0
    while i < str_len:
        poss_char_loc = char_loc[i]
        if loc_index[i] < len(poss_char_loc):
            next_loc = poss_char_loc[loc_index[i]]
            if check_locations(current, next_loc):
                if not (next_loc in prev_locs):

                    prev_locs.append(current)
                    current = next_loc
                    loc_index[i] += 1
                    i += 1
                    continue

            loc_index[i] += 1
            continue

        elif i == 0:
            return False

        current = prev_locs.pop()
        loc_index[i] = 0
        i -= 1

    return True


def eval_possible(grid, words):
    locations = defaultdict(list)
    grid_shape = grid.shape
    for i in range(grid_shape[0]):
        for j in range(grid_shape[1]):
            locations[grid[i, j]].append((i, j))

    possible = []

    for word in words:
        if eval_word(word, locations):
            possible.append(word)

    return possible


def get_possible_words(grid):
    words = read_worddict(FILE_NAME)
    possible_words = eval_possible(grid, words)
    return sorted(possible_words, key=len, reverse=True)


def main():
    test_grid = np.array([["w", "t", "g", "r"], ["h", "s", "n", "r"], ["c", "c", "w", "u"], ["o", "e", "e", "h"]])
    words = read_worddict(FILE_NAME)
    # possible = eval_possible(test_grid, words)
    possible = get_possible_words(test_grid)
    print(possible)

    # locations = defaultdict(list)
    #
    # for i in range(4):
    #     for j in range(4):
    #         locations[test_grid[i, j]].append((i, j))
    #
    # print(eval_word("run", locations))
