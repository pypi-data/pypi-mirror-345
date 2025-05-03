"""DependenciesSM

This module contains all of the required functionality in regards to proper planning of SM calculations (in particular, their summary measure and data dependencies).


Authors: Brandon Carrasco
Created on: 15-01-2025
Modified on: 08-04-2025
"""

# Summary Measure Dependencies

from . FunctionalSM import DATA_DEPENDENCIES, SM_DEPENDENCIES
from itertools import chain


### On resolving summary measure dependencies (on other summary measures being calculated before hand) ###

# SMs can be floaters (no dependencies nor does anything depend on it) -> Automatically shoved to the back of the list
# SMs can be tails (no dependencies, but some SMs depend on it) -> Automatically shoved to the back of the list (in front of or behind the floaters; it doesn't matter)
# SMs can be heads (some dependencies, but nothing depends on it) -> Automatically shoved to the front of the list
# SMs can be links (some dependencies, but some other SMs depend on it as well) -> Run through list of SMs not in list
#   -> If all of an SM's dependencies are in the re-ordered list, add the SM to the list (before the heads)
#   -> Otherwise, skip over it and move onto the next one. Do so until all links have been added to the list. 
## O(n^2) time! But considering how few summary measures we'll be really calculating, I think it's alright.

### End of digression

# Karpov (The Summary Measure Dependency Resolver)

class Karpov:

    def AddRequiredSummaryMeasures(summary_measures: list[str]) -> list[str]:
        """Given a list of summary measures, checks and produces a list of all dependencies (other summary measures) that must be calculated prior to them.

        Parameters
        ----------
        summary_measures : list[str]
            List of summary measures to be calculated.

        Returns
        -------
        requiredSMs : list[str]
            Summary measures that will be calculated as well as the summary measures necessary to calculate them.
        """
        requiredSMs = []
        for sm in summary_measures:
            if sm not in SM_DEPENDENCIES.keys(): # Summary measure has no dependencies
                continue
            dependencies = [dep for dep in SM_DEPENDENCIES[sm] if dep not in summary_measures] # Get all SM dependencies for the current summary measure, that aren't in the original request or updated summary measure list
            if len(dependencies) > 0:
                dependencies = dependencies + Karpov.AddRequiredSummaryMeasures(dependencies + summary_measures) # Get dependencies of new summary measures
                requiredSMs = requiredSMs + dependencies # If dependency not already in summary measures, add it
        return list(set(requiredSMs))

    def OrderSummaryMeasures(summary_measures: list[str]) -> list[str]:
        """Given a list of summary measures, re-orders the summary measures list such that all dependencies will be  calculated prior to their dependent summary measure.
        
        Parameters
        ----------
        summary_measures : list[str]
            List of summary measures to be calculated.

        Returns
        -------
        reordered_summary_measures : list[str]
            Summary measures that will be calculated in an order that will prevent dependent summary measures from being calculated prior to the summary measure(s) they're dependent on.
        """
        all_dep = list(chain.from_iterable([SM_DEPENDENCIES[sm] for sm in summary_measures if sm in SM_DEPENDENCIES.keys()])) # Flatten full list of dependencies
        full_dependencies = list(set(all_dep)) # Get rid of duplicate dependences
        head_SMs = [sm for sm in summary_measures if sm not in full_dependencies and sm in SM_DEPENDENCIES.keys()] # If sm not a dependency, but is dependent
        floater_SMs = [sm for sm in summary_measures if sm not in full_dependencies and sm not in SM_DEPENDENCIES.keys()] # If sm is neither a dependency or dependent
        tail_SMs = [sm for sm in summary_measures if sm in full_dependencies and sm not in SM_DEPENDENCIES.keys()] # If sm is a dependency, but not dependent
        link_SMs = list(set(summary_measures) -  set(head_SMs + floater_SMs + tail_SMs)) # If sm is both a dependency and dependent.

        # Add all non-dependent SMs
        reordered_summary_measures = tail_SMs + floater_SMs

        # Iteratively add dependent SMs (that other SMs in the list are dependent on)
        while len(link_SMs) > 0:
            add_SMs = []
            for i in range(len(link_SMs)):
                link = link_SMs[i]
                if all(dep in reordered_summary_measures for dep in SM_DEPENDENCIES[link]): # Check if all dependencies for sm already exists in the reordered summary measures list
                    add_SMs.append(link)
            reordered_summary_measures = reordered_summary_measures + add_SMs # Add all summary measures whose dependencies are satisfied to the ordered list
            link_SMs = [sm for sm in link_SMs if sm not in add_SMs] # Remove all added summary measures

        # Add remaining purely dependent SMs
        reordered_summary_measures = reordered_summary_measures + head_SMs
        return reordered_summary_measures

    def ResolveDependencies(summary_measures: list[str]) -> tuple[list[str], list[str]]:
        """Given a list of summary_measures, return list of data dependencies (aka. data that should be pre-calc'd for efficiency's sake) and the full re-ordered list of SMs that satisfy all SM dependencies.

        Parameters
        ----------
        summary_measures : list[str]
            List of summary measures to be calculated.

        Returns
        -------
        summary_reordered : list[str]
            Summary measures that will be calculated (with dependencies added and ordered in a way to prevent out-of-order summary measure calculations)
        data_depend : list[str]
            Common calculations that will be performed to ensure efficient calculation of data.
        """
        data_depend = set()
        summary_reordered = []

        summary_reordered = Karpov.AddRequiredSummaryMeasures(summary_measures) + summary_measures
        summary_reordered = Karpov.OrderSummaryMeasures(summary_reordered)
        for sm in summary_reordered:
            # Grab data dependency (function to call) from data dependencies constant
            if sm in DATA_DEPENDENCIES.keys():
                for dDep in DATA_DEPENDENCIES[sm]:
                    data_depend.add(dDep)

        return summary_reordered, list(data_depend)

### TESTING ###

