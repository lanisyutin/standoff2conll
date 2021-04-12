#!/usr/bin/env python
import json
import sys
import os
import codecs

from logging import error

from document import Document
from tagsequence import TAGSETS, DEFAULT_TAGSET
from standoff import DISCONT_RULES, OVERLAP_RULES
from common import TOKENIZATION_REGEXS

import pandas as pd 

def argparser():
    import argparse
    ap = argparse.ArgumentParser(description='Convert standoff to CoNLL format',
                                 usage='%(prog)s [OPTIONS] DIRS/FILES')
    ap.add_argument('-1', '--singletype', default=None, metavar='TYPE',
                    help='replace all annotation types with TYPE')
    ap.add_argument('-a', '--asciify', default=None, action='store_true',
                    help='map input to ASCII')
    ap.add_argument('-c', '--char-offsets', default=False, action='store_true',
                    help='include character offsets')
    ap.add_argument('-n', '--no-sentence-split', default=False,
                    action='store_true',
                    help='do not perform sentence splitting')
    ap.add_argument('-d', '--discont-rule', choices=DISCONT_RULES,
                    default=DISCONT_RULES[0],
                    help='rule to apply to resolve discontinuous annotations')
    ap.add_argument('-i', '--include-docid', default=False, action='store_true',
                    help='include document IDs')
    ap.add_argument('-k', '--tokenization', choices=list(TOKENIZATION_REGEXS.keys()),
                    default=list(TOKENIZATION_REGEXS.keys())[0], help='tokenization')
    ap.add_argument('-o', '--overlap-rule', choices=OVERLAP_RULES,
                    default=OVERLAP_RULES[0],
                    help='rule to apply to resolve overlapping annotations')
    ap.add_argument('-s', '--tagset', choices=TAGSETS, default=None,
                    help='tagset (default %s)' % DEFAULT_TAGSET)
    ap.add_argument('-t', '--types', metavar='TYPE', nargs='*',
                    help='filter annotations to given types')
    ap.add_argument('-x', '--exclude', metavar='TYPE', nargs='*',
                    help='exclude annotations of given types')
    ap.add_argument('data', metavar='DIRS/FILES', nargs='+')
    return ap

def is_standoff_file(fn):
    return os.path.splitext(fn)[1] in ('.ann', '.a1')

def txt_for_ann(filename):
    return os.path.splitext(filename)[0]+'.txt'

def document_id(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def read_ann(filename, options, encoding='utf-8'):
    txtfilename = txt_for_ann(filename)
    with codecs.open(txtfilename, 'rU', encoding=encoding) as t_in:
        with codecs.open(filename, 'rU', encoding=encoding) as a_in:
            return Document.from_standoff_to_spert(
                t_in.read(), a_in.read(),
                sentence_split = not options.no_sentence_split,
                discont_rule = options.discont_rule,
                overlap_rule = options.overlap_rule,
                filter_types = options.types,
                exclude_types = options.exclude,
                tokenization_re = TOKENIZATION_REGEXS.get(options.tokenization),
                document_id = document_id(filename)
            )

def convert_directory(directory, options):
    files = [n for n in os.listdir(directory) if is_standoff_file(n)]
    files = [os.path.join(directory, fn) for fn in files]

    if not files:
        error('No standoff files in {}'.format(directory))
        return

    converted_files = convert_files(files, options)

    return converted_files

def convert_files(files, options):
    errors = []
    converted_files = []
    for fn in sorted(files):
        try:
            converted_files.extend(read_ann(fn, options))
        except Exception as e:
            errors.append((fn.split('\\')[-1], e.args[0]))
    
    if errors:
        import time
        with open(f"errors_log_{time.time()}.txt", 'w', encoding='utf-8') as f:
            f.write("\n".join([file + ": " + text for file, text in errors]))

    return converted_files

def get_relations_count(filepath):
    import json
    from collections import defaultdict

    corpus = json.load(open(filepath, 'r'))
    counter = defaultdict(int)
    
    for sentence in corpus:
        for relation in sentence['relations']:
            counter[relation['type']] += 1

    return counter

def get_stats(filepath):
    res = get_relations_count(filepath)
    df = pd.DataFrame(res.values(), index=res)
    df.sort_values(0,ascending=False, inplace=True)
    
    return df

def main(argv):
    files = []
    args = argparser().parse_args(argv[1:])
    
    for path in args.data:
        files = []
        if os.path.isdir(path):
            files.extend(convert_directory(path, args))

        filepath = os.path.join(path,'nerel_all.json')
        json.dump(files, open(filepath, 'w', encoding='utf-8'))

        stats = get_stats(filepath)
        stats.to_csv(os.path.join(path,'nerel_stats.csv'))
        print(stats)
        print(stats.shape)


    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
