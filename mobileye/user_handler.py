from mobileye import argparse


def get_input() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    # --name NAME --dept DEPARTMENT --id TASK ID
    parser.add_argument("--name", nargs='*')
    parser.add_argument("--dept")
    parser.add_argument("--id", type=int)
    args = parser.parse_args()

    # handle missing args
    while (not args.name):
        args.name = input('Please enter your name: ')
    while (not args.dept):
        args.dept = input('Please enter department: ')
    while (not args.id):
        args.id = input('Please enter task id: ')

    return args.name, args.dept, int(args.id)
