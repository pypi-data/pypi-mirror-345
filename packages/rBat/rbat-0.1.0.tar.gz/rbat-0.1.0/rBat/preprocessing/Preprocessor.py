# Imports
from . smoothing import lowess, repeated_running_medians
from . segmentation import segment_path
from functools import partial
import numpy as np

DEFAULT_PARAMS = {
    "LOWESS" : {
        "deg" : 2,
        "half_window" : 24,
        "num_iter" : 2
    },
    "RRM" : {
        "half_windows" : [7, 5, 3, 3], 
        "min_arr" : 12,        
        "tol" : 1.3        
    },
    "EM" : {         
        "half_window" : 4,    
        "log_transform" : np.cbrt, 
        "num_guesses" : 5,   
        "num_iters" : 500,    
        "significance" : 0.05,  
        "max_k" : 6, 
        "k" : None,
        "segment_constrain" : True # Specifies if the segment types should be constrained to 0 (lingering episodes) and 1 (progression episodes). False = more movement types than just two.
    }
}

LOG_TRANSFORM_FUNCTIONS = {
    "cbrt": np.cbrt,
    "log": np.log,
    "sqrt": np.sqrt,
    "log10": np.log10,
    "log2": np.log2,
    "log1p": np.log1p,
    "None": lambda x: x,
}

FRAMES_PER_SECOND = 29.97

