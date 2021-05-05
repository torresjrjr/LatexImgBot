#!/usr/bin/python

from random import randint


def get_random_example():
    File = open("examples.tex", 'r')
    File.seek(0)

    example_lines  = []
    record         = False

    for i, line in enumerate(File):
        if i == 0:
            if not line.startswith("%TOTAL"):
                raise Exception("No total on first line.")
            else:
                total_examples = int( line.split()[1] )
                example_number = randint(1, total_examples)
                continue

        if line.startswith(f"%BEGIN {example_number}"):
            record = True
            continue

        if line.startswith(f"%END {example_number}"):
            record = False
            break

        if record:
            example_lines += [line]

    example = ''.join(example_lines)
    return example


print(get_random_example())
