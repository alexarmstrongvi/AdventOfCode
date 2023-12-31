from pathlib import Path
import sys

digit_strings = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
)
def main():
    vals = []
    for line in Path(sys.argv[1]).open('r'):
        digits = []
        for i in range(len(line)):
            if line[i].isdigit():
                digits.append(int(line[i]))
                continue
            for digit, digit_string in enumerate(digit_strings):
                if line.startswith(digit_string, i):
                    digits.append(digit)
                    break
        val = 10*digits[0] + digits[-1]
        print(f'{line.strip()} -> {digits} -> {val}')
        vals.append(val)

    print(sum(vals))
    with open('solution.txt', 'w') as ofile:
        for val in vals:
            ofile.write(f'{val}\n')
        ofile.write(f'\n{sum(vals)}\n')

if __name__ == '__main__':
    main()
