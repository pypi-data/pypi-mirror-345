predicate glasgow_global_cardinality(array[int] of var int: x,
                                    array[int] of int: cover,
                                    array[int] of var int: counts);

predicate fzn_global_cardinality(array[int] of var int: x,
                             array[int] of int: cover,
                             array[int] of var int: counts) =
    assert(index_set(cover) = index_set(counts),
        "global_cardinality: cover and counts must have identical index sets",
        glasgow_global_cardinality(x,cover,counts));