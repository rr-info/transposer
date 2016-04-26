Transposer [![Build Status](https://travis-ci.org/davidparsson/transposer.svg?branch=master)](https://travis-ci.org/davidparsson/transposer)
==========
Modified: http://shaharr.info, 2016


Transposing chords from one key to another

Usage
-----

To transpose chords, use transposer like this:

    python transposer.py --from=F# --to=Eb input.txt
    python transposer.py --from=F# --to=Eb [-p] [-v] input.txt

Input files
-----------

The input file should be a plain text file (UTF-8 compatible).
The default version doesn't require additional formatting:
 - Chords must be separated *somehow* (e.g. space, words, characters).
 - Root notes must be in upper case,
 - "m" (minor) / "b" (flat) must be in lower case

Todo / Notes:
-------------
 
 - supported chord styles & symbols:  #, b, m, digits, +, /
   - e.g. Bb76, G#7+/F#, Dm
 - long symbols (maj, maj7, sus4) are NOT yet supported
 - special unicode musical characters not yet supported: sharp (♯, 266F) and flat (bemol)

 
Examples
--------
The contents of `example.txt`:

    Rocking start, jazzy ending
    | D | G A | Bbm7#11/Db |
    <p><b>E</b>&nbsp;<b>D</b>&nbsp;<b>C</b>&nbsp;<b>A67</b>&nbsp;A4<b>
    
`transposer --from=D --to=E example.txt` prints:

    Rocking start, jazzy ending
    | E | A B | Cm7#11/D# |
    <p><b>D</b>&nbsp;<b>C</b>&nbsp;<b>A#</b>&nbsp;<b>G67</b>&nbsp;G4<b>


Testing
-------

Run unit tests using Python's doctest:

    python -m doctest -v transposer.py
    (well, that might not work anymore after my upgrade (Apr 2016)
    
