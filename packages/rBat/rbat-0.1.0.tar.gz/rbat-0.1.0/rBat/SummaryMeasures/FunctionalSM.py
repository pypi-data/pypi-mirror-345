"""FunctionSM

This module contains all of the required functionality in regards to Summary Measure functions (their calculations)


Authors: Brandon Carrasco
Created on: 07-11-2024
Modified on: 01-05-2025
"""

# Imports
import numpy as np
from . import FieldSM as fsm
from . FieldSM import GetLocaleFromIndex, GetIndexFromLocale

# Constants

FRAMES_PER_SECOND = 29.97

## Ref ids for Data & SMs -> Easier way to call the summary measure functions

SM_MAPPING = {
    "calc_homebases" : "CalculateHomeBases",
    "calc_HB1_cumulativeReturn" : "CalculateFreqHomeBaseStops",
    "calc_HB1_meanDurationStops" : "CalculateMeanDurationHomeBaseStops",
    "calc_HB1_meanReturn" : "CalculateMeanReturnHomeBase",
    "calc_HB1_meanExcursionStops" : "CalculateMeanStopsExcursions",
    "calc_HB1_stopDuration" :  "Calculate_Main_Homebase_Stop_Duration",
    "calc_HB2_stopDuration" : "Calculate_Secondary_Homebase_Stop_Duration",
    "calc_HB2_cumulativeReturn" : "Calculate_Frequency_Stops_Secondary_Homebase",
    "calc_HB1_expectedReturn" : "Calculated_Expected_Return_Frequency_Main_Homebase",
    "calc_sessionReturnTimeMean" : "Calculate_Mean_Return_Time_All_Locales",
    "calc_sessionTotalLocalesVisited" : "Calculate_Total_Locales_Visited",
    "calc_sessionTotalStops" : "Calculate_Total_Stops",
    "calc_expectedMainHomeBaseReturn" : "Expected_Return_Time_Main_Homebase",
    "calc_distanceTravelled" : "Calculate_Distance_Travelled",
    "calc_boutsOfChecking" : "Calculate_Bouts",
    "calc_bout_totalBouts" : "Calculate_Bout_Total",
    "calc_bout_totalBoutDuration" : "Calculate_Bout_Total_Duration",
    "calc_bout_meanTimeUntilNextBout" : "Calculate_Bout_Mean_Time_Until_Next_Bout",
    "calc_bout_meanCheckFreq" : "Calculate_Bout_Mean_Check_Frequency",
    "calc_bout_meanRateOfChecks" : "Calculate_Bout_Mean_Rate_Of_Checks"
}

DATA_MAPPING = {
    "locale_stops_calc" : "CalculateStops",
    "distances_calc" : "CalcuateDistances",
}


## Storing Dependencies for Summary Measures and Common Calcs
## SM Dependencies
### All SMs that are dependent on other SMs to be calculated appear here in this dict.
### Their values is a list of summary measures that must be calculated before the key SM is calculated.
SM_DEPENDENCIES = {
    "calc_HB1_cumulativeReturn" : ["calc_homebases"],
    "calc_HB1_meanDurationStops" : ["calc_homebases"],
    "calc_HB1_meanReturn" : ["calc_homebases"],
    "calc_HB1_meanExcursionStops" : ["calc_homebases"],
    "calc_HB1_stopDuration" : ["calc_homebases"],
    "calc_HB2_stopDuration" : ["calc_homebases"],
    "calc_HB2_cumulativeReturn" : ["calc_homebases"],
    "calc_HB1_expectedReturn" : ["calc_homebases"],
    "calc_sessionReturnTimeMean" : ["calc_homebases"],
    "calc_expectedMainHomeBaseReturn" : ["calc_homebases", "calc_HB1_meanReturn", "calc_sessionReturnTimeMean"],
    "calc_boutsOfChecking" : ["calc_homebases"],
    "calc_bout_totalBouts" : ["calc_boutsOfChecking"],
    "calc_bout_totalBoutDuration" : ["calc_boutsOfChecking"],
    "calc_bout_meanTimeUntilNextBout" : ["calc_boutsOfChecking"],
    "calc_bout_meanCheckFreq" : ["calc_homebases", "calc_boutsOfChecking"],
    "calc_bout_meanRateOfChecks" : ["calc_homebases", "calc_boutsOfChecking"],
}

## Data Dependencies
### Dictionary of summary measure names (strings) matched to the functions that calculate the metrics that the summary measure needs.
DATA_DEPENDENCIES = {
    "calc_homebases" : ["locale_stops_calc"],
    "calc_HB1_cumulativeReturn" : ["locale_stops_calc"],
    "calc_HB1_meanDurationStops" : ["locale_stops_calc"],
    "calc_HB1_meanReturn" : ["locale_stops_calc"],
    "calc_HB1_meanExcursionStops" : ["locale_stops_calc"],
    "calc_HB1_stopDuration" : ["locale_stops_calc"],
    "calc_HB2_stopDuration" : ["locale_stops_calc"],
    "calc_HB2_cumulativeReturn" : ["locale_stops_calc"],
    "calc_HB1_expectedReturn" : ["locale_stops_calc"],
    "calc_sessionReturnTimeMean" : ["locale_stops_calc"],
    "calc_sessionTotalLocalesVisited" : ["locale_stops_calc"],
    "calc_sessionTotalStops" : ["locale_stops_calc"],
    "calc_distanceTravelled" : ["distances_calc"]
}


