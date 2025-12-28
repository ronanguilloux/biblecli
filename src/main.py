import sys
import argparse
from tf.app import use
from tf.fabric import Fabric
import os
import contextlib

# Import new DB module
from book_normalizer import BookNormalizer
from references_db import ReferenceDatabase
from cli_help import CLIHelp

# TOB Configuration
BIBLECLI_DIR="/Users/ronan/Documents/Gemini/antigravity/biblecli"
TOB_DIR = BIBLECLI_DIR+'/tob_tf/TOB/TraductionOecumenique/1.0'

# Initialize Managers
DATA_DIR = os.path.join(BIBLECLI_DIR, "data")
normalizer = BookNormalizer(DATA_DIR)
ref_db = ReferenceDatabase(DATA_DIR, normalizer)

try:
    with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
        TF_TOB = Fabric(locations=[TOB_DIR], silent=True)
        API_TOB = TF_TOB.load('text book chapter verse', silent=True)
except Exception as e:
    API_TOB = None

def get_french_text(book_en, chapter_num, verse_num):
    if not API_TOB:
        return ""
        
    F = API_TOB.F
    L = API_TOB.L
    
    book_fr = normalizer.n1904_to_tob.get(book_en)
    if not book_fr:
        # Try direct mapping if not found (e.g. if N1904 uses spaces instead of underscores)
        book_fr = normalizer.n1904_to_tob.get(book_en.replace(" ", "_"))
        
    if not book_fr:
        return f"[TOB: Book '{book_en}' not found]"

    # 1. Find book node
    book_node = None
    for n in F.otype.s('book'):
        if F.book.v(n) == book_fr:
            book_node = n
            break
            
    if not book_node:
        return f"[TOB: Book '{book_fr}' node not found]"

    # 2. Find chapter node
    chapter_node = None
    for n in L.d(book_node, otype='chapter'):
        if F.chapter.v(n) == int(chapter_num):
            chapter_node = n
            break
            
    if not chapter_node:
        return f"[TOB: Chapter {chapter_num} not found]"

    # 3. Find verse node
    verse_node = None
    for n in L.d(chapter_node, otype='verse'):
        if F.verse.v(n) == int(verse_num):
            verse_node = n
            break
            
    if not verse_node:
        return "" # Verse might not exist in TOB or mapping issue

    # 4. Get text
    return F.text.v(verse_node)

def format_ref_fr(target_str):
    """
    Format a reference like 'ACT.1.25-ACT.1.26' into 'Ac 1:25-26'.
    Converts book codes to French abbreviations.
    """
    if not target_str: return ""
    
    def parse_one(ref):
        parts = ref.split(".")
        if len(parts) >= 3:
            book_code = parts[0]
            chapter = parts[1]
            verse = parts[2]
            fr_abbr = normalizer.code_to_fr_abbr.get(book_code, book_code)
            return fr_abbr, chapter, verse
        return None, None, None

    if "-" in target_str:
        ranges = target_str.split("-")
        if len(ranges) == 2:
            start_ref = ranges[0]
            end_ref = ranges[1]
            
            s_abbr, s_ch, s_vs = parse_one(start_ref)
            
            if "." not in end_ref:
                if s_abbr:
                     return f"{s_abbr} {s_ch}:{s_vs}-{end_ref}"
            
            e_abbr, e_ch, e_vs = parse_one(end_ref)
            
            if s_abbr:
                if e_abbr and s_abbr == e_abbr and s_ch == e_ch:
                    return f"{s_abbr} {s_ch}:{s_vs}-{e_vs}"
                elif e_abbr and s_abbr == e_abbr:
                    return f"{s_abbr} {s_ch}:{s_vs}-{e_ch}:{e_vs}"
                elif e_abbr:
                    return f"{s_abbr} {s_ch}:{s_vs}-{e_abbr} {e_ch}:{e_vs}"
    
    abbr, ch, vs = parse_one(target_str)
    if abbr:
        return f"{abbr} {ch}:{vs}"
        
    return target_str

    
