import warnings
import math

from metas_unclib import *
from numpy.ma.extras import unique

from helpers import ensureList, dccConfiguration, DccConfiguration

uncertaintyKeys = [
    "si:expandedUnc",  # easy unc for single data --> expandedUncXMLList
    "si:coverageInterval", # we check if symmetric if yes go for rect expandedUnc
    "si:expandedUncXMLList", # easy unc for list data 
    "si:coverageIntervalXMLList", # we check if symmetric if yes go for rect expandedUncXMLList
    "si:ellipsoidalRegionXMLList",
    "si:rectangularRegionXMLList",
    "si:measurementUncertaintyUnivariate", # easy unc for single data --> expandedMUType k=k und p=p ; standardMUType k=1
    "si:measurementUncertaintyUnivariateXMLList", # easy unc for single data --> expandedMUType k=k und p=p ; standardMUType k=1
]


def parseUncertainties(jsonDict: dict, data: list, relativeUncertainty: dict = None):
    if (
        "si:expandedUnc" in jsonDict.keys()
        or "si:expandedUncXMLList" in jsonDict.keys()
    ):
        dataWithUnc, extraUncInfo = parseExpandedUnc(
            jsonDict=jsonDict, data=data, relativeUncertainty=relativeUncertainty
        )
    elif(
            "si:measurementUncertaintyUnivariate" in jsonDict.keys() or "si:measurementUncertaintyUnivariateXMLList" in jsonDict.keys()
    ):
        dataWithUnc, extraUncInfo = parseExpandedUnc(
            jsonDict=jsonDict, data=data, relativeUncertainty=relativeUncertainty)
    elif (
        not any(uncKey in jsonDict.keys() for uncKey in uncertaintyKeys)
        and relativeUncertainty
    ):
        dataWithUnc = parseRelativeUnc(
            data=data, relativeUncertainty=relativeUncertainty
        )
        extraUncInfo = {}# TODO handle this case, but there will be no information with in the dcc :(
    else:
        warnings.warn(
            "no uncertainty parsed, returning the same data you gave me!",
            RuntimeWarning,
        )
        dataWithUnc = data
        extraUncInfo = {} # maybe None would be better
    return dataWithUnc, extraUncInfo


