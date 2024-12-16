"""
Title: Utilities
Description: Generic functions used elsewhere
Author: Jasper Cooper
"""

# Generic function for collapsing a list of strings by comma. Used to print
# messages in other functions
def comma_join(string_list):
    separator = ", "
    return separator.join(string_list)

# Generic function for subsetting a list of strings
def subset_string(string_list, substring):
    subset = [item for item in string_list if substring in item]
    return subset