### Commander-Specific Helper Functions (calculation of data mainly) ###

def CalculateStopLocale(data: np.ndarray, env: fsm.Environment, index=True) -> tuple[int, int, int]:
    """Calculates and returns the locale that the visit (present within the data belongs to).

    Calculates only the first lingering episode.
    
    Parameters
    ----------
    data : numpy.ndarray
        Time-spatial data of the specimen
    env : Environment
        Test environment of the specimen.
    index : Bool
        Flag indicating to return the list index of the locale of the stop or the Eshkol-Wachmann name for the locale.
    
    """
    visit = False
    localeDurations = [0 for i in range(25)]
    stopStart = 0
    for i in range(len(data)):
        frame = data[i]
        if frame[4] == 0: # if currently in a lingering episode
            if not visit:
                stopStart = i
            visit = True
            specimenLocale = env.SpecimenLocation(frame[1], frame[2], index=True)
            localeDurations[specimenLocale] += 1
        elif visit and (frame[4] == 1 or (i == len(data) - 1 and frame[4] == 0)): # If the lingering episode finishes or the end of the data is reached
            if i == len(data) - 1 and frame[4] == 0:
                specimenLocale = env.SpecimenLocation(frame[1], frame[2], index=True)
                localeDurations[specimenLocale] += 1
            maxLocale = np.argmax(localeDurations)
            if index:
                return maxLocale, stopStart, i
            else:
                return fsm.GetLocaleFromIndex(maxLocale), stopStart, i
    return -1, None, None # No stop occurred.

def CheckForMissingDependencies(calc: str, preExistingSMs: dict):
    """
        Confirms that the selected calc has all of its summary measure dependencies calculated. Throws error otherwise.
    """
    if calc not in SM_DEPENDENCIES.keys(): # If desired SM requires no summary measures to be calculated, then everything's fine
        return
    dependencies = SM_DEPENDENCIES[calc]
    notCalculated = set(dependencies) - set(preExistingSMs)
    if len(notCalculated) != 0: # If some dependencies still haven't been calculated
        print(f"Attempting to calculate {calc}, but missing the following necessary summary measures:")
        for sm in notCalculated:
            print(f"     - {sm}")
        raise Exception("Error: Missing one or more summary measures necessary to calculate another summary measure!")

def HandleMissingInputs(refId: str, data: np.ndarray, env: fsm.Environment, calculatedSummaryMeasures: dict, preExistingCalcs: dict | None) -> dict:
    """
        Calculates all necessary pre-calculations if they haven't already been calculated.

        TODO: Do the same for the summary measures that haven't been calculated.

        Parameters
        ----------
        refId : str
            Reference id corresponding to the summary measure to calculate.
        data : numpy.ndarray
            Smoothed time spatial data.
        env : fsm.Environment
            Test environment of specimen.
        calculatedSummaryMeasures : dict
            Dictionary of summary measures that have already been calculated.
        preExistingCalcs : dict | None
            Dictionary of any pre-existing data calculations. If None, no pre-existing calcs to pass.
        
        Returns
        -------
        desiredDataCalcs : dict
            Dictionary of all necessary data calculations to calculate the summary measure.
    """
    # Check if required summary measures have been calculated already
    ## If not, then raise an Error!
    CheckForMissingDependencies(refId, calculatedSummaryMeasures.keys())
    # Perform any necessary pre-calcs (for data dependencies)
    requiredDataCalcs = DATA_DEPENDENCIES.get(refId, [])
    desiredDataCalcs = CalculateMissingCalcs(data, env, preExistingCalcs, requiredDataCalcs) if len(requiredDataCalcs) > 0 else {}
    return desiredDataCalcs

def CalculateMissingCalcs(data: np.ndarray, env: fsm.Environment, preExistingCalcs: dict | None, calcs: list[str]) -> dict:
    """
        Given a list of data calculations (or none), determine which data calculations need to be calculated for a summary measure and then calculate them.
    """
    # Find missing calcs
    desiredCalcs = {}
    if preExistingCalcs != None: # If passed pre-existing data, find any pre-calculated data that's missing (that will be calculated)
        missingCalcs = list(set(calcs) - set(preExistingCalcs.keys()))
        for calc in list(set(calcs) - set(missingCalcs)): # Add all already existing calcs to the desired calcs dictionary
            desiredCalcs[calc] = preExistingCalcs[calc]
    else:
        missingCalcs = calcs # If no pre-existing data passed, then calculated all required data.

    # Calculate Missing Calcs
    for missingCalc in missingCalcs: # Calculate all missing calculations and add them to the desired calcs dictionary
        calcFunc = globals()[DATA_MAPPING[missingCalc]]
        desiredCalcs[missingCalc] = calcFunc(data, env)

    # Return as dict for use in the summary measure function
    
    return desiredCalcs

### Calculating metrics ###

## Metrics/Data Calculation Schema ##
#   All calculations of common data that's used across one or more summary measures share the following input schema:
#       data : numpy.ndarray
#           Preprocessed data array, of the format: 0 = frame, 1 = x-coord, 2 = y-coord, 3 = velocity, 4 = movement type (lingering or progression)
#       env : Environment
#           Testing environment for the given specimen (and data array)
#   This schema is ensures that these functions can be called generically. Data Pre-calc functions shouldn't need anything but these two inputs.
## End of Data Calculation Schema ##