def handle_reference(A, ref_str, show_english=False, show_greek=True, show_french=True, show_crossref=False, cross_refs=None, show_crossref_text=False):
    api = A.api
    T = api.T
    F = api.F
    L = api.L

    # Normalize reference
    ref_str = ref_str.replace(',', ':')
    
    # Check if reference starts with any abbreviation
    parts = ref_str.split()
    if len(parts) >= 2:
        two_word_abbr = f"{parts[0]} {parts[1]}"
        if two_word_abbr in normalizer.abbreviations:
            ref_str = f"{normalizer.abbreviations[two_word_abbr]} {' '.join(parts[2:])}"
            parts = ref_str.split() 
        elif parts[0] in normalizer.abbreviations:
            ref_str = f"{normalizer.abbreviations[parts[0]]} {' '.join(parts[1:])}"
            parts = ref_str.split() 
    elif len(parts) == 1:
        if parts[0] in normalizer.abbreviations:
            ref_str = normalizer.abbreviations[parts[0]]
            parts = [ref_str]

    try:
        # Check if it's a range (e.g., "Luke 1:4-7")
        if "-" in ref_str and ":" in ref_str:
            last_colon_idx = ref_str.rfind(":")
            if last_colon_idx != -1:
                book_chapter = ref_str[:last_colon_idx]
                verses_part = ref_str[last_colon_idx+1:]
                
                if "-" in verses_part:
                    start_v, end_v = verses_part.split("-")
                    start_v = int(start_v)
                    end_v = int(end_v)
                    
                    if ' ' in book_chapter:
                        book, chapter = book_chapter.rsplit(' ', 1)
                        book_fr= normalizer.n1904_to_tob.get(book)
                        if not book_fr: book_fr = book
                        print(f"\n{book_fr} {chapter}:{start_v}-{end_v}")
                    else:
                        book = book_chapter
                        chapter = ""
                        print(f"\n{book_chapter}:{start_v}-{end_v}")
                    
                    for v_num in range(start_v, end_v + 1):
                        single_ref = f"{book_chapter}:{v_num}"
                        node = A.nodeFromSectionStr(single_ref)
                        if node and isinstance(node, int):
                            print_verse(A, node=node, show_english=show_english, show_greek=show_greek, show_french=show_french, show_crossref=show_crossref, cross_refs=cross_refs, show_crossref_text=show_crossref_text)
                        else:
                            if ' ' in book_chapter:
                                b, c = book_chapter.rsplit(' ', 1)
                                print_verse(A, book_en=b, chapter=c, verse=v_num, show_english=show_english, show_greek=show_greek, show_french=show_french, show_crossref=show_crossref, cross_refs=cross_refs, show_crossref_text=show_crossref_text)
                            else:
                                print(f"Could not find verse: {single_ref}")
                    return

        # Check if it's a chapter reference (e.g., "John 13")
        if ":" not in ref_str and " " in ref_str:
            parts = ref_str.rsplit(' ', 1)
            if len(parts) == 2:
                book_name = parts[0]
                try:
                    chapter_num = int(parts[1])
                    
                    book_fr = normalizer.n1904_to_tob.get(book_name)
                    if not book_fr: book_fr = book_name
                    print(f"\n{book_fr} {chapter_num}")
                    
                    chapter_nodes = [n for n in F.otype.s('chapter') 
                                    if F.book.v(n) == book_name and F.chapter.v(n) == chapter_num]
                    
                    if chapter_nodes:
                        chapter_node = chapter_nodes[0]
                        verse_nodes = L.d(chapter_node, otype='verse')
                        
                        for verse_node in verse_nodes:
                            print_verse(A, node=verse_node, show_english=show_english, show_greek=show_greek, show_french=show_french, show_crossref=show_crossref, cross_refs=cross_refs, show_crossref_text=show_crossref_text)
                        return
                    else:
                        if API_TOB:
                            v = 1
                            found_any = False
                            while True:
                                txt = get_french_text(book_name, chapter_num, v)
                                if (not txt or txt.startswith("[TOB:")) and v > 1:
                                    break
                                if txt and not txt.startswith("[TOB:"):
                                    print_verse(A, book_en=book_name, chapter=chapter_num, verse=v, show_english=show_english, show_greek=show_greek, show_french=show_french, show_crossref=show_crossref, cross_refs=cross_refs, show_crossref_text=show_crossref_text)
                                    found_any = True
                                v += 1
                            if found_any: return
                        
                        print(f"Could not find chapter: {ref_str}")
                        return
                except ValueError:
                    pass  
        
        # Fallback to single reference lookup
        node = A.nodeFromSectionStr(ref_str)
        
        if node and isinstance(node, int):
            print_verse(A, node=node, show_english=show_english, show_greek=show_greek, show_french=show_french, show_crossref=show_crossref, cross_refs=cross_refs, show_crossref_text=show_crossref_text)
        else:
            if ":" in ref_str and " " in ref_str:
                parts = ref_str.rsplit(' ', 1)
                book_name = parts[0]
                if ":" in parts[1]:
                    ch_v = parts[1].split(":")
                    if len(ch_v) == 2:
                        try:
                            ch = int(ch_v[0])
                            vs = int(ch_v[1])
                            print_verse(A, book_en=book_name, chapter=ch, verse=vs, show_english=show_english, show_greek=show_greek, show_french=show_french, show_crossref=show_crossref, cross_refs=cross_refs, show_crossref_text=show_crossref_text)
                            return
                        except ValueError:
                            pass

            print(f"Could not find reference: {ref_str}")
            
    except Exception as e:
        print(f"Error processing reference: {e}")

