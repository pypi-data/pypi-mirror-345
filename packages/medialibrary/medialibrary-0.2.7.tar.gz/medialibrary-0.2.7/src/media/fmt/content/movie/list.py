#!/usr/bin/env python

#
# Copyright 2025 Chris Josephes
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
Code for generating a list of movies in a table structure.
'''

# pylint:disable=too-many-instance-attributes, R0801

from media.fmt.formatter.selector import Selector
from media.fmt.structure.table import (Table, TableColumnSpec,
                                       TableHeaderColumnSpec)
from media.general.sorting.batch import Batch
from media.general.sorting.organizer import Organizer
from media.fmt.content.movie.common import (build_copyright_year,
                                            build_genre_classification,
                                            build_runtime)


class MovieListTable():
    '''
    A list of movie content objects, showing the
    title, year, runtime, and genre information.
    '''
    def __init__(self):
        # self.formatter = in_formatter_name
        self.table = Table()
        self.table_fmt = None
        self.organizer = None
        self.movies = []
        self.sample = 0
        self.group = Organizer.G_ANY_ALPHA
        self.asort = Batch.S_TITLE
        self._setup_table()

    def _setup_table(self):
        '''
        Set up the table structure.
        '''
        # self.table_fmt = Selector.load_formatter(self.formatter).get_table()
        self.table.set_columns(
                TableColumnSpec('Title', 40),
                TableColumnSpec('Year', 4),
                TableColumnSpec('Runtime', 8),
                TableColumnSpec('Genre', 40)
                )
        self.table.set_classes('contentTable')

    def set_movies(self, in_movies):
        '''
        Pass all the movie content objects
        that were found in the repository.
        '''
        if len(in_movies) > 0:
            self.movies = in_movies
            self.organizer = Organizer(in_movies)

    def params_from_controller(self, in_controller):
        '''
        Get the parameter values from the controller object.
        '''
        self.group = in_controller.group
        self.asort = in_controller.sort
        if in_controller.args.random:
            self.sample = in_controller.args.random

    def build(self, in_grouping=None,
              in_sorting=None, in_sample=0):
        '''
        Populate the table with entries by having the
        Organizer object create a series of batches.

        We can build the table using parameters
        that are set from a Controller object,
        or we can take parameters that are passed
        as method arguments.
        '''
        batches = []
        if in_grouping:
            self.group = in_grouping
        if in_sorting:
            self.asort = in_sorting
        if self.sample == 0:
            self.sample = max(in_sample, 0)
        # Parameters are set, now build the batches
        if self.sample > 0:
            batches = self.organizer.create_batches(self.group, self.sample)
        else:
            batches = self.organizer.create_batches(self.group)
        # If we have batches, build the table rows
        if batches:
            self._import_batches(batches, self.asort)

    # NOTE:
    # Titles and the field spec (length, justification, etc)
    # Should be in separate data structures, since the titles
    # will be easy, but the formatting will be tricky.
    #
    # What we have been calling lists, should really just be
    # considered tables.

    # Flow
    #
    # If there's only one batch, it doesn't need a subheader
    # If there's more than one, then we need subheaders

    def _import_batches(self, in_batches, in_sort):
        '''
        Add batches to the table.
        '''
        if len(in_batches) == 1:
            self.table.add_body()
            self._add_batch(in_batches[0], in_sort)
        else:
            for btch in sorted(in_batches):
                self.table.add_body(btch.header)
                self._add_batch(btch, in_sort)

    def _add_batch(self, in_batch, in_sort_field=Batch.S_TITLE):
        '''
        Add entries from a single batch into the table,
        respecting the sort order.
        '''
        order_list = in_batch.index_by(in_sort_field)
        for movie in order_list:
            self._add_row_entry(movie.movie)

    def _add_row_entry(self, movie):
        '''
        Add a single entry to the table, formatting
        all the data.
        '''
        # output the single entry
        y_string = build_copyright_year(movie)
        runtime = build_runtime(movie)
        category = build_genre_classification(movie)
        self.table.add_row(str(movie.title), y_string, runtime, category)

    # Maybe.....
    # Do the formatting render stuff here, instead of keeping it as
    # instance variables
    def get_output(self, formatter):
        '''
        Return the formatted table.
        '''
        # return self.table_fmt.render(self.table)
        return formatter.render(self.table)

    def build_stat_table(self):
        '''
        Generate a table of statistics.
        '''
        total = len(self.organizer.entries)
        stat_table = MovieStatTable(total, self.sample)
        return stat_table


class MovieListTable3():
    '''
    A list of movie content objects, showing the
    title, year, runtime, and genre information.
    '''
    def __init__(self, in_formatter_name=None):
        self.output = ''
        self.formatter = in_formatter_name
        self.table = None
        self.table_fmt = None
        self.organizer = None
        self.sample = 0
        self._setup_table()

    def _setup_table(self):
        '''
        Set up the table structure.
        '''
        # self.table_fmt = Selector.load_formatter(self.formatter).get_table()
        self.table = Table()
        self.table.set_columns(
                TableColumnSpec('Title', 40),
                TableColumnSpec('Year', 4),
                TableColumnSpec('Runtime', 8),
                TableColumnSpec('Genre', 40)
                )

        self.table.set_classes('contentTable')
        # self.table.start()

    def set_organizer(self, in_organizer=None):
        '''
        Set the organizer object.
        '''
        self.organizer = in_organizer

    def populate(self, in_grouping=Organizer.G_ANY_GENRE,
                 in_sorting=Batch.S_TITLE, sample_size=0):
        '''
        Populate the table with entries by having the
        Organizer object create a series of batches.
        '''
        batches = []
        if sample_size > 0:
            batches = self.organizer.create_batches(in_grouping, sample_size)
            self.sample = sample_size
        else:
            batches = self.organizer.create_batches(in_grouping)
        if batches:
            self._batch_import(batches, in_sorting)

#     def build_batches(self, grouping, sample_size=0):
#         '''
#         Build the batches of data based on passed parameters.
#         '''
#         batches = []
#         if sample_size > 0:
#             batches = self.organizer.create_batches(grouping, sample_size)
#         else:
#             batches = self.organizer.create_batches(grouping)
#         if batches:
#             # do the batch stuff
#             self.batch_loop(batches)
#         else:
#             pass
#             # we hit some error here

    # NOTE:
    # Titles and the field spec (length, justification, etc)
    # Should be in separate data structures, since the titles
    # will be easy, but the formatting will be tricky.
    #
    # What we have been calling lists, should really just be
    # considered tables.

    # Flow
    #
    # If there's only one batch, it doesn't need a subheader
    # If there's more than one, then we need subheaders

