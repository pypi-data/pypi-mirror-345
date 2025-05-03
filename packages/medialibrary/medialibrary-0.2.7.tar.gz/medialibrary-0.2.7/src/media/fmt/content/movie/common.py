#!/usr/bin/env python

#
# Copyright 2024 Chris Josephes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

'''
Functions that are common to output operations tied to movie data.
'''

from datetime import timedelta


def build_genre_simple(in_movie):
    '''
    Build a string for all genres.
    '''
    o_string = ''
    classification = in_movie.classification
    if classification.genres:
        if classification.genres.primary:
            o_string = f"{classification.genres.primary}"
        if classification.genres.secondary:
            o_string += '/' + '/'.join(classification.genres.secondary)
    return o_string


def build_genre_classification(in_movie):
    '''
    Build a text classification string.
    '''
    o_string = ""
    classification = in_movie.classification
    if classification.category:
        o_string = "[" + str(classification.category) + "]"
    o_string += " " + build_genre_simple(in_movie)
    if classification.genres.specific:
        class_s = classification.genres.specific.strip()
        if class_s:
            o_string += f" \"{class_s}\""
    return o_string


def build_subgenre_classifications(in_movie):
    '''
    Build the subgenre list.
    '''
    subgenre_s = ", ".join(sorted(in_movie.classification.genres.subgenres))
    if subgenre_s:
        return f"({subgenre_s})\n"
    return ""


def build_copyright_year(in_movie):
    '''
    Construct a printable version of the copyright year.
    '''
    year_s = "0000"
    if in_movie.catalog:
        if in_movie.catalog.copyright:
            year_s = f"{in_movie.catalog.copyright.year:4d}"
    return year_s


def build_runtime(in_movie):
    '''
    Construct a presentable version of the runtime value.
    '''
    runtime = timedelta(seconds=0)
    if in_movie.technical:
        if in_movie.technical.runtime:
            runtime = in_movie.technical.runtime.overall
    return f"{runtime!s}"
