"""CommanderSM

This module serves as the main entrypoint for calculating and (temporarily in code) storing summary measures.


Authors: Brandon Carrasco
Created on: 13-11-2024
Modified on: 08-04-2025
"""

import numpy as np
from . import FieldSM as fsm
from . import FunctionalSM as fcsm
from . FunctionalSM import DATA_MAPPING, SM_MAPPING



### Commander Class ###

class Commander:
    """
        The Commander class stores the relevant information to calculate summary measures,
        as well as communicating them to whatever functionality calls it.

        Think of the Commander class as a middleman.

        Parameters
        ----------
        environment : str
            String denoting which test environment the specimen was in.
    """

    def __init__(self, environment: str):
        self.env = self.SelectEnvironment(environment)
        self.storedAuxiliaryInfo = {}
        self.calculatedSummaryMeasures = {}

    def SelectEnvironment(self, environmentName: str) -> fsm.Environment:
        """Based on the environment name passed, select the environment that will be used by the Commander.

        Parameters
        ----------
        environmentName : str
            Identifier of the environment to be used for calculation of summary measures. Available environmentName values are: common (all non-Q21 to Q23 & non-Q17 environments) and q20s (covers Q21 to Q23 environments)

        Returns
        -------
        Environment
            Environment to be used for the calculation of summary measures.
        """
        if environmentName == "common":
            return fsm.COMMON_ENV
        elif environmentName == "q20s":
            return fsm.Q20S_ENV
        else:
            raise Exception("Invalid environmentName passed: please pass common, q20s, or q17 as the environmentName.")
        
    # Goal for the below function is to: pre-calculate of important data that's used among several summary measures to reduce calculating the same thing over and over again.
    def PerformPreCalculations(self, data: np.ndarray, env: fsm.Environment, commonCalculations: list[str]):
        """Performs common calculations using the data and environment to avoid unnecessary recalculations.
            
            Updates self.storedAuxiliaryInfo with the store auxiliary calculations.

            Parameters
            ----------
            data : numpy.ndarray
                Preprocessed data array, of the format: 0 = frame, 1 = x-coord, 2 = y-coord, 3 = velocity, 4 = movement type (lingering or progression)
            env : Environment
                Testing environment for the given specimen (and data array)
            commonCalculations : list[str]
                A list of strings that correspond to the common calculations (between summary measures) that will be calculated.
        """
        # Run through each calculation and add them to the storedAuxiliaryInfo dictionary
        for cCalc in commonCalculations:
            func = getattr(fcsm, DATA_MAPPING[cCalc])
            self.storedAuxiliaryInfo[cCalc] = func(data, env)
            
    def AccountForJitter(self, data: np.ndarray, min=20, max=180) -> np.ndarray:
        """Given the preprocessed data, it will return the dataset with all x & y coordinates capped between 20 & 180 (the coordinate system used by the supervisors).
            This accounts for the rat being on the edges of the field -> the jitter of the tracking device sometimes makes the rat look like its crossing those boundaries, but its not.

            Parameters
            ----------
            data : numpy.ndarray
                Preprocessed data array, of the format: 0 = frame, 1 = x-coord, 2 = y-coord, 3 = velocity, 4 = movement type (lingering or progression)
            min : Number
                Minimum value to clip the jitter values. Defaults to 20.
            max : Number
                Maximum value to clip the jitter values. Defaults to 180.
            
            Returns
            -------
            data : numpy.ndarray
                Data array with any invalid values clipped to the minimum and maximum values.
        """
        # x-coord
        data[:, 1] = np.clip(data[:, 1], min, max)
        # y-coord
        data[:, 2] = np.clip(data[:, 2], min, max)
        return data        
        

    ## 0 = frame
    ## 1 = x-coord
    ## 2 = y-coord
    ## 3 = velocity
    ## 4 = segmentType (lingering vs. progression)

    def CalculateSummaryMeasures(self, data: np.ndarray, summaryMeasures: list[str], commonCalculations: list[str]) -> dict:
        """
            Calculates the list of summary measures (and common calculations) passed to it using the data provided.

            Updates self.calculatedSummaryMeasures with calculated summary measures.

            Parameters
            ----------
            data : numpy.ndarray
                Preprocessed data array, of the format: 0 = frame, 1 = x-coord, 2 = y-coord, 3 = velocity, 4 = movement type (lingering or progression)
            summaryMeasures : list[str]
                List of strings representing summary measures to be calculated on the dataset. Summary measures must be in the correct order and have all their dependent summary measures.
            commonCalculations : list[str]
                List of strings representing common calculations to be used in the summary measures passed.

            Returns
            -------
            calculatedSummaryMeasures
                Dictionary mapping summary measure ref. ids (see FunctionalSM) to their calculated outputs.
        """
        # Handle data jitter
        if self.env == fsm.COMMON_ENV:
            data = self.AccountForJitter(data)
        elif self.env == fsm.Q20S_ENV:
            data = self.AccountForJitter(data, min=-80, max=80)

        # Perform pre-calculations where possible to reduce overhead
        self.PerformPreCalculations(data, self.env, commonCalculations)
        
        # Run through summary measures & calculate them
        for sm in summaryMeasures:
            func = getattr(fcsm, SM_MAPPING[sm])
            self.calculatedSummaryMeasures[sm] = func(data, self.env, self.calculatedSummaryMeasures, self.storedAuxiliaryInfo)

        return self.calculatedSummaryMeasures
        

### TESTING ###