def print_verse(A, node=None, book_en=None, chapter=None, verse=None, show_english=False, show_greek=True, show_french=True, show_crossref=False, cross_refs=None, show_crossref_text=False):
    api = A.api
    T = api.T
    F = api.F
    L = api.L
    
    if node:
        section = T.sectionFromNode(node)
        book_en = section[0]
        chapter = int(section[1])
        verse = int(section[2])
    else:
        chapter = int(chapter)
        verse = int(verse)

    book_fr = normalizer.n1904_to_tob.get(book_en)
    if not book_fr:
        book_fr = normalizer.n1904_to_tob.get(book_en.replace(" ", "_"))
    if not book_fr:
        book_fr = book_en
    
    # Header
    if node:
        print(f"\n{book_fr} {chapter}:{verse}")
    else:
        print(f"\n{book_fr} {chapter}:{verse}")

    # Greek text
    if show_greek and node:
        greek_text = T.text(node)
        if greek_text and greek_text.strip():
            print(f"{greek_text}")
    
    # English translation
    if show_english and node:
        words = L.d(node, otype='word')
        english_text = []
        for w in words:
            trans = F.trans.v(w) if hasattr(F, 'trans') else ""
            if not trans and hasattr(F, 'gloss'):
                trans = F.gloss.v(w)
            english_text.append(trans)
        print(f"{' '.join(english_text)}")
    
    # French translation (TOB)
    if show_french:
        french_text = get_french_text(book_en, chapter, verse)
        if french_text and not french_text.startswith("[TOB:"):
            print(f"{french_text}")
        elif french_text and node:
             print(f"{french_text}")

    # Cross-references
    if show_crossref:
        print("\n––––––––––")
        groups = {"Parallel": [], "Allusion": [], "Quotation": [], "Other": []}
        
        if cross_refs:
            book_code = normalizer.n1904_to_code.get(book_en) or normalizer.n1904_to_code.get(book_en.replace(" ", "_"))
            if book_code:
                # Retrieve references from the standardized DB subset (passed as cross_refs dict)
                # Key format in cross_refs (from ReferenceDatabase.get_references) is "BOOK.C.V"
                source_key = f"{book_code}.{chapter}.{verse}"
                
                # We need to access the structure: { "source_key": { "notes": [], "relations": [] } }
                # Note: load_cross_references previously merged everything into a single dict keyed by source.
                # ReferencesDatabase.get_references returns a filtered dict with the same structure.
                
                data = cross_refs.get(source_key, {})
                relations = data.get("relations", [])
                notes = data.get("notes", [])
                
                if notes:
                    print("    Notes:")
                    for n in notes:
                        print(f"        {n}")
                    print("") 
                
                def sort_key(rel):
                    target = rel.get("target", "")
                    t_book = target.split(".")[0] if "." in target else ""
                    order = normalizer.book_order.get(t_book, 999)
                    try:
                        parts = target.split(".")
                        ch = int(parts[1]) if len(parts) > 1 else 0
                        vs = int(parts[2].split("-")[0]) if len(parts) > 2 else 0
                        return (order, ch, vs)
                    except (ValueError, IndexError):
                        return (order, 0, 0)

                relations.sort(key=sort_key)
                for rel in relations:
                    rel_type = rel.get("type", "other")
                    target = rel.get("target", "")
                    target_fr = format_ref_fr(target)
                    if rel_type == "parallel": groups["Parallel"].append((target, target_fr))
                    elif rel_type == "allusion": groups["Allusion"].append((target, target_fr))
                    elif rel_type == "quotation": groups["Quotation"].append((target, target_fr))
                    else: groups["Other"].append((target, target_fr))

        for label, items in groups.items():
            if items:
                print(f"    {label}: ")
                for target_raw, target_fr in items:
                    print(f"        {target_fr}")
                    if show_crossref_text:
                        refs_to_fetch = []
                        if "-" in target_raw:
                            parts = target_raw.split("-")
                            if len(parts) == 2:
                                start_p = parts[0].split(".")
                                end_p = parts[1].split(".")
                                
                                # Case 1: Full ref to full ref
                                if len(start_p) == 3 and len(end_p) == 3:
                                    b_code = start_p[0]
                                    ch = int(start_p[1])
                                    s_v = int(start_p[2])
                                    e_v = int(end_p[2])
                                    if b_code == end_p[0] and ch == int(end_p[1]):
                                        for v in range(s_v, e_v + 1):
                                            refs_to_fetch.append((b_code, ch, v))

                                # Case 2: Full ref to verse only
                                elif len(start_p) == 3 and len(end_p) == 1:
                                     b_code = start_p[0]
                                     ch = int(start_p[1])
                                     s_v = int(start_p[2])
                                     try:
                                         e_v = int(end_p[0])
                                         if e_v >= s_v:
                                             for v in range(s_v, e_v + 1):
                                                 refs_to_fetch.append((b_code, ch, v))
                                     except ValueError:
                                         pass
                        else:
                            parts = target_raw.split(".")
                            if len(parts) == 3:
                                refs_to_fetch.append((parts[0], int(parts[1]), int(parts[2])))
                        
                        for b_code, ch, vs in refs_to_fetch:
                            b_en = normalizer.code_to_n1904.get(b_code)
                            if b_en:
                                txt = get_french_text(b_en, ch, vs)
                                if txt: print(f"            {txt}")


