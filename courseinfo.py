#!/usr/bin/env python

#-----------------------------------------------------------------------
# courseinfo.py
# Author: Elise Kratzer, Ernest McCarter
#-----------------------------------------------------------------------

import sys
import contextlib
import sqlite3
import textwrap

#-----------------------------------------------------------------------
DATABASE_URL = 'file:reg.sqlite?mode=rw'

def format_input_params(arg):
    # add escape characters for wild cards
    parameter = str(arg).replace('\\', '\\\\')
    parameter = parameter.replace('_', '\_')
    parameter = parameter.replace('%', '\%')
    # add wild cards for string search
    return '%' + parameter + '%'

# generates the query and params conditionally based
# on which parameters in args are present
def generate_query_and_params(args):
    # build query
    query_string = "SELECT " \
        "classes.classid, " \
        "crosslistings.dept, " \
        "crosslistings.coursenum, " \
        "courses.area, courses.title "
    query_string += "FROM classes, crosslistings, courses "
    conditionals = " WHERE crosslistings.courseid = classes.courseid" \
        " AND courses.courseid = classes.courseid"
    params = []
    # add condtionals to query string and format input parameters
    if args["dept"] is not None:
        conditionals += " AND crosslistings.dept LIKE ? ESCAPE '\\'"
        params.append(format_input_params(args["dept"]))
    if args["coursenum"] is not None:
        conditionals += " AND crosslistings.coursenum " \
            "LIKE ? ESCAPE '\\'"
        params.append(format_input_params(args["coursenum"]))

    if args["area"] is not None:
        conditionals += " AND courses.area LIKE ? ESCAPE '\\'"
        params.append(format_input_params(args["area"]))

    if args["title"] is not None:
        conditionals += " AND courses.title LIKE ? ESCAPE '\\'"
        params.append(format_input_params(args["title"]))
    # add conditionals
    query_string += conditionals
    # order list
    query_string += " ORDER BY crosslistings.dept ASC, " \
        "crosslistings.coursenum ASC, " \
        "classes.classid ASC;"

    return (query_string, params)

def run_info_query(args):
    # execute database queries
    try:
        with sqlite3.connect(
            DATABASE_URL, isolation_level=None, uri=True
            ) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                # generate query
                query_string, params = generate_query_and_params(args)

                # execute query
                cursor.execute(query_string, params)

                # return coures info
                classes = cursor.fetchall()
                return [True, classes]

    except Exception as ex:
        print(ex, file=sys.stderr)
        return [False, ex]



def print_query_result(classes):
    for value in classes:
        print(textwrap.fill("%5d %4s %6s %4s %s" % value,
        width=72,
        break_long_words=False,
        subsequent_indent='                       '))
