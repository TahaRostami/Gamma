"""
Given models of size gamma representing queen domination on an n x n chessboard,
this script counts the number of unique models up to isomorphism.
"""

import zipfile
import json

def convert_to_int_if_possible(lst):
    """
    Converts a list of strings to integers if possible.
    :param lst: List of strings.
    :return: List of integers or None if conversion fails or list is empty.
    """
    try:
        converted_list = [int(item) for item in lst if item]
        return converted_list if converted_list else None
    except ValueError:
        return None

def check_iso(model1, model2, n):
    """
    Checks if two models are isomorphic by applying the 8 symmetries of the chessboard.

    :param model1: The first model (set of positions in 1-based indexing).
    :param model2: The second model (set of positions in 1-based indexing).
    :param n: The size of the chessboard (n x n).
    :return: True if `model1` is isomorphic to `model2` under any of the 8 symmetries, False otherwise.
    """

    def position_to_int(row, col):
        """Converts (row, col) coordinates back to integer position on the board."""
        return row * n + col

    # Define transformation functions for the symmetries of the chessboard.
    def identity(pos):
        i,j=divmod(pos,n)
        return position_to_int(i, j)

    def rotate_90(pos):
        i,j=divmod(pos,n)
        return position_to_int(n-1-j, i)

    def rotate_180(pos):
        i,j=divmod(pos,n)
        return position_to_int(n - 1 - i, n - 1 - j)

    def rotate_270(pos):
        i,j=divmod(pos,n)
        return position_to_int(j, n-1-i)

    def reflect_horizontally(pos):
        i,j=divmod(pos,n)
        return position_to_int(i, n - 1 - j)

    def reflect_vertically(pos):
        i,j=divmod(pos,n)
        return position_to_int(n - 1 - i, j)

    def reflect_main_diagonal(pos):
        i,j=divmod(pos,n)
        return position_to_int(j, i)

    def reflect_anti_diagonal(pos):
        i,j=divmod(pos,n)
        return position_to_int(n - 1 - j, n - 1 - i)

    # Transformations are implemented according to the specifications outlined in reference [1]
    # and use 0-based indexing.
    transformations = [identity, rotate_90, rotate_180, rotate_270,
        reflect_horizontally, reflect_vertically,
        reflect_main_diagonal, reflect_anti_diagonal]

    # Check if model1 is isomorphic to model2 under any of the 8 transformations.
    for transformation in transformations:
        # Transformations functions use 0-based indexing, but the model is 1-based indexing.
        # Therefore, we adjust the indices before applying the transformation.
        transformed_model1 = set(transformation(m-1)+1 for m in model1)
        # For debugging purposes
        #print(model1,transformed_model1)
        if transformed_model1 == model2:
            return True
    # For debugging purposes
    #print('-'*50)

    return False

def count_up_to_iso(n,models):
    """
    Counts the number of unique models up to isomorphism.

    :param n: The size of the chessboard (n x n).
    :param models: A list of models (sets of positions).
    :return: List of unique models up to isomorphism.
    """
    unique_models = []
    for m in models:
        to_be_added = True
        # Compare the current model with all previously found unique models.
        for um in unique_models:
            if check_iso(m, um, n):
                to_be_added = False
                break
        if to_be_added:
            unique_models.append(m)
    return unique_models

def count_up_to_iso_v2(n, models):
    """
    This is a hardcoded but optimized procedure for counting unique models up to isomorphism.
    It uses canonical forms of models based on chessboard symmetries to efficiently deduplicate them.
    """

    def canonical_form(model, n):
        """
        Returns the canonical (lexicographically smallest) representation of the model
        by applying all 8 symmetries and choosing the smallest one.
        """

        def position_to_int(row, col):
            """Converts (row, col) coordinates to integer position on the board."""
            return row * n + col

        def apply_symmetry(pos, transformation):
            i, j = divmod(pos, n)
            return transformation(i, j)

        transformations = [
            lambda i, j: (i, j),
            lambda i, j: (j, n - 1 - i),
            lambda i, j: (n - 1 - i, n - 1 - j),
            lambda i, j: (n - 1 - j, i),
            lambda i, j: (i, n - 1 - j),
            lambda i, j: (n - 1 - i, j),
            lambda i, j: (j, i),
            lambda i, j: (n - 1 - j, n - 1 - i)
        ]

        # Generate all transformations of the model and choose the lexicographically smallest
        canonical_representations = []
        for transformation in transformations:
            transformed_model = sorted(position_to_int(*apply_symmetry(pos - 1, transformation)) + 1 for pos in model)
            canonical_representations.append(tuple(transformed_model))

        return min(canonical_representations)

    unique_canonical_models = set()
    for model in models:
        canonical_model = canonical_form(model, n)
        unique_canonical_models.add(canonical_model)

    return unique_canonical_models

