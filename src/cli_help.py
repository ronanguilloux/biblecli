class CLIHelp:
    def __init__(self):
        pass

    def print_usage(self):
        help_text = """
GNT(1)                       Bible CLI Manual                       GNT(1)

NAME
       biblecli - A command-line interface for the Greek New Testament (N1904)

SYNOPSIS
       biblecli [COMMAND | REFERENCE] [ARGS...] [OPTIONS]

DESCRIPTION
       biblecli is a tool for reading and searching the Greek New Testament (N1904)
       along with English and French (TOB) translations.

COMMANDS
       list books
              List all available books in the N1904 dataset.
       
       add -c [COLLECTION] -s [SOURCE] -t [TARGET] --type [TYPE] -n [NOTE]
              Add a new cross-reference to the specified collection.
              
              Arguments:
              -c, --collection: Collection name (e.g. 'nt_ronan', 'ot_ronan')
              -s, --source:     Source reference (e.g. 'Mc 1:1')
              -t, --target:     Target reference (e.g. 'Lc 1:1')
              --type:           Relation type (parallel, allusion, quotation, other). Default: 'other'
              -n, --note:       Note text for the relation

       search [QUERY] (Coming soon)
              Search for specific terms in the New Testament.

REFERENCES
       References can be specified in various formats:
       - Single verse: "Jn 1:1" or "Jean 1:1"
       - Verse range: "Mt 5:1-10"
       - Whole chapter: "Mk 4"

OPTIONS
       -h, --help
              Show this help message and exit.

       -t, --tr [en|fr|gr]
              Specify which translations to display.

       -c, --crossref
              Display cross-references at verse level.

       -f, --crossref-full
              Display cross-references with related verse text.

       -s, --source [SOURCE]
              Filter cross-references by source (e.g. 'tob'). 
"""
        print(help_text)
