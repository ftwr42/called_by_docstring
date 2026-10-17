import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='called_by Docstring',
                                     description='adds a :called_by: field to the docstring of a function, '
                                                 'indicating a list of functions that call it.',
                                     epilog='The truth is out there!')

    parser.add_argument('-p', '--path', type=str, required=False, help='Path to source dir to')

    args = parser.parse_args()

    # if path is not provided, use the current working directory
    if args.path is None:
        import os
        args.path = os.getcwd()

    # check if the provided path is a valid directory
    if not os.path.isdir(args.path):
        raise ValueError(f"The provided path '{args.path}' is not a valid directory.")

