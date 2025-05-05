from .python_generate_xlsx_report import add_numeric_sheet_to_file, gera_metrica
from argparse import ArgumentParser
import logging

logging.basicConfig(level=logging.DEBUG)


def main():
    parser = ArgumentParser(description="CLI para python_sample_xlsx_report")
    subparsers = parser.add_subparsers(dest='comando', required=True)

    parser_add = subparsers.add_parser('add_numeric_sheet')
    parser_add.add_argument('file')

    parser_metrica = subparsers.add_parser('gera_metrica')
    parser_metrica.add_argument('file')

    parser_both = subparsers.add_parser('run_both')
    parser_both.add_argument('file')

    args = parser.parse_args()
    add_numeric_sheet_to_file(path=args.file)
    gera_metrica(path=args.file)
    logging.info(f"Info: {parser.print_help()}")


if __name__ == "__main__":
    main()
    