def CalculateStops(data: np.ndarray, env: fsm.Environment) -> tuple[list[int], list[int]]:
    """
        Given the raw time-series data and environment of the experiment, calculates the stops in each locale, as well as the total duration of the stops (in frames) for each locale.
    """
    stopLocales = [0 for x in range(25)]
    stopFrames = [0 for x in range(25)]
    stopped = False
    prevStopLocale = -1
    locDur = [0 for x in range(25)]
    
    for i in range(len(data)):
        frame = data[i]
        if frame[4] == 0: # Part of a lingering episode
            specimenLocale =  env.SpecimenLocation(frame[1], frame[2], index=True) # Get current locale of specimen

            stopped = True # Lingering episode begins (if it hasn't already begun)
            # Count the stop
            locDur[specimenLocale] += 1
        elif frame[4] == 1 and stopped: # lingering episode ends
            stopped = False
            # Get the maximum duration for each locale and add a stop to the max locale
            maxLocale = np.argmax(locDur)
            if maxLocale != prevStopLocale: # If a stop is NOT successive (previous stop locale is the same as the current stop locale, then it's considered one stop).
                stopLocales[maxLocale] += 1
            prevStopLocale = maxLocale
            # Add stop frames to total stop durations
            stopFrames[maxLocale] += sum(locDur) 
            # Reset local locale stop durations (for a stop episode)
            locDur = [0 for x in range(25)]

    if stopped: # if the search for stops ends on a stop, then sum it up and calculate the necessary stuff
        maxLocale = np.argmax(locDur)
        if maxLocale != prevStopLocale: # If a stop is successive (previous stop locale is the same as the current stop locale, then it's considered one stop). Otherwise, add the stop.
            stopLocales[maxLocale] += 1
        # Add stop frames to total stop durations
        # stopFrames = [sum(comb) for comb in zip(stopFrames, locDur)]
        stopFrames[maxLocale] += sum(locDur) 
    return stopLocales, stopFrames


def CalcuateDistances(data: np.ndarray, env: fsm.Environment) -> list[int]:
    """
        Given the raw time-series data and environment, calculates the distance travelled from one frame to the next.

        Frame 0 will always be 0.
    """
    distanceFrames = [0]
    prevFrameX = data[0][1]
    prevFrameY = data[0][2]
    for i in range(1, len(data)):
        curFrameX = data[i][1]
        curFrameY = data[i][2]
        dist = np.sqrt(np.square(curFrameX - prevFrameX) + np.square(curFrameY - prevFrameY))
        distanceFrames.append(dist)
        prevFrameX = curFrameX
        prevFrameY = curFrameY
    return distanceFrames
        
        
### Functions to Calculate Summary Measures ###

### On Summary Measures format ###
#   All summary measures follow the same parameters format:
#       data : numpy.ndarray
#           Preprocessed data array, of the format: 0 = frame, 1 = x-coord, 2 = y-coord, 3 = velocity, 4 = movement type (lingering or progression)
#       env : Environment
#           Testing environment for the given specimen (and data array)
#       requiredSummaryMeasures : dict
#           Dict containing all summary measures (matching name to outputs) previously calculated by the interface (or by some other method). Must contain the summary measures that the current summary measure being calculated depends on.
#       preExisitingCalcs : dict | None
#           Dict containing all the data calculations (locale stops, etc.) that the summary measure requires. Optional, but saves time if pre-calculated and shared with all dependent summary measures.
#   The above schema ensures that summary measures can be run by the interface generically (or be handled by a bespoke solution generically).
### End of Summary Measures format explanation ###

## Minor Notes ##
#   SM descriptions contain the following two ids:
#   1. 'Also referred to as...', which describes what official name for the summary measures are when downloaded. Defined by Dr. Anna Dvorkin & Dr. Henry Szetchman. 
#   2. 'Reference ID for Commander:...', which describes the shorthand we use to call those summary measures (from the Commander class).
## End of Minor Notes ##

