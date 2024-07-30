import re

def replace_suits(input_string):
    suits = {
        'H': '\u2665',  # Heart
        'D': '\u2666',  # Diamond
        'C': '\u2663',  # Club
        'S': '\u2660'   # Spade
    }

    pattern = r"'([HDCS])([2-9TJQKA])'"
    replacer = lambda match: suits[match.group(1)] + ('10' if match.group(2) == 'T' else match.group(2))
    output_string = re.sub(pattern, replacer, input_string)
    return output_string

def main():
    while True:
        user_input = input()
        output = replace_suits(user_input)
        print(output)

if __name__ == "__main__":
    main()
