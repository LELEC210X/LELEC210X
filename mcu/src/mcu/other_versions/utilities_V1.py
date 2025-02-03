import numpy as np
import unittest

####################################################################################################
# Utility functions

def convertSuffix(value: int | float | str) -> str | float | None:
    """Get the suffixex value or from the suffix obtain the value

    @param value: The value to convert
    @return: The value with the suffix as a string or the value without the suffix as a float, or None if invalid or error
    """
    suffix_map = {
        -24 : ["y", "yocto"],
        -21 : ["z", "zepto"],
        -18 : ["a", "atto"],
        -15 : ["f", "femto"],
        -12 : ["p", "pico"],
        -9  : ["n", "nano"],
        -6  : ["µ", "u" , "micro"],
        -3  : ["m", "milli"],
        0   : ["" , "unit"],
        3   : ["k", "kilo"],
        6   : ["M", "meg", "mega"],
        9   : ["G", "gig", "giga"],
        12  : ["T", "tera"],
        15  : ["P", "peta"],
        18  : ["E", "exa"],
        21  : ["Z", "zetta"],
        24  : ["Y", "yotta"],
    }

    if isinstance(value, (int, float)):
        # Calculate the exponent of the value
        exp = int(np.floor(np.log10(abs(value)) / 3) * 3)
        # Check if the value is in the suffix map
        if exp in suffix_map:
            # Get the suffix
            suffix = suffix_map[exp][0]
            # Return the value with the suffix
            return f"{value / 10**exp:.3f} {suffix}"
        else:
            return f"{value:.3f}"
        
    elif isinstance(value, str):
        # Get the value and the suffix:
        suffix = ""
        for i, c in enumerate(value):
            if not c.isdigit() and c != ".":
                suffix = value[i:].strip()
                value = value[:i].strip()
                break
        # Try to convert the value to a float
        try:
            value = float(value)
        except ValueError:
            return None
        # Check if the suffix is in the suffix map
        for exp, suffixes in suffix_map.items():
            if suffix in suffixes:
                return value * 10**exp
    # If the value is not a number or a string return None 
    return None

####################################################################################################
# Unit tests

class TestConvertSuffix(unittest.TestCase):
    def test_exponents(self):
        suffix_map = {
            -24 : ["y", "yocto"],
            -21 : ["z", "zepto"],
            -18 : ["a", "atto"],
            -15 : ["f", "femto"],
            -12 : ["p", "pico"],
            -9  : ["n", "nano"],
            -6  : ["µ", "u" , "micro"],
            -3  : ["m", "milli"],
            0   : ["" , "unit"],
            3   : ["k", "kilo"],
            6   : ["M", "meg", "mega"],
            9   : ["G", "gig", "giga"],
            12  : ["T", "tera"],
            15  : ["P", "peta"],
            18  : ["E", "exa"],
            21  : ["Z", "zetta"],
            24  : ["Y", "yotta"],
        }
        for exp, suffixes in suffix_map.items():
            value = 1.2346 * 10**exp
            self.assertEqual(convertSuffix(value), f"1.235 {suffixes[0]}")
            for suffix in suffixes:
                self.assertEqual(convertSuffix(f"1.2346 {suffix}"), value)

    def test_invalid(self):
        self.assertIsNone(convertSuffix("1.2345 invalid"))
        self.assertIsNone(convertSuffix("invalid 1.2345"))
        self.assertIsNone(convertSuffix("invalid"))

    def test_rounding(self):
        self.assertEqual(convertSuffix(1.2346), "1.235 ")
        self.assertEqual(convertSuffix(1.2344), "1.234 ")
        self.assertEqual(convertSuffix(1.2346e-3), "1.235 m")
        self.assertEqual(convertSuffix(1.2344e-3), "1.234 m")

    def test_big_exponentials(self):
        self.assertEqual(convertSuffix("89385 G"), 89385*1e9)
        self.assertEqual(convertSuffix("82458.20498 T"), 82458.20498*1e12)


####################################################################################################    

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)
