from yta_constants.enum import YTAEnum as Enum


class TextFinderMode(Enum):
    """
    This is the mode in which we will look for the terms
    in the given segment text to find any coincidences.
    """

    EXACT = 'exact'
    """
    The term found must be exactly matched on the text,
    which means that accents and punctuation marks will
    be considered.
    """
    IGNORE_CASE_AND_ACCENTS = 'ignore_case_and_accents'
    """
    The term found must match, in lower case and ignoring
    the accents, the text.
    """