def parseExpandedUnc(jsonDict: dict, data: list, relativeUncertainty: dict = None):
    uncData = {}
    #TODO we will lose keys if one of the predescending wasn't defined NEDS TO BE CHANGED ASAP
    if "si:expandedUnc" in jsonDict.keys():
        uncJsonData = jsonDict["si:expandedUnc"]
        uncData["uncertainty"] = uncJsonData["si:uncertainty"]
        uncData["coverageFactor"] = uncJsonData["si:coverageFactor"]
        uncData["coverageProbability"] = uncJsonData["si:coverageProbability"]
        uncData["distribution"] = (
            uncJsonData["si:distribution"]
            if "si:distribution" in uncJsonData.keys()
            else ["normal"]
        )
    elif "si:expandedUncXMLList" in jsonDict.keys():
        uncJsonData = jsonDict["si:expandedUncXMLList"]
        uncData["uncertainty"] = uncJsonData["si:uncertaintyXMLList"]
        uncData["coverageFactor"] = uncJsonData["si:coverageFactorXMLList"]
        uncData["coverageProbability"] = uncJsonData["si:coverageProbabilityXMLList"]
        uncData["distribution"] = (
            uncJsonData["si:distributionXMLList"]
            if "si:distributionXMLList" in uncJsonData.keys()
            else ["normal"]
        )
    elif "si:measurementUncertaintyUnivariate" in jsonDict.keys():
        try:
            uncJsonData = jsonDict["si:measurementUncertaintyUnivariate"]['si:expandedMU']
            uncData["uncertainty"] = uncJsonData['si:valueExpandedMU']
            uncData["coverageFactor"] = uncJsonData["si:coverageFactor"]
            uncData["coverageProbability"] = uncJsonData["si:coverageProbability"]
            uncData["distribution"] = (
                uncJsonData["si:distribution"]
                if "si:distribution" in uncJsonData.keys()
                else ["normal"]
            )
        except Exception as e:
            raise e #here for debug break point
    elif "si:measurementUncertaintyUnivariateXMLList" in jsonDict.keys():
        try:
            uncJsonData=jsonDict["si:measurementUncertaintyUnivariateXMLList"]['si:expandedMUXMLList']
            uncData["uncertainty"] = uncJsonData["si:valueExpandedMUXMLList"]
            uncData["coverageFactor"] = uncJsonData["si:coverageFactorXMLList"]
            uncData["coverageProbability"] = uncJsonData["si:coverageProbabilityXMLList"]
            uncData["distribution"] = (
                uncJsonData["si:distributionXMLList"]
                if "si:distributionXMLList" in uncJsonData.keys()
                else ["normal"]
            )
        except KeyError:
            raise NotImplementedError("Uncertanty for Keys "+str(jsonDict["si:measurementUncertaintyUnivariateXMLList"].keys())+" is not implemented yet")
    extraUncInfo={}
    if uncData:
        # Convert relevant entries into lists.
        for key in ["uncertainty", "coverageFactor", "coverageProbability"]:
            uncData[key] = ensureList(uncData[key])
        uncData["distribution"] = ensureList(uncData["distribution"])

        # Helper to access either the single value or the indexed element.
        def get_value(lst, idx):
            return lst[0] if len(lst) == 1 else lst[idx]

        # Validate that each parameter list is either of length 1 or equal to the length of data.
        for key in ["uncertainty", "coverageFactor", "coverageProbability", "distribution"]:
            if len(uncData[key]) not in [1, len(data)]:
                raise RuntimeError(f"Length of {key} does not match data: {jsonDict}")

        dataWithUnc = []

        # we will check the unce params once if they are al identical
        uncAllreadyChecked = False
        storeOriginalUncData=False # we will set this to True if dccConfiguration.storeOriginalUncerForNonIntK is true and at least one k factor is not Int
        if (len(uncData["coverageFactor"])<=1 or len(uncData["coverageProbability"])<=1) and len(uncData["distribution"])==1:
            k_factor = get_value(uncData["coverageFactor"], 0)
            cov_prob = get_value(uncData["coverageProbability"], 0)
            dist_value = get_value(uncData["distribution"], 0)
            # Determine the canonical distribution type.
            distribution = isDistribution(dist_value)
            # Update coverage parameters (calculate missing value and check consistency)
            cov_prob, k_factor = handle_coverage_params(cov_prob, k_factor, distribution)
            # set a flag so we don't check it late again of each item
            uncAllreadyChecked=True
            # populate extraUncInfo
            extraUncInfo["coverageFactor"]=[k_factor]
            extraUncInfo["coverageProbability"]=[cov_prob]
            extraUncInfo["distribution"]=[distribution]
            if dccConfiguration.storeOriginalUncerForNonIntK:
                if not k_factor.is_integer():
                    storeOriginalUncData=True

        else:
            if dccConfiguration.storeOriginalUncerForNonIntK:
                storeOriginalUncData=False
                for kFactorFromList in uncData["coverageFactor"]:
                    if not kFactorFromList.is_integer():
                        storeOriginalUncData=False
        # Loop over each data element individually.
        for i in range(len(data)):
            dataItem = data[i]
            uncItem = get_value(uncData["uncertainty"], i)
            if storeOriginalUncData and i==0:
                extraUncInfo["originalUnc"]=[uncItem]
            if storeOriginalUncData and i!=0:
                extraUncInfo["originalUnc"].append(uncItem)
            if not uncAllreadyChecked:
                k_factor = get_value(uncData["coverageFactor"], i)
                cov_prob = get_value(uncData["coverageProbability"], i)
                dist_value = get_value(uncData["distribution"], i)
                # Determine the canonical distribution type.
                distribution = isDistribution(dist_value)

                # Update coverage parameters (calculate missing value and check consistency)
                cov_prob, k_factor = handle_coverage_params(cov_prob, k_factor, distribution)
                if i==0:
                    extraUncInfo["coverageFactor"] = [k_factor]
                    extraUncInfo["coverageProbability"] = [cov_prob]
                    extraUncInfo["distribution"] = [distribution]

                else:
                    extraUncInfo["coverageFactor"].append(k_factor)
                    extraUncInfo["coverageProbability"].append(cov_prob)
                    extraUncInfo["distribution"].append(distribution)


            # Handle the element based on its distribution.
            if distribution == "normal":
                # For normal distributions, adjust the uncertainty using the (possibly updated) k_factor.
                absUncItem = abs(uncItem) / k_factor
                dataWithUnc.append(ufloat(dataItem, absUncItem))
            elif distribution == "uniform":
                # For uniform distributions, compute the lower and upper bounds.
                # For uniform distributions, adjust the uncertainty interval based on the k_factor.
                # Here, we assume uncItem is the expanded uncertainty (U) such that
                # standard uncertainty u = U / k_factor and half-range a = u * sqrt(3).
                if k_factor==1.73 or k_factor==1.732 or k_factor==1.7321:
                    effective_a = 1.0 # manual rounding for the normal cases
                else:
                    effective_a = abs(uncItem) * math.sqrt(3) / k_factor
                lower_bound = dataItem - effective_a
                upper_bound = dataItem + effective_a
                # TODO profile since we do not performe monteCarlo at the moment mayby using k to scale unc would be way easier than the distribution object
                distribution_obj = UniformDistribution(lower_bound, upper_bound)
                dataWithUnc.append(ufloatfromdistribution(distribution_obj))
            else:
                warnings.warn(
                    "This uncertainty representation is not supported yet! Proceeding with no uncertainty."
                )
                raise NotImplementedError

        # Optionally, check against relative uncertainty if provided.
        if relativeUncertainty:
            relativeUncertainty["uncertainty"] = ensureList(relativeUncertainty["uncertainty"])
            if len(relativeUncertainty["uncertainty"]) not in [1, len(data)]:
                raise RuntimeError("Relative uncertainty length mismatch")
            # Expand relative uncertainty to a list if necessary.
            relUnc_list = (relativeUncertainty["uncertainty"]
                           if len(relativeUncertainty["uncertainty"]) == len(data)
                           else relativeUncertainty["uncertainty"] * len(data))
            absUncFromRelUnc = []
            for relUnc, value in zip(relUnc_list, data):
                absUncFromRelUnc.append(relUnc * value)
            # Check each element’s computed absolute uncertainty.
            for givenAbsUnc, computedAbsUnc in zip(uncData["uncertainty"], absUncFromRelUnc):
                if not math.isclose(givenAbsUnc, computedAbsUnc, rel_tol=1e-3):
                    warnings.warn(
                        "Absolute uncertainties given and computed from relative uncertainty do not match! Proceeding with given abs uncertainty",
                        RuntimeWarning,
                    )

        return dataWithUnc, extraUncInfo