def handle_list(A, args):
    api = A.api
    F = api.F
    N = api.N
    
    if not args:
        print("Error: Missing argument for 'list'. Available: 'books'")
        return

    subcommand = args[0]
    
    if subcommand == "books":
        print("Available books:")
        for node in N.walk():
            if F.otype.v(node) == 'book':
                print(F.book.v(node))
    else:
        print(f"Unknown list command: {subcommand}")

def handle_add(args):
    # args matches the structure added in main: collection, source, target, type, note
    try:
        ref_db.add_relation(
            collection_name=args.collection,
            source_ref=args.source,
            target_ref=args.target,
            rel_type=args.type,
            note=args.note
        )
        print(f"Successfully added reference to {args.collection}:")
        print(f"  Source: {args.source}")
        print(f"  Target: {args.target}")
        print(f"  Type:   {args.type}")
        print(f"  Note:   {args.note}")
    except ValueError as e:
        print(f"Error adding reference: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")




def main():
    parser = argparse.ArgumentParser(description="N1904 CLI Tool", add_help=False)
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")
    
    # We use a subparser strategy or manual parse to handle "add" vs valid refs
    # Beacuse "add" has specific required args, let's peek at argv[1]
    
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        # Sub-parser for add command
        add_parser = argparse.ArgumentParser(description="Add reference")
        add_parser.add_argument("command", choices=["add"])
        add_parser.add_argument("-c", "--collection", required=True, help="Collection name (e.g. nt_ronan)")
        add_parser.add_argument("-s", "--source", required=True, help="Source reference (e.g. 'Mc 1:1')")
        add_parser.add_argument("-t", "--target", required=True, help="Target reference (e.g. 'Lc 1:1')")
        add_parser.add_argument("--type", default="other", help="Relation type (parallel, allusion, quotation, other)")
        add_parser.add_argument("-n", "--note", default="", help="Note for the relation")
        
        args = add_parser.parse_args(sys.argv[1:])
        handle_add(args)
        return

    # Standard parser for other commands
    parser.add_argument("command_or_ref", nargs="?", help="Command or Bible reference")
    parser.add_argument("args", nargs="*", help="Arguments for the command")
    parser.add_argument("-t", "--tr", nargs="+", choices=["en", "fr", "gr"], help="Translations")
    parser.add_argument("-c", "--crossref", action="store_true", help="Display cross-references")
    parser.add_argument("-f", "--crossref-full", action="store_true", help="Display cross-references with text")
    parser.add_argument("-s", "--source", help="Filter cross-references by source")
    
    args = parser.parse_args()

    if args.help or not args.command_or_ref:
        CLIHelp().print_usage()
        return

    first_arg = args.command_or_ref
    
    if first_arg == "search":
        print("done.")
        return
    
    if first_arg == "list":
        try:
            A = use("CenterBLC/N1904", version="1.0.0", silent=True)
        except Exception as e:
            print(f"Error loading N1904: {e}")
            sys.exit(1)
        
        handle_list(A, args.args)
        return

    # Load TF
    try:
        with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
            A = use("CenterBLC/N1904", version="1.0.0", silent=True)
    except Exception as e:
        print(f"Error loading N1904: {e}")
        sys.exit(1)

    show_english = False
    show_greek = True
    show_french = True
    
    if args.tr:
        if "en" in args.tr: show_english = True
        if "fr" in args.tr: show_greek = False; show_french = True
        if "gr" in args.tr: show_greek = True; show_french = False

    cross_refs = None
    show_crossref = args.crossref or args.crossref_full
    if show_crossref:
        book_key = first_arg.split()[0]
        if book_key in ["1", "2", "3", "I", "II", "III"]:
             parts = first_arg.split()
             if len(parts) > 1:
                 book_key = f"{parts[0]} {parts[1]}"
        
        resolved = normalizer.abbreviations.get(book_key, book_key)
        book_code = normalizer.n1904_to_code.get(resolved) or normalizer.n1904_to_code.get(resolved.replace(" ", "_"))
        
        ref_db.load_all(source_filter=args.source)
        # Pass the full DB? No, handle_reference expects a filtered subset or the full dict?
        # get_references returns the subset for the book to optimize lookup if needed, 
        # or we can pass ref_db.in_memory_refs directly.
        # Originally load_cross_references returned a dict. 
        # ref_db.in_memory_refs is that dict.
        cross_refs = ref_db.in_memory_refs

    handle_reference(A, first_arg, show_english, show_greek, show_french, show_crossref, cross_refs, args.crossref_full)

if __name__ == "__main__":
    main()
