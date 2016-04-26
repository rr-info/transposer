#!/usr/bin/python
# encoding: utf-8
"""
transposer.py

See README.md for information.

Created by David Pärsson on 2011-08-13:
    Excessively doctested due to education.

Modified by Shaharr, 2016-04-26:
    + supports "any" text format!
    + core chord find and replace using regex
    + supports more chord types:  Xm7, X#4, X76, and more.
    - previous version assumed specific line formatting -- not required
    - no recursion is used anymore
    + usage, commets to STDERR, spacing, and misc


"""

import sys
import os
import re, getopt

key_list = [('A',), ('A#', 'Bb'), ('B',), ('C',), ('C#', 'Db'), ('D',),
            ('D#', 'Eb'), ('E',), ('F',), ('F#', 'Gb'), ('G',), ('G#', 'Ab')]

sharp_flat = ['#', 'b']
sharp_flat_preferences = {
    'A' : '#',
    'A#': 'b',
    'Bb': 'b',
    'B' : '#',
    'C' : 'b',
    'C#': 'b',
    'Db': 'b',
    'D' : '#',
    'D#': 'b',
    'Eb': 'b',
    'E' : '#',
    'F' : 'b',
    'F#': '#',
    'Gb': '#',
    'G' : '#',
    'G#': 'b',
    'Ab': 'b',
    }

key_regex  = re.compile(r"[ABCDEFG][#b]?")
key_regex2 = re.compile(r"(^|\W)([ABCDEFG][#b]*[m2467+]*)(\W|$)")
verbose = False


def log(*items):
    if not verbose:
        return
    things = []
    for s in items:
        if type(s) in [int, float, long]:
            s = unicode(s)
        if type(s) is unicode:
            s=s.replace(u'\n', u'\\n')
            s=s.replace(u'\r', u'\\r')
            s.encode('utf-8')
        elif type(s) in [str, ]:
            s=s.replace('\n', '\\n')
            s=s.replace('\r', '\\r')
        else:
            s = s.__repr__()
        things.append(s)

    line = '\t'.join(things) + '\n'
    try:
        sys.stderr.write(line)
    except UnicodeEncodeError:
        sys.stderr.write('(gibberish)\n')



def get_index_from_key(source_key):
    """Gets the internal index of a key
    >>> get_index_from_key('Bb')
    1
    """
    for key_names in key_list:
        if source_key in key_names:
            return key_list.index(key_names)
    raise Exception("Invalid key: %s" % source_key)


def get_key_from_index(index, to_key):
    """Gets the key at the given internal index.
    Sharp or flat depends on the target key.
    >>> get_key_from_index(1, 'Eb')
    'Bb'
    """
    key_names = key_list[index % len(key_list)]
    if len(key_names) > 1:
        sharp_or_flat = sharp_flat.index(sharp_flat_preferences[to_key])
        return key_names[sharp_or_flat]
    return key_names[0]


def get_transponation_steps(source_key, target_key):
    """Gets the number of half tones to transpose
    >>> get_transponation_steps('D', 'C')
    -2
    """
    source_index = get_index_from_key(source_key)
    target_index = get_index_from_key(target_key)
    return target_index - source_index


def transpose_file(file_name, from_key, to_key):
    """Transposes a file from a key to another.
    >>> transpose_file('example.txt', 'D', 'E')
    'Rocking start, jazzy ending\\n| E | A B | Cm7#11/D# |\\n'
    """
    direction = get_transponation_steps(from_key, to_key)
    result = ''
    try:
        for line in open(file_name):
            #line = line.rstrip()
            result += transpose_line(line, direction, to_key)
        return result
    except IOError:
        log("Invalid filename!")
        usage()


def transpose_line_plain(source_line, direction, to_key):
    """Transposes a line a number of keys if it starts with a pipe. Examples:
    >>> transpose_line_plain('| A | A# | Bb | C#m7/F# |', -2, 'C')
    '| G | Ab | Ab | Bm7/E |'

    Different keys will be sharp or flat depending on target key.
    >>> transpose_line_plain('| A | A# | Bb | C#m7/F# |', -2, 'D')
    '| G | G# | G# | Bm7/E |'

    It will use the more common key if sharp/flat, for example F# instead of Gb.
    >>> transpose_line_plain('| Gb |', 0, 'Gb')
    '| F# |'

    Lines not starting with pipe will not be transposed
    >>> transpose_line_plain('A | Bb |', -2, 'C')
    'A | Bb |'
    """
    if source_line[0] != '|':
        return source_line
    source_chords = key_regex.findall(source_line)
    return recursive_line_transpose(source_line, source_chords, direction, to_key)