def CalculateHomeBases(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> tuple[int, int | None]:
    """
        Given an environment and matrix containing columns specifying the x-coords, y-coords, and movement type (lingering or progression) of the specimen per frame (every sample is one frame),
        return the two locales (main home base & secondary home base) of the specimen.

        If the main home base is visited only once, then return None for secondary home base. 

        Also referred to as KPname01 & KPname02.

        Reference ID for Commander: calc_homebases
    """
    ### Perform necessary calculations on the data!
    desiredCalcs = HandleMissingInputs('calc_homebases', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    localeVisits = desiredCalcs['locale_stops_calc'][0]
    localeDuration = desiredCalcs['locale_stops_calc'][1]
    for i in range(len(localeVisits)):
        print(f"Locale {GetLocaleFromIndex(i)} was visited {localeVisits[i]} times, for a duration of {localeDuration[i]}")

    # Calculate home bases
    topTwoMostVisited = np.argpartition(np.array(localeVisits), len(localeVisits) - 2)[-2:]
    localeA = topTwoMostVisited[0]
    localeB = topTwoMostVisited[1]
    # Check & handle tiebreaker
    # if localeVisits[localeA] == localeVisits[localeB]:
    if abs(localeVisits[localeA] - localeVisits[localeB]) <= 4: # If the number of stops in both locales are within 5 of each other, check their durations.
        mainHomeBase = localeA if localeDuration[localeA] >= localeDuration[localeB] else localeB
    else:
        mainHomeBase = localeA if localeVisits[localeA] >= localeVisits[localeB] else localeB
    secondaryHomeBase = localeA if mainHomeBase == localeB else localeB
    if localeA < 2 and localeB < 2: # In case that there's less than two stops for main home base. In this case, the home base would essentially be a random locale that has one stop in it.
        return GetLocaleFromIndex(mainHomeBase), None
    else:
        return GetLocaleFromIndex(mainHomeBase), GetLocaleFromIndex(secondaryHomeBase)


def CalculateFreqHomeBaseStops(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> int:
    """
        Calculates the cumulative number of stops within the first home base. Requires the First Home Base to have been calculated (ref. id. calc_homebases)

        Also referred to as KPcumReturnfreq01

        Reference ID is: calc_HB1_cumulativeReturn
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_HB1_cumulativeReturn', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    localeVisits = desiredCalcs['locale_stops_calc'][0]
    mainHomeBase = requiredSummaryMeasures['calc_homebases'][0]

    # Constraint: cannot calculate the summary measure if 2nd home base isn't present
    # if requiredSummaryMeasures["calc_homebases"][1] == None:
    #     print("WARNING: Cannot calculate mean return time to main home base, as second home base does not exist!")
    #     return None
    
    ind = GetIndexFromLocale(mainHomeBase)
    return localeVisits[ind]

def CalculateMeanDurationHomeBaseStops(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> tuple[float, float]:
    """
        Calculates the mean duration (in seconds) of the specimen remaining in the main home base. Additionally returns the log (base 10) of this duration as well.

        Also referred to as KPmeanStayTime01_s & KPmeanStayTime01_s_log.

        Reference ID is: calc_HB1_meanDurationStops
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_HB1_meanDurationStops', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    localeVisits = desiredCalcs['locale_stops_calc'][0]
    localeDuration = desiredCalcs['locale_stops_calc'][1]
    mainHomeBase = requiredSummaryMeasures['calc_homebases'][0]

    ind = GetIndexFromLocale(mainHomeBase)
    totalDuration = localeDuration[ind]
    numStops = localeVisits[ind]

    duration_in_seconds = (totalDuration / numStops) / FRAMES_PER_SECOND
    return duration_in_seconds, np.log10(duration_in_seconds)

def CalculateMeanReturnHomeBase(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> float:
    """
        Calculates the mean return time to the main home base (in seconds). Also can be thought of as the mean duration of execursions.

        Also referred to as KPcumReturnfreq01

        Reference ID is: calc_HB1_meanReturn
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_HB1_meanReturn', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    localeVisits = desiredCalcs['locale_stops_calc'][0]
    localeDuration = desiredCalcs['locale_stops_calc'][1]
    mainHomeBase = requiredSummaryMeasures['calc_homebases'][0]

    # Constraint: cannot calculate the summary measure if 2nd home base isn't present
    if requiredSummaryMeasures["calc_homebases"][1] == None:
        print("WARNING: Cannot calculate mean return time to main home base, as second home base does not exist!")
        return None
    
    ind = GetIndexFromLocale(mainHomeBase)
    # Sum of all durations and stops minus the ones that are in the main home base
    totalDuration = sum(localeDuration) - localeDuration[ind]
    totalExcursions = sum(localeVisits) - localeVisits[ind]
    return (totalDuration / totalExcursions) / FRAMES_PER_SECOND

def CalculateMeanStopsExcursions(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> float:
    """
        Calculates the mean number of stops during excursions (away from the Main Home Base).

        Also referred to as KPstopsToReturn01

        Reference ID is: calc_HB1_meanExcursionStops
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_HB1_meanExcursionStops', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    mainHomeBase = requiredSummaryMeasures['calc_homebases'][0]

    totalExcursions = 0
    totalStops = 0
    excursion = False
    # stopped = False
    previousLocale = -1

    f = 0
    while f < len(data):
        stopLocale, preStopIndex, postStopIndex = CalculateStopLocale(data[f:], env, index=False)
        if stopLocale == -1: # no more visitations, period
            break
        if stopLocale != previousLocale: # If not a successive stop, then count it
            if stopLocale != mainHomeBase:
                if not excursion:
                    excursion = True
                    totalExcursions += 1
                totalStops += 1
            else:
                excursion = False
        f += postStopIndex
    # Count number of excursions (and their total stops) for each locale
    # for i in range(len(data)):
    #     frame = data[i]
    #     specimenLocale = env.SpecimenLocation(frame[1], frame[2])
    #     if specimenLocale != mainHomeBase: # If the specimen is not in the main home base
    #         if frame[4] == 1 and not excursion: # If the specimen is no longer in its main home base, it's on an excursion. Has to be moving in a progressive episode to be counted as an excursion (lingering between main home base and elsewhere doesn't count).
    #             totalExcursions += 1
    #             excursion = True
    #         if frame[4] == 0 and excursion and not stopped: # If the specimen is lingering while on an excursion
    #             totalStops += 1 ## UPDATE WITH PROPER STOP CALCULATION METHODS. NEEDS TO CALCULATE ACCORDING TO REAL STOP METHOD.
    #             stopped = True
    #         elif frame[4] == 1:
    #             stopped = False 
    #     else:
    #         excursion = False
    return totalStops / totalExcursions

def Calculate_Main_Homebase_Stop_Duration(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> float:
    """
        Calculates the cumulative duration of stops within the first home base, measured in seconds.

        Also referred to as: KPtotalStayTime01_s

        Reference ID is: calc_HB1_stopDuration
    """
    # Check if required summary measures have been calculated already
    CheckForMissingDependencies('calc_HB1_stopDuration', requiredSummaryMeasures.keys())
    # Perform any necessary pre-calcs
    requiredCalcs = DATA_DEPENDENCIES["calc_HB1_stopDuration"]
    desiredCalcs = CalculateMissingCalcs(data, env, preExistingCalcs, requiredCalcs)

    ### Summary Measure Logic
    # localeVisits = desiredCalcs['locale_stops_calc'][0]
    localeDuration = desiredCalcs['locale_stops_calc'][1]
    mainHomeBase = requiredSummaryMeasures['calc_homebases'][0]

    ind = GetIndexFromLocale(mainHomeBase)
    return localeDuration[ind] / FRAMES_PER_SECOND

def Calculate_Secondary_Homebase_Stop_Duration(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> float:
    """
        Calculates the cumulative duration of stops within the second home base, measured in seconds.

        Warning: There must be at least two stop within the first home base (for the second home base to exist).

        Also referred to as: KPtotalStayTime02_s

        Reference ID is: calc_HB2_stopDuration
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_HB2_stopDuration', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    # Constraint: cannot calculate the summary measure if 2nd home base isn't present
    if requiredSummaryMeasures["calc_homebases"][1] == None:
        print("WARNING: Cannot calculate mean return time to main home base, as second home base does not exist!")
        return None

    localeDuration = desiredCalcs['locale_stops_calc'][1]
    secondaryHomeBase = requiredSummaryMeasures['calc_homebases'][1]

    ind = GetIndexFromLocale(secondaryHomeBase)
    return localeDuration[ind] / FRAMES_PER_SECOND


def Calculate_Frequency_Stops_Secondary_Homebase(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> int:
    """
        Calculates the cumulative number of stops within the second home base.

        Warning: There must be at least two stop within the first home base (for the second home base to exist).

        Also referred to as: KPcumReturnfreq02

        Reference ID is: calc_HB2_cumulativeReturn
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_HB2_cumulativeReturn', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    # Constraint: cannot calculate the summary measure if 2nd home base isn't present
    if requiredSummaryMeasures["calc_homebases"][1] == None:
        print("WARNING: Cannot number of stops within the secondary home base, as second home base does not exist!")
        return None

    localeVisits = desiredCalcs['locale_stops_calc'][0]
    secondaryHomeBase = requiredSummaryMeasures['calc_homebases'][1]

    ind = GetIndexFromLocale(secondaryHomeBase)
    return localeVisits[ind]

def Calculated_Expected_Return_Frequency_Main_Homebase(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> float:
    """
        Calculates the expected return frequency to the first home base.

        TO DO: Confirm that this function is meant to calculate expected return!

        Also referred to as: KPexpReturnfreq01

        Reference ID is: calc_HB1_expectedReturn
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_HB1_expectedReturn', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    localeVisits = desiredCalcs['locale_stops_calc'][0]
    mainHomeBase = requiredSummaryMeasures['calc_homebases'][0]

    # The total number of locales visited during the session
    totalLocalesVisited = sum([1 if visits > 0 else 0 for visits in localeVisits])

    # All stops in the main home base
    ind = GetIndexFromLocale(mainHomeBase)
    mainVisits = localeVisits[ind]
    
    return (mainVisits * totalLocalesVisited) / sum(localeVisits)

def Calculate_Mean_Return_Time_All_Locales(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> float:
    """
        Calculates the mean return time to all locales, or rather, the average time it takes to visit or stop in a locale.

        Warning: There must be at least two stop within the first home base (for there to be a main home base). I think.

        Also referred to as: KP_session_ReturnTime_mean

        Reference ID is: calc_sessionReturnTimeMean
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_sessionReturnTimeMean', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    if requiredSummaryMeasures["calc_homebases"][1] == None:
        print("WARNING: Cannot calculate mean return time to all locales, as the first home base is only stopped in once!")
        return None

    localeVisits = desiredCalcs['locale_stops_calc'][0]
    localeDurations = desiredCalcs['locale_stops_calc'][1]
    mainHomeBase = requiredSummaryMeasures['calc_homebases'][0]

    excursionTimes = []
    totalExcursionsDuration = sum(localeDurations)
    for loc in range(len(localeDurations)):
        if localeVisits[loc] > 0: # If the locale was visited at least once.
            excursionTimeForLocale = totalExcursionsDuration - localeDurations[loc] # Calculate the current locales total excursion (away from locale) time.
            excursionTimes.append(excursionTimeForLocale / localeVisits[loc]) # Calculate the average return time to the current locale 

    # Average the total excursion time
    meanReturnTimeToAllLocales = np.mean(excursionTimes)
    return  meanReturnTimeToAllLocales / FRAMES_PER_SECOND


def Expected_Return_Time_Main_Homebase(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> float:
    """
        Calculates the expected return time to the main homebase.

        Warning: There must be at least two stop within the first home base (for there to be a main home base). I think.

        Also referred to as: KPexpReturntime01

        Reference ID is: calc_expectedMainHomeBaseReturn
    """
    # # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs("calc_expectedMainHomeBaseReturn", data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    if requiredSummaryMeasures["calc_homebases"][1] == None:
        print("WARNING: Cannot calculate mean return time to main homebase, as the first home base is only stopped in once!")
        return None
    
    mainHomeBaseMeanReturn = requiredSummaryMeasures['calc_HB1_meanReturn']
    sessionMeanReturn = requiredSummaryMeasures['calc_sessionReturnTimeMean']
    
    return mainHomeBaseMeanReturn / sessionMeanReturn
    

def Calculate_Total_Locales_Visited(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> int:
    """
        Calculates the total number of locales visited (1 to 25) throughout a session.

        Also referred to as: KP_session_differentlocalesVisited_#

        Reference ID is: calc_sessionTotalLocalesVisited
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_sessionTotalLocalesVisited', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    localeVisits = desiredCalcs['locale_stops_calc'][0]
    
    visitedLocales = [1 if visits > 0 else 0 for visits in localeVisits]
    return sum(visitedLocales)

def Calculate_Total_Stops(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> int:
    """
        Calculates total number of stops in a session.

        Also referred to as: KP_session_Stops_total#

        Reference ID is: calc_sessionTotalStops
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_sessionTotalStops', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    localeVisits = desiredCalcs['locale_stops_calc'][0]

    return sum(localeVisits)

###  Distance & Locomotion Summary Measures ###

def Calculate_Distance_Travelled(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None):
    """
        Calculates all distances travelled metrics. Returns a tuple of (total distance for progression segments only, total distance for all segments),
        total distance travelled, speed of progression, 
        and a tuple of two lists of travelled distances in five minute intervals from start to finish,
        with the first list corresponding to the use of only the progression statements, and
        the second corresponding to the use of all segements.

        See Checking_parameters_Definitions_Oct30_2024 for full list of variables.

        Reference ID is: calc_distanceTravelled
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_distanceTravelled', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    distanceData = desiredCalcs['distances_calc']
    # Get chunk length (in terms of frames) for five minutes worth of time
    chunkLength = 5 * 60 * FRAMES_PER_SECOND
    chunk = 0
    distancesProgression = [0 for i in range(11)]
    distancesAll = [0 for i in range(11)]
    totalDurationOfProgression = 0

    for i in range(len(data)):
        # Update chunks if necessary
        if i == (chunk + 1) * chunkLength:
            chunk += 1
        frame = data[i]
        # Add distance to all distances list
        distancesAll[chunk] += distanceData[i]
        if frame[4] == 1: # If it's a progression segment, add it to the progression distances list
            distancesProgression[chunk] += distanceData[i]
            totalDurationOfProgression += 1 # Add 1 frame to the total duration of progressions
    totalDurationSeconds = totalDurationOfProgression / FRAMES_PER_SECOND
    # Divide all distances by 100 to get distance in metres
    distancesAll = [distance / 100 for distance in distancesAll]
    distancesProgression = [distance / 100 for distance in distancesProgression]
    # Calculate total distance travelled for all & progression
    totalDistanceAll = sum(distancesAll)
    totalDistanceProgression = sum(distancesProgression)
    return (totalDistanceProgression, totalDistanceAll), totalDurationSeconds, totalDistanceProgression / (totalDurationSeconds), (distancesProgression, distancesAll)


def Calculate_Bouts(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None) -> list[list]:
    """
        Calculates the bouts of checking and returns a list of lists containing frames from the time-spatial data comprising checking bouts.

        NOTE: Not intended to be returned to the user. Only used for the bout characterization summary measures. Only a summary measure because it requires main homebase.

        Reference ID is: calc_boutsOfChecking
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_boutsOfChecking', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    mainHomeBase = requiredSummaryMeasures["calc_homebases"][0]

    ## Need to find all long lingering episodes and filter them out to get bouts of activity
    # Find mean time + IQR of lingering episodes
    allLing = []
    ling = False
    currentLing = []

    # Get the start (inclusive) and end (exclusive) points of all lingering episodes
    for i in range(len(data)):
        frame = data[i]
        if frame[4] == 0 and ling == False:
            ling = True
            currentLing.append(i)
        elif frame[4] == 1 and ling == True:
            ling = False
            currentLing.append(i)
            allLing.append(currentLing) # Append [start, end) points to the all lingering episodes thingy 
            currentLing = []
    if len(currentLing) != 0: # In case the loop ends on a lingering episode
        currentLing.append(len(data))
        allLing.append(currentLing)

    # Calculate means for lingering episode duration
    timeForEpi = [end - start for (start, end) in allLing] # Calculate the total duration for each lingering episode
    meanTimeLing = sum(timeForEpi) / len(allLing) # Mean time of lingering episode
    q75Mean, q25Mean = np.percentile(timeForEpi, [75, 25])
    iqrMean = q75Mean - q25Mean

    # Get outlier lingering episodes (time of epi is >= mean + 1.5 * iqr)
    outlierIndices = np.array(timeForEpi)
    outlierIndices = (outlierIndices >= (meanTimeLing + 1.5 * iqrMean)) # Which lingering episodes are outliers -> should produce a bool array
    outliers = []
    for x in range(len(outlierIndices)): # Get indices of all outlier episodes in the actual data
        if outlierIndices[x] == True: # If the current lingering episode is an outlier
            outliers = outliers + [frame for frame in range(allLing[x][0], allLing[x][1])] # generate indicies between the start and end of lingering episodes

    # Calculate bouts of activity
    boutOfActivity = np.delete(data, outliers, axis=0) # Delete all frames that belong to outlier lingering episodes
    ## Convert bouts into chunks of frames
    prev_frame = boutOfActivity[0]
    total_chunks = []
    cur_chunk = [prev_frame]
    for c in range(1, len(boutOfActivity)):
        frame = boutOfActivity[c]
        if frame[0] != prev_frame[0] + 1: # If this frame doesn't follow the previous one -> end of chunk
            total_chunks.append(cur_chunk)
            cur_chunk = [frame]
        else: # Add current frame to the current chunk
            cur_chunk.append(frame)
        prev_frame = frame
    if len(cur_chunk) != 0: # Add current chunk at the end of the data
        total_chunks.append(cur_chunk)


    # Go through each locomotor bout and split into checking events
    ## Find all intervals between two consecutive visits to the home base
    checkingBoutsDurations = []
    boutLeftPoints = []
    boutRightPoints = []
    ch = 0
    removalIndices = []
    for locomotorBout in total_chunks:
        right_points = [] # start of hb visitation (think of it as the ')', or end, of an excursion)
        left_points = [] # end of hb visitation (think of it as the '(', or start, of an excursion)
        # hb_visit = False if env.SpecimenLocation(locomotorBout[0][1], locomotorBout[0][2]) != mainHomeBase or locomotorBout[0][4] == 1 else True # Check if specimen is in homebase and is visiting it.
        # first_visit = True if hb_visit else False # Covers the edge case of the bouts beginning with a lingering episode
        first_visit = True
        f = 0
        while f < len(locomotorBout):
            stopLocale, preStopIndex, postStopIndex = CalculateStopLocale(locomotorBout[f:], env, index=False)
            if stopLocale == -1: # no more visitations, period
                break
            elif stopLocale == mainHomeBase:
                if first_visit:
                    first_visit = False
                else: # Currently between two consecutive home base visits
                    right_points.append(f + preStopIndex)
                left_points.append(f + postStopIndex - 1)
            f += postStopIndex

        if first_visit: # No visit to the homebase, mark this locomotor bout for removal and skip the rest of the analysis
            removalIndices.append(ch)
            ch += 1
            continue
        
        curCheckingBoutsDuration = []
        for i in range(len(right_points)): # Get total excursion lengths
            start_of_excursion = left_points[i]
            end_of_excursion = right_points[i]
            curCheckingBoutsDuration.append(end_of_excursion + 1 - start_of_excursion)
        if len(curCheckingBoutsDuration) > 0: # If visited only once, or if there's no visit to the home base or something.
            checkingBoutsDurations.append(curCheckingBoutsDuration)
        else:
            checkingBoutsDurations.append([0])
        boutLeftPoints.append(left_points)
        boutRightPoints.append(right_points)
        ch += 1
        

    relevantChunks = []
    for i in range(len(total_chunks)): # Remove all chunks that don't have at least one visit to the main homebase
        if i not in removalIndices:
            relevantChunks.append(total_chunks[i])

    if len(relevantChunks) == 0: # No checking bouts exist.
        return [] # no bouts to check


    ## Calculate relevant values based on all bouts
    checkingBoutsDurationsFlattened = [x for cBD in checkingBoutsDurations for x in cBD if x != 0]
    meanTimeReturn = np.sum(checkingBoutsDurationsFlattened) / max(len(checkingBoutsDurationsFlattened), 1) # Mean time of lingering episode
    q75MeanReturn, q25MeanReturn = np.percentile(checkingBoutsDurationsFlattened, [75, 25])
    iqrMeanReturn = q75MeanReturn - q25MeanReturn

    ## Create truth mask on each locomotour bout to split them
    returnIntervalTruthMask = []
    for locoBoutReturnIntervals in checkingBoutsDurations:
        totalReturnIntervals = np.array(locoBoutReturnIntervals)
        outlierReturnIntervals = (totalReturnIntervals >= (meanTimeReturn + 1.5 * iqrMeanReturn))
        returnIntervalTruthMask.append(outlierReturnIntervals)

    ## Split locomotor bouts into separate bouts of checking.
    boutSplits = []
    for b in range(len(relevantChunks)):
        currentSplits = []
        starts = boutLeftPoints[b]
        ends = boutRightPoints[b]
        for i in range(len(ends)):
            if returnIntervalTruthMask[b][i]: # If the current return interval is an outlier
                currentSplits.append(starts[i])
        boutSplits.append(currentSplits)

    ### Split locomotor bouts into checking bouts (and concatenate them to one long list of bouts)
    checkingBouts = []
    for b in range(len(relevantChunks)):
        prev_split = 0
        currentBoutSplits = boutSplits[b]
        currentLocomotorBout = relevantChunks[b]
        if len(currentBoutSplits) > 0: # If current locomotor bout needs to be split up
            for i in range(len(currentBoutSplits)): # Add the splits as separate checking bouts
                actualSplitPoint = currentBoutSplits[i] + 1
                curCheckingBout = currentLocomotorBout[prev_split:actualSplitPoint]
                
                checkingBouts.append(curCheckingBout)
                prev_split = actualSplitPoint
            # Append the final checking bout to the total checking bouts list
            finalCheckingBout = currentLocomotorBout[prev_split:]
            checkingBouts.append(finalCheckingBout)
        else:
            checkingBouts.append(currentLocomotorBout)

    # Final filtering -> Look through each checking bout and confirm that they have at least one visit to the homebase & two progression episodes (confirm how long an episode has to be).
    final_bouts = []

    for cBout in checkingBouts:
        addBout = False
        progressions = 0
        hbVisit = False
        progEp = False

        # Check if main home base is visited at least once
        f = 0
        while f < len(cBout):
            stopLocale, preStopIndex, postStopIndex = CalculateStopLocale(cBout[f:], env, index=False)
            if stopLocale == -1: # no more visitations, period
                break
            elif stopLocale == mainHomeBase:
                hbVisit = True
                break
            f += postStopIndex
        
        if not hbVisit: # No visit to main homebase; skip
            continue

        # Check if there are least two progressive episodes in the bout
        for i in range(len(cBout)):
            frame = cBout[i]

            if frame[4] == 1 and not progEp: # Check if there are at least two progressions (by checking the number of progression episodes) in a checking bout
                progressions += 1
                progEp = True
            elif frame[4] == 0 and progEp:
                progEp = False
            
            if progressions == 2: # if the two progression episodes found, end search early.
                addBout = True
                break
        
        if addBout: # Check if the bout satisfies the final filtering requirements. If so, add it to the final bouts.
            final_bouts.append(cBout)
    
    return final_bouts


## Bout Summary Measures ##

def Calculate_Bout_Total(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None):
    """
        Calculates total number of bouts in a session.

        Also referred to as BoutNumber_max

        Reference ID is: calc_bout_totalBouts
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_bout_totalBouts', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    checkingBouts = requiredSummaryMeasures["calc_boutsOfChecking"]

    return len(checkingBouts)

def Calculate_Bout_Total_Duration(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None):
    """
        Calculates total duration of bouts of checking in a session (in seconds).

        Also referred to as DurationOfBout_s_sum.
        
        TODO: Ask what DurationOfBout_s is.

        Reference ID is: calc_bout_totalBoutDuration
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_bout_totalBoutDuration', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    checkingBouts = requiredSummaryMeasures["calc_boutsOfChecking"]

    return (sum([len(bout) for bout in checkingBouts])) / FRAMES_PER_SECOND


def Calculate_Bout_Mean_Time_Until_Next_Bout(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None):
    """
        Calculates the mean time to next checking bout (average duartion of inter-bout intervals). Returns it in seconds.

        Also referred to as UNKNOWN

        Reference ID is: calc_bout_meanTimeUntilNextBout
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_bout_meanTimeUntilNextBout', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    checkingBouts = requiredSummaryMeasures["calc_boutsOfChecking"]

    timesUntilNextBout = []
    for i in range(len(checkingBouts) - 1):
        currentBoutEndFrame = checkingBouts[i][-1][0] # Get the last frame's (in the current bout) frame number
        nextBoutStartFrame = checkingBouts[i + 1][0][0] # Get the first frame's (in the next bout) frame number
        timesUntilNextBout.append(nextBoutStartFrame - currentBoutEndFrame) # Add the time (in frames) until next bout
    
    return np.mean(timesUntilNextBout) / FRAMES_PER_SECOND

def Calculate_Bout_Mean_Check_Frequency(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None):
    """
        Calculates the average frequency (per-bout) of rat returning to the homebase during a bout.

        Also referred to as UNKNOWN

        Reference ID is: calc_bout_meanCheckFreq
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_bout_meanCheckFreq', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    checkingBouts = requiredSummaryMeasures["calc_boutsOfChecking"]
    mainHomeBase = requiredSummaryMeasures["calc_homebases"][0]

    totalChecks = 0
    # Find the number of checks (returns to homebase) for every bout
    for bout in checkingBouts:
        f = 0
        while f < len(bout):
            stopLocale, preStopIndex, postStopIndex = CalculateStopLocale(bout[f:], env, index=False)
            if stopLocale == -1: # no more visitations, period
                break
            elif stopLocale == mainHomeBase:
                totalChecks += 1
            f += postStopIndex
        
    return totalChecks / len(checkingBouts)

def Calculate_Bout_Mean_Rate_Of_Checks(data: np.ndarray, env: fsm.Environment, requiredSummaryMeasures: dict, preExistingCalcs: dict = None):
    """
        Calculates the mean rate of checking (or, the average reciprocal return time to the main homebase). Returns in seconds (NEED TO CONFIRM THIS; MAY NEED TO RETURN IN HZ, WHICH WILL NEED ITS OWN DIVISION METHOD THINGY)

        Also referred to as RateOfChecksInBout_Hz

        Reference ID is: calc_bout_meanRateOfChecks
    """
    # Check if required summary measures have been calculated already
    desiredCalcs = HandleMissingInputs('calc_bout_meanRateOfChecks', data, env, requiredSummaryMeasures, preExistingCalcs)

    ### Summary Measure Logic
    checkingBouts = requiredSummaryMeasures["calc_boutsOfChecking"]
    mainHomeBase = requiredSummaryMeasures["calc_homebases"][0]

    
    meanRateOfChecks = 0
    # Find the reciprocal return times
    for bout in checkingBouts:
        excursionTimes = []
        exc = False

        # Start and end frames of excursions -> used to calculate their durations
        start = 0
        end = -1

        f = 0
        while f < len(bout):
            stopLocale, preStopIndex, postStopIndex = CalculateStopLocale(bout[f:], env, index=False)
            if stopLocale == -1: # no more visitations, period
                end = len(bout)
                excursionTimes.append(end - start)
                break
            elif stopLocale == mainHomeBase:
                end = preStopIndex + 1
                excursionTimes.append(end - start)
                start = postStopIndex
            f += postStopIndex
        
        # Add the mean reciprocal return time for the bout.
        meanRateOfChecks += 1 / np.mean(excursionTimes)
            
    return (meanRateOfChecks / len(checkingBouts)) / FRAMES_PER_SECOND
        

### TESTING ###
