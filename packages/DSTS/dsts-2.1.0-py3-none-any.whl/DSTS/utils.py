import numpy as np
import pandas as pd

def NNsorting(aug, array, reference_array):
    """
    Sort array in NN order of reference array.

    Parameters:
    aug (int): The multiplier for the size of the synthesized data relative to the original data. 
                Defaults to 5.
    array : array to sort
    reference_array : reference array
    
    Returns:
    sorted array

    """
    size = reference_array.shape[0]
    final_array =[]
    # NNmatch with original data
    for j in range(aug):
        indices = list(range(size))
        for i in range(size):
            index = np.argmin([np.sum(np.abs(array[j][k] - reference_array[i]), axis=0) for k in indices])
            chosen_index = indices[index]
            final_array.append(array[j][chosen_index])
            indices.pop(index)
    
    return np.vstack(final_array)