def transpose_line(source_line, direction, to_key):
    """
    Transposes ANY line a number of keys.
    Find and replace with regular expressions & groups (re.sub with callback)
    Base note is regarded as an independant chord.
    No recursion needed :)
    Lines not starting with pipe WILL be transposed (as opposed to other methods)
    chords must be at least separated by space
    chords are matched ANYWHERE on the line.

    Examples:

    >>> transpose_line('| A | A# | Bb | C#m7/F# |', -2, 'C')
    '| G | G# | G# | Bm7/F# |'

    >>> transpose_line(x, -2, 'D')
    'Am<p><b>E</b>&nbsp;<b>D</b>&nbsp;<b>C</b>&nbsp;<b>A</b>&nbsp;<b>G</b>&nbsp;<b>C</b>&nbsp;<b>D</b>&nbsp;<b>G</b>&nbsp;<b>Em</b></p>B67'
    'Gm<p><b>D</b>&nbsp;<b>C</b>&nbsp;<b>A#</b>&nbsp;<b>G</b>&nbsp;<b>F</b>&nbsp;<b>A#</b>&nbsp;<b>C</b>&nbsp;<b>F</b>&nbsp;<b>Dm</b></p>A67'

    It will use the more common key if sharp/flat, for example F# instead of Gb.
    >>> transpose_line('| Gb |', 0, 'Gb')
    '| F# |'

    """

    def replace(match):
        groups = match.groups()
        log(groups)
        if not groups:
            return None
        chord = groups[1]
        pre = groups[0]
        post = groups[2]
        base = key_regex.findall(chord)[0]
        new_chord = transpose(base, direction, to_key)
        chord = chord.replace(base, new_chord)
        return pre+chord+post

    log(source_line)
    target_line = key_regex2.sub(replace, source_line)
    return target_line


def recursive_line_transpose(source_line, source_chords, direction, to_key):
    """ after 2016 update, it's obsolete,
    and required only for the --plain version """

    if not source_chords or not source_line:
        return source_line
    source_chord = source_chords.pop(0)
    chord_index = source_line.find(source_chord)
    after_chord_index = chord_index + len(source_chord)

    return source_line[:chord_index] + \
           transpose(source_chord, direction, to_key) + \
           recursive_line_transpose(source_line[after_chord_index:], source_chords, direction, to_key)


def transpose(source_chord, direction, to_key):
    """Transposes a chord a number of half tones.
    Sharp or flat depends on target key.
    >>> transpose('C', 3, 'Bb')
    'Eb'
    """
    source_index = get_index_from_key(source_chord)
    return get_key_from_index(source_index + direction, to_key)


def usage():
    print '''Usage:
    %s [--regex] --from=Eb --to=F# <filename>
    Where:
        -f --from=    original scale/chord
        -t --to=      eventual scale/chord
        -p --plain    do NOT the advanced regex replacement
        -v --verbose  show debug messages (STDERR)
        ''' % os.path.basename(__file__)
    sys.exit(2)


def main():
    from_key = 'C'
    to_key = 'C'
    file_name = None
    regex = False
    global transpose_line, verbose

    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'vpf:t:', ['verbose', 'plain', 'from=', 'to=', 'doctest'])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    for option, value in options:
        if option in ('-f', '--from'):
            from_key = value
        elif option in ('-t', '--to'):
            to_key = value
        elif option in ('-v', '--verbose'):
            verbose = True
        elif option in ('-p', '--plain'):
            regex = False
            transpose_line = transpose_line_plain
        elif option == '--doctest':
            import doctest
            doctest.testmod()
            exit()
        else:
            usage()

    if arguments:
        file_name = arguments[0]
    else:
        usage()

    result = transpose_file(file_name, from_key, to_key)

    log("Result (%s -> %s):" % (from_key, to_key))
    print(result)


if __name__ == '__main__':
    main()