class Preprocessor:
    def __init__(self, function_params=None):
        """
            function_params is a dict of dicts, with each inner dict corresponding to each major function, with their keys being function parameters and values the parameter values
        """
        self.lowess_params = DEFAULT_PARAMS["LOWESS"]
        self.rrm_params = DEFAULT_PARAMS["RRM"]
        self.em_params = DEFAULT_PARAMS["EM"]

        # Update params if there are any modifications from the default
        self.set_lowess_params(function_params)
        self.set_rrm_params(function_params)
        self.set_em_params(function_params)

        # Create the partial functions for the preprocessor to run
        self.lowess_func = partial(lowess, deg=self.lowess_params["deg"], half_window=self.lowess_params["half_window"], num_iter=self.lowess_params["num_iter"])
        self.rrm_func = partial(repeated_running_medians, half_windows=self.rrm_params["half_windows"], min_arr=self.rrm_params["min_arr"], tol=self.rrm_params["tol"])
        self.em_func = partial(segment_path, half_window=self.em_params["half_window"], log_transform=self.em_params["log_transform"],
                               num_guesses=self.em_params["num_guesses"], num_iters=self.em_params["num_iters"], significance=self.em_params["significance"], 
                               max_k=self.em_params["max_k"], k=self.em_params["k"])

    def preprocess_data(self, data):
        """
            Preprocesses the incoming data.

            Data is of the form: [frame, x-coordinates, y-coordinates]
        """
        ## Should the backend pass all the data files to my interface, or just do it one at a time.
        ## Personally, I think one at a time. Our RAM will be limited, and loading everything into memory might be unideal.

        # Run LOWESS (lowess)
        transformed_data = self.smooth_dataset(data)
        
        # Run RRM (repeated_running_medians)
        arrests = self.identify_arrests(data)

        # Calculate interpolations & velocity
        transformed_data = self.interpolate_and_velocity(transformed_data, arrests)

        # Run EM (segment_path)
        transformed_data = self.find_movement_types(transformed_data, arrests)

        return transformed_data     # Return numpy array of form: [frame, x-coordinates, y-coordinates, velocity, segment_type]
    
    def smooth_dataset(self, data):
        """
            Given a dataset of the form [frame, x, y], smooth it and calculate the velocities.
        """
        transformed_data = data.copy()

        # Run LOWESS (lowess)
        transformed_X, vel_X = self.lowess_func(transformed_data[:, 1])
        transformed_Y, vel_Y = self.lowess_func(transformed_data[:, 2])

        ## Apply smoothed data changes
        transformed_data[:, 1] = transformed_X
        transformed_data[:, 2] = transformed_Y

        ## Calculate and concatenate velocities to the transformed dataset
        velocities = np.sqrt(np.square(vel_X * FRAMES_PER_SECOND) + np.square(vel_Y * FRAMES_PER_SECOND)).reshape((-1, 1))
        transformed_data = np.hstack((transformed_data, velocities))
        
        return transformed_data

    
    def identify_arrests(self, data):
        """
            Given a dataset of the form [frame, x, y], determine the arrests using RRM.
        """
        data_copy = data.copy()
        # Find arrests for both x & y coords
        _, arrests_X = self.rrm_func(data_copy[:, 1])
        _, arrests_Y = self.rrm_func(data_copy[:, 2])

        # Get mask of shared arrests
        x_mask = np.zeros((len(data)), dtype=bool)
        y_mask = np.zeros((len(data)), dtype=bool)
        for xArrest_start, xArrest_end in arrests_X:
            x_mask[xArrest_start - 1 : xArrest_end] = True
        for yArrest_start, yArrest_end in arrests_Y:
            y_mask[yArrest_start - 1 : yArrest_end] = True

        arrest_mask = np.bitwise_and(x_mask, y_mask)
        arrest_mask_length = len(data)

        # From the shared arrests, add their start and end points (in frame numbers - indexed from 1) to the final arrest list
        arrests = []
        in_interval = False
        start = None
        for i in range(len(arrest_mask)):
            if not in_interval and arrest_mask[i]: # First frame that is an arrest (after a non-arrest)
                start = i + 1
                in_interval = True
            elif in_interval and not arrest_mask[i]: # First frame that isn't an arrest (after an arrest)
                arrests.append((start, i))
                in_interval = False
            elif in_interval and i == arrest_mask_length - 1: # Arrest continues until end of experiment.
                arrests.append((start, i + 1))

        return arrests

    def interpolate_and_velocity(self, data, arrests):
        """
            Takes in LOWESS data and arrest intervals. Returns data with interpolated coordinates and velocity.
        """
        transformed_data = data.copy()
        # arrest mask
        for start, end in arrests:
            arrest_length = end - (start - 1) 
            # Linear interpolation of the x, y coordinates during the arrests
            transformed_data[start - 1 : end, 1] = np.linspace(data[start - 1, 1], data[end - 1, 1], arrest_length) # X
            transformed_data[start - 1 : end, 2] = np.linspace(data[start - 1, 2], data[end - 1, 2], arrest_length) # Y

            # Velocity setting -> set velocity equal to 0 for all arrests
            transformed_data[start - 1 : end, 3] = 0 

        return transformed_data
    
    def find_movement_types(self, data: np.ndarray, arrests: list):
        """
            Takes in smoothed data and returns data with movement type concatenated to it.
            
        """
        # Run the EM algorithm and find the segments of movement type. Run the EM algorithm on fixed data so that it properly recognizes arrests.
        # print(fixed_data[:50])
        ## Create list of zero-indexed arrests (instead of one-indexed arrests accounting for frame values)
        zero_indexed_arrests = [(start - 1, end - 1) for (start, end) in arrests]
        segments = self.em_func(data[:, 1:3], zero_indexed_arrests).astype(int)

        # Create array of movement type data
        movement_types = np.zeros((len(data)))
        for start, end, move_type in segments:
            movement_types[start : end + 1] = move_type
            if self.em_params["segment_constrain"]: # Constrains movement types to 0 (lingering episode) or 1 (progression episode)
                movement_types = np.where(movement_types > 1, 1, movement_types)

        return np.hstack((data, movement_types.reshape(-1, 1)))

    def set_function_or_value(self, parameter, value):
        """
            Returns the appropriate value depending on the parameters. Basically used just in case we need to return functions.
        """
        if parameter == "log_transform":
            return LOG_TRANSFORM_FUNCTIONS[value]
        else:
            return value

    def set_lowess_params(self, parameter_dict):
        if parameter_dict != None and len(parameter_dict) != 0:
            for param, val in parameter_dict["LOWESS"].items():
                self.lowess_params[param] = val
    
    def set_rrm_params(self, parameter_dict):
        if parameter_dict != None and len(parameter_dict) != 0:
            for param, val in parameter_dict["RRM"].items():
                self.rrm_params[param] = val
    
    def set_em_params(self, parameter_dict):
        if parameter_dict != None and len(parameter_dict) != 0:
            for param, val in parameter_dict["EM"].items():
                self.em_params[param] = self.set_function_or_value(param, val)

