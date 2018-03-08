
from utils import *


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units

# Update the unit list to add the new diagonal units
diagonal_units = [boxes[::10], boxes[8:73:8]]
unitlist = unitlist + diagonal_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters: values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns: dict after naked twins elimination
    """
    # Find all boxes with 2 possible values
    doubles = [box for box in values.keys() if len(values[box]) == 2]

    # For each box in 'doubles', find a peer with the same possible values (a 'twin')
    # Store each unique pair of twins in a list
    twins = set()
    for box in doubles:
        for twin in peers[box]:
            if values[box] == values[twin]:
                twins.add(frozenset((box, twin)))
    twins = [tuple(pair) for pair in list(twins)]

    # Identify shared peers for each pair of twins (if twins are in the same unit,
    # they'll share peers from that unit).
    # Save each peer, along with the values that need to be removed from it, to a list.
    # Note: we mustn't `replace` values in boxes before the loop ends.
    values_to_replace = []
    for twin1, twin2 in twins:
        common_peers = list(peers[twin1].intersection(peers[twin2]))
        for box in common_peers:
            first_value = values[twin1][0]
            second_value = values[twin1][1]
            if first_value in values[box]:
                values_to_replace.append((box, first_value))
            if second_value in values[box]:
                values_to_replace.append((box, second_value))

    # Now the values_to_replace list contains tuples such as f.x. ('H5', '2')
    # Replacing values happens in this, separate, loop:
    for box, value in values_to_replace:
        assign_value(values, box, values[box].replace(value,''))

    return values


def eliminate(values):
    """
    Iterate over each box in puzzle that only has one value
    and remove this value from every one of its peers

    Parameters: values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns: dict after elimination
    """

    for box in values:
        if len(values[box]) == 1:
            box_peers = peers[box]
            box_value = values[box]
            for peer in box_peers:
                assign_value(values, peer, values[peer].replace(box_value, ""))
        else:
            continue
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    If only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters: values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns: dict with all single-valued boxes assigned
    """

    # For values from 1 to 9, iterate through every unit in unitlist.
    # Check which fields in the unit have this value in the list of possible values
    # If only one field in a unit can contain that value, the value is assigned to that field on the grid
    for unit in unitlist:
        for value in '123456789':
            boxes_with_value = [box for box in unit if value in values[box]]
            if len(boxes_with_value) == 1:
                assign_value(values, boxes_with_value[0], value)
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters: values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns: dict or False
        If continued application of constraint strategies no longer produces changes:
            return dict
        If puzzle is unsolvable:
            return False
    """

    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])

        stalled = solved_values_before == solved_values_after

    sanity_check = list(values.values())
    if '' in sanity_check:
        return False
    else:
        return values


def search(values):
    """Apply depth first search to solve Sudoku puzzle in case reduction alone
    doesn't solve the puzzle.

    Parameters: values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns: dict or False
        The values dictionary with all boxes assigned or False
    """

    # Reduce the puzzle
    values = reduce_puzzle(values)

    # If sudoku is corrupt, return False
    if values is False:
        return False

    # If sudoku is solved, return the solved puzzle:
    if all(len(values[box]) == 1 for box in boxes):
        return values

    # Choose one of the unfilled boxes with the fewest possible values (n>1)
    boxes_lengths = [(box, len(values[box])) for box in values.keys() if len(values[box]) > 1]
    sorted_by_length = sorted(boxes_lengths, key=lambda box: box[1])
    chosen_box = min(sorted_by_length)[0]

    # Assign each of the possible values to the box in turn and try to solve resulting grid
    # by constraint propagation and creating further new grids (if necessary)
    # If result of search is True, return the current grid
    for value in values[chosen_box]:
        new_grid = values.copy()
        new_grid[chosen_box] = value
        display(new_grid)
        attempt = search(new_grid)
        if attempt:
            return attempt


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters: grid(string)
        a string representing a sudoku grid.

        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns: dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue.')