#     def batch_loop(self, in_batches):
#         '''
#         Main table body building loop.
#         '''
#         if len(in_batches) == 1:
#             self.table.add_body()
#         else:
#             for btch in sorted(in_batches):
#                 self.table.add_body(btch.header)
#                 self.batch(btch)

    def _batch_import(self, in_batches, in_sort):
        if len(in_batches) == 1:
            self.table.add_body()
            self._in_batch(in_batches[0], in_sort)
        else:
            for btch in sorted(in_batches):
                self.table.add_body(btch.header)
                # self.batch(btch)
                self._in_batch(btch, in_sort)

#     def batch(self, in_batch, sort_field=Batch.S_TITLE):   # WTF is '1' ??
#         '''
#         Output a movie batch. one entry at a time.
#         '''
#         order_list = in_batch.index_by(sort_field)
#         for movie in order_list:
#             self._entry(movie.movie)

    def _in_batch(self, in_batch, in_sort_field=Batch.S_TITLE):
        order_list = in_batch.index_by(in_sort_field)
        for movie in order_list:
            self._entry(movie.movie)

    def _entry(self, movie):
        # output the single entry
        y_string = build_copyright_year(movie)
        runtime = build_runtime(movie)
        category = build_genre_classification(movie)
        self.table.add_row(str(movie.title), y_string, runtime, category)

    # Maybe.....
    # Do the formatting render stuff here, instead of keeping it as
    # instance variables
    def get_output(self, formatter):
        '''
        Return the formatted table.
        '''
        # return self.table_fmt.render(self.table)
        return formatter.render(self.table)

    def build_stat_table(self):
        '''
        Generate a table of statistics.
        '''
        total = len(self.organizer.entries)
        stat_table = MovieStatTable(total, self.sample)
        return stat_table


