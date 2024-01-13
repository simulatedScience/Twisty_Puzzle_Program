import pickle


def plot_x_values(filepath):
    training_info_dict = load_pickle_file(filepath)

    # get relevant constant values
    base_exploration_rate = training_info_dict["base_exploration_rate"]
    scramble_moves_increased = training_info_dict["scramble_moves_increased"]
    # get values
    x_values = training_info_dict["x_values"]
    explo_rates = training_info_dict["exploration_rates"]

def load_pickle_file(filepath):
    """
    load any pickle file located at the given filepath.
    ending '.pickle' can be ommited.
    """
    try:
        with open(filepath, "rb") as file:
            python_obj = pickle.load(file)
        return python_obj
    except FileNotFoundError:
        return load_pickle_file(filepath + ".pickle")