
def change_case(orig_string: str):
    return orig_string.swapcase()


def split_in_half(orig_string: str):
    middle = len(orig_string) // 2
    return orig_string[:middle], orig_string[middle:]


def remove_special_characters(orig_string: str):
    result = ""
    for char in orig_string:
        if char.isalnum() or char == " ":
            result += char
    return result