class MovieListTable2():
    '''
    A list of movie content objects, showing the
    title, year, runtime, and genre information.
    '''
    def __init__(self):
        self.output = ''
        self.driver = None
        self.table = None
        self.table_fmt = None

    def setup(self, in_driver):
        '''
        Set up the table structure.
        '''
        self.table_fmt = Selector.load_formatter(in_driver).get_table()
        self.table = Table()
        # self.table.add_column(TableColumnSpec('Title', 40))
        # self.table.add_column(TableColumnSpec('Year', 4))
        # self.table.add_column(TableColumnSpec('Runtime', 8))
        # self.table.add_column(TableColumnSpec('Genre', 40))
        self.table.set_columns(
                TableColumnSpec('Title', 40),
                TableColumnSpec('Year', 4),
                TableColumnSpec('Runtime', 8),
                TableColumnSpec('Genre', 40)
                )

        self.table.set_classes('contentTable')
        # self.table.start()

    # NOTE:
    # Titles and the field spec (length, justification, etc)
    # Should be in separate data structures, since the titles
    # will be easy, but the formatting will be tricky.
    #
    # What we have been calling lists, should really just be
    # considered tables.

    # Flow
    #
    # If there's only one batch, it doesn't need a subheader
    # If there's more than one, then we need subheaders

    def batch_loop(self, in_batches):
        '''
        Main table body building loop.
        '''
        if len(in_batches) == 1:
            self.table.add_body()
        else:
            for btch in sorted(in_batches):
                self.table.add_body(btch.header)
                self.batch(btch)

    def batch(self, in_batch, sort_field=Batch.S_TITLE):   # WTF is '1' ??
        '''
        Output a movie batch. one entry at a time.
        '''
        order_list = in_batch.index_by(sort_field)
        for movie in order_list:
            self._entry(movie.movie)

    def _entry(self, movie):
        # output the single entry
        y_string = build_copyright_year(movie)
        runtime = build_runtime(movie)
        category = build_genre_classification(movie)
        self.table.add_row(str(movie.title), y_string, runtime, category)

    def get_output(self):
        '''
        Return the formatted table.
        '''
        return self.table_fmt.render(self.table)


class MovieStatTable():
    '''
    Table to report the list stats.
    '''
    def __init__(self, in_total, in_sample=0):
        self.table = None
        self.table_fmt = None
        self.total = in_total
        self.sample = 0
        if in_sample != 0:
            self.sample = in_sample
        self._setup_table()
        self.report()

    def _setup_table(self):
        '''
        Build the table structure object.
        '''
        # self.table_fmt = Selector.load_formatter(in_driver).get_table()
        self.table = Table()
        c1 = TableHeaderColumnSpec('', 20)
        c2 = TableColumnSpec('Total', 8)
        c3 = TableColumnSpec('Sample', 8)
        # self.table.add_column(TableHeaderColumnSpec('', 20))
        # self.table.add_column(TableColumnSpec('Total', 8))
        if self.sample > 0:
            self.table.set_columns(c1, c2, c3)
        else:
            self.table.set_columns(c1, c2)
        # if self.sample > 0# :
        #    self.table.add_column(TableColumnSpec('Sample', 8))
        self.table.set_classes('statsTable')
        # self.table.start()

    def report(self):
        '''
        Generate the report data for the stat table.
        '''
        total_s = f"{self.total:8d}"
        if self.sample > 0:
            sample_s = f"{self.sample:8d}"
            self.table.add_row('Movies', total_s, sample_s)
        else:
            self.table.add_row('Movies', total_s)
        # self.table.finish()

    def get_output(self):
        '''
        Return the output for the stat table.
        '''
        return self.table_fmt.render(self.table)