"""
There are two data sources for checking isomorphism in model enumeration scenarios:

1. 'generate_all_v2.zip' contains the output from UniDom for different board sizes (n) 
   and gamma values, which is used for testing against established results.

2. 'n_19_gamma_10_stat_results.json' stores models for the next open case of model enumeration (n=19).
   Both sources have slight differences in format, as shown below.
"""

source_ids=[1,2] # List of sources to process (1 for zip file, 2 for JSON file).

"""
There are two methods for counting up to isomorphism:

- 'count_up_to_iso' is a slower, but carefully written method suitable for moderate, manageable sizes.
- 'count_up_to_iso_v2' is an optimized version that uses canonical labeling, offering much faster performance.

"""
iso_count_method=[count_up_to_iso,count_up_to_iso_v2][1]

# Loop through the two sources and process them.
for source_id in source_ids:
    print(f'Source ID:{source_id}')
    if source_id==1:
        # Reading the models from the zip file
        zip_file_path = '../experiments/exp4_unidom_bug/generate_all_v2.zip'
        for n, gamma in [(4, 2), (5, 3), (6, 3), (7, 4), (8, 5), (9, 5), (10, 5), (11, 5), (12, 6), (13, 7), (14, 8),
                         (15, 9), (16, 9), (17, 9), (18, 9), (19, 10)]:
            file_to_read = f'generate_all_v2/all_{n}_{gamma}.txt'

            models = []

            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                with zip_ref.open(file_to_read) as file:
                    content = file.read().decode('utf-8').split('\n')
                    for c in content:
                        result = convert_to_int_if_possible(c.split(' ')[:-1])
                        if result is not None:
                            # Convert 0-based to 1-based indexing
                            # Moreover due to unidom's format, we need to discard first item as the first item does
                            # not denote a queen placement but the size of the found solution.
                            result = set([item + 1 for x, item in enumerate(result) if x > 0])
                            models.append(result)

            print(f"Counting Solutions up to Isomorphism for n={n} and gamma={gamma}: {len(iso_count_method(n,models))}")
    elif source_id==2:
        n,gamma = 19,10
        with open('n_19_gamma_10_stat_results.json','r') as json_file:
            models = [set(model) for model in json.load(json_file)['models']]
        print(f"Counting Solutions up to Isomorphism for n={n} and gamma={gamma}: {len(iso_count_method(n,models))}")

    print('\n'+'-'*50+'\n')





"""

Results Comparison: Counting Solutions up to Isomorphism


                          #UP TO ISO      #UP TO ISO
            N   Gamma  ThisCodeReports  PrevWorkReports
            --------------------------------------------
            4   2           3               3               
            5   3           37              37
            6   3           1               1
            7   4           13              13
            8   5           638             638
            9   5           21              21
            10  5           1               1
            11  5           1               1
            12  6           1               1
            13  7           41              41
            14  8           588             588
            15  9          25872          25872
            --------------------------------------------
            16  9           371             43
            17  9           22              22
            18  9           2               2
            --------------------------------------------
            19  10          11              -


Important Notes

1. Verification for N = 4 to 15:

    The results for cases where 4≤n≤15 have been solved and verified by multiple works, leading to high confidence in 
    the correctness of those results. For this reason, they serve as a basis for testing and validating our code. I 
    tested my implementation against these known values for  4≤n≤15, and the results are consistent.


2. Discrepancy for N = 16:

    For cases where 
    16≤n≤18, the results were solved in a previous work [2], though they have not been widely verified by other 
    researchers. A notable inconsistency appears for  n=16, where my code reports 371 solutions compared to 43 in [2].
    Without access to the original data from [2], it is difficult to make a definitive judgment about the cause of this
    difference. However, I hypothesize that the issue may stem from a bug in the tool "Unidom" used by the previous 
    work. Our testing has revealed bugs in Unidom's model enumeration process, which could explain the lower count 
    in [2].
    
    While this discrepancy is interesting, solving n=16 is not the primary focus of our current work, but it still
    provides insight into potential issues in prior research.
    
3. N = 19 Solved:
    The open case n=19 with γ=10 has been solved in this work, with this code reporting 11 solutions. This result is
    new and has not been reported by previous work.
"""


"""
References:
[1] - P.B. Gibbons, and J. A. Webb, ”Some new results for the queens domination problem,” Australasian Journal of 
     Combinatorics, pp.145-160, 1997.
[2] - W.H. Bird, "Computational methods for domination problems," Doctoral dissertation, 2017.
"""

