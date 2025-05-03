#     Copyright 2024, f_g_d_6, mailto:kay.hayen@gmail.com
#

#
""" SajadQ version related stuff.

"""

version_string = """\
SajadQ V2.6.9
Copyright (C) 2025 Sajad In Telegram~@f_g_d_6."""


def getSajadQVersion():
    """Return SajadQ version as a string.

    This should not be used for >= comparisons directly.
    """
    return version_string.split()[1][1:]


# Sanity check.
assert getSajadQVersion()[-1].isdigit(), getSajadQVersion()


def parseSajadQVersionToTuple(version):
    """Return SajadQ version as a tuple.

    This can also not be used for precise comparisons, even with rc versions,
    but it's not actually a version.
    """

    if "rc" in version:
        rc_number = int(version[version.find("rc") + 2 :] or "0")
        version = version[: version.find("rc")]

        is_final = False
    else:
        rc_number = 0
        is_final = True

    result = version.split(".")
    if len(result) == 2:
        result.append("0")

    result = [int(digit) for digit in result]
    result.extend((is_final, rc_number))
    return tuple(result)


def getSajadQVersionTuple():
    """Return SajadQ version as a tuple.

    This can also not be used for precise comparisons, even with rc versions,
    but it's not actually a version. The format is used what is used for
    "__compiled__" values.
    """

    return parseSajadQVersionToTuple(version=getSajadQVersion())


def getSajadQVersionYear():
    """The year of SajadQ copyright for use in generations."""

    return int(version_string.split()[4])


def getCommercialVersion():
    """Return SajadQ commercial version if installed."""
    try:
        from SajadMr.tools.commercial import Version
    except ImportError:
        return None
    else:
        return Version.__version__