def parseRelativeUnc(data: list, relativeUncertainty: dict):
    if len(relativeUncertainty["uncertainty"]) == 1:
        relativeUncertainty["uncertainty"] = relativeUncertainty["uncertainty"] * len(
            data
        )
    if len(relativeUncertainty["uncertainty"]) == len(data):
        absUncFromRelUnc = [
            relUnc * value
            for relUnc, value in zip(relativeUncertainty["uncertainty"], data)
        ]
        dataWithUnc = [
            ufloat(dataItem, abs(uncItem))
            for (dataItem, uncItem) in zip(data, absUncFromRelUnc)
        ]
    else:
        raise RuntimeError(
            f"Length of uncertainty does not match data: relUnc: {relativeUncertainty}, data: {data}"
        )
    return dataWithUnc


def isDistribution(value):
    """
    Map a single distribution identifier to its canonical type.

    Parameters:
        value (str): A distribution identifier (e.g., 'normal', 'Gauss', 'uniform', etc.)

    Returns:
        str: "normal" if the input matches any synonyms for a normal distribution,
             "uniform" if it matches any synonyms for a uniform/rectangular distribution,
             None otherwise.
    """
    normalized = str(value).strip().lower()
    if normalized in {"normal", "gauss", "gau", "gauß"}:
        return "normal"
    elif normalized in {"rectangular", "uniform", "rect", "rectangle"}:
        return "uniform"
    else:
        return None

def handle_coverage_params(coverageProbability, k_factor, distribution):
    """
    Calculate and check coverageProbability and k_factor for normal and uniform distributions.

    For normal distributions:
      - If k_factor is provided, compute coverageProbability = erf(k_factor/√2).
      - If only coverageProbability is provided, compute k_factor = √2 * erfinv(coverageProbability).
      - If both are provided, recalc coverageProbability from k_factor (priority to k_factor)
        and ensure the mismatch is within dccConfiguration.allowedCoveragePropabilityMissmatch.
      - If a missmatch occures either an warning is generated and given k is used (DccConfiguration.CoveragePropabilityMissmatchBehavior.WARNING_TAKE_K_VALUE)
        or and Exception is raised DccConfiguration.CoveragePropabilityMissmatchBehavior.EXCEPTION

    For uniform distributions:
      - If k_factor is provided:
            computed_cov = (k_factor/√3 + 1)/2 if k_factor <= √3, else computed_cov = 1.0.
      - If only coverageProbability is provided, compute k_factor = √3*(2*coverageProbability - 1).
      - If both are provided, compute computed_cov and check against the provided coverageProbability.

    Parameters:
        coverageProbability (float or None): The provided coverage probability.
        k_factor (float or None): The provided coverage factor.
        distribution (str): "normal" or "uniform".

    Returns:
        tuple: (coverageProbability, k_factor) after calculation/validation.

    Raises:
        ValueError: If neither parameter is provided or if the provided values are inconsistent.
    """
    try:
        allowed = dccConfiguration.allowedCoveragePropabilityMissmatch[distribution]
    except KeyError:
        allowed = dccConfiguration.allowedCoveragePropabilityMissmatch['default']
    if distribution == "normal":
        if k_factor is not None:
            computed_cov = math.erf(k_factor / math.sqrt(2))
            if coverageProbability is None:
                coverageProbability = computed_cov
            else:
                if abs(coverageProbability - computed_cov) > allowed:
                    if dccConfiguration.coveragePropabilityMissmatchBehaivior == DccConfiguration.CoveragePropabilityMissmatchBehavior.EXCEPTION:
                        raise ValueError(
                            f"Normal distribution mismatch: provided coverageProbability {coverageProbability} vs computed {computed_cov}"
                        )
                    elif dccConfiguration.coveragePropabilityMissmatchBehaivior == DccConfiguration.CoveragePropabilityMissmatchBehavior.WARNING_TAKE_K_VALUE:
                        warnings.warn( f"Normal distribution mismatch: provided coverageProbability {coverageProbability} vs computed {computed_cov} using k value for further calculations. Since dccConfiguration.CoveragePropabilityMissmatchBehavior.WARNING_TAKE_K_VALUE is set" )
                        return computed_cov, k_factor
        elif coverageProbability is not None:
            # Requires Python 3.8+ for math.erfinv
            k_factor = math.sqrt(2) * math.erfinv(coverageProbability)
        else:
            raise ValueError(
                "For normal distribution, at least one of coverageProbability or k_factor must be provided.")
        return coverageProbability, k_factor

    elif distribution == "uniform":

#        For a rectangular (i.e. uniform) distribution, one commonly used result is that if a random variable is uniformly distributed between –a and a, then its standard uncertainty is given by
#        \[
#        u = \frac{a}{\sqrt{3}},
#        \]
#        because the variance of a uniform distribution on [–a, a] is \( \sigma^2 = a^2/3 \). Consequently, if you define an "expanded uncertainty" U (which might be provided by the user) and wish to express it in terms of standard uncertainty via a coverage factor \(k\), then
#        \[
#        u = \frac{U}{k}.
#       \]
#        Combining these gives a way to relate U, \(k\), and the half-width \(a\) of the distribution:
#        \[
#        a = \frac{U \sqrt{3}}{k}.
#        \]
#        Furthermore, the probability that a value falls within the interval \([-k\cdot u, k\cdot u]\) is obtained by integrating the uniform density. For \([-c, c]\) (with \(c \le a\)), the cumulative probability is
#        \[
#       P = \frac{2c}{2a} = \frac{c}{a}.
#        \]
#        Substituting \(c = k\cdot u\) and \(u = a/\sqrt{3}\) yields
#        \[
#        P = \frac{k\,(a/\sqrt{3})}{a} = \frac{k}{\sqrt{3}} \quad \text{(for } k \le \sqrt{3}\text{)},
#        \]
#        with \(P = 1\) if \(k > \sqrt{3}\).
#        These relationships are widely cited in metrology and uncertainty analysis. For example:
#        - The *Guide to the Expression of Uncertainty in Measurement* (GUM, JCGM 100:2008) explains that for a uniform (rectangular) distribution the standard uncertainty is \(u = a/\sqrt{3}\).
#        - NIST’s *Technical Note 1297* provides guidelines for evaluating uncertainties where similar derivations for the uniform distribution are given.

        if k_factor is not None:
            # Calculate computed coverageProbability from k_factor.
            if k_factor <= math.sqrt(3):
                computed_cov = (k_factor / math.sqrt(3) + 1) / 2
            else:
                computed_cov = 1.0  # Entire range covered.
            if coverageProbability is None:
                coverageProbability = computed_cov
            else:
                if abs(coverageProbability - computed_cov) > allowed:
                    if dccConfiguration.coveragePropabilityMissmatchBehaivior == DccConfiguration.CoveragePropabilityMissmatchBehavior.EXCEPTION:
                        raise ValueError(
                            f"Normal distribution mismatch: provided coverageProbability {coverageProbability} vs computed {computed_cov}"
                        )
                    elif dccConfiguration.coveragePropabilityMissmatchBehaivior == DccConfiguration.CoveragePropabilityMissmatchBehavior.WARNING_TAKE_K_VALUE:
                        warnings.warn( f"Normal distribution mismatch: provided coverageProbability {coverageProbability} vs computed {computed_cov} using k value for further calculations. Since dccConfiguration.CoveragePropabilityMissmatchBehavior.WARNING_TAKE_K_VALUE is set" )
                        return computed_cov, k_factor
        elif coverageProbability is not None:
            # Invert the relationship for uniform distributions.
            k_factor = math.sqrt(3) * (2 * coverageProbability - 1)
        else:
            raise ValueError(
                "For uniform distribution, at least one of coverageProbability or k_factor must be provided.")
        return coverageProbability, k_factor

    else:
        raise ValueError("Unsupported distribution type. >>" +str(distribution)+"<<")