#!/usr/bin/env python

#-----------------------------------------------------------------------
# coursedetails.py
# Author: Elise Kratzer, Ernest McCarter
#-----------------------------------------------------------------------

import contextlib
import sqlite3

#-----------------------------------------------------------------------

DATABASE_URL = 'file:reg.sqlite?mode=rw'

def execute_queries(cursor, class_details, class_id):
    # ----- get class information -----
    # generate query string
    query_string = "SELECT " \
        "classes.courseid, " \
        "classes.days, " \
        "classes.starttime, " \
        "classes.endtime, " \
        "classes.bldg, " \
        "classes.roomnum, " \
        "classes.classid "
    query_string += "FROM classes "
    query_string += "WHERE classes.classid=?;"

    # execute query
    cursor.execute(query_string, [class_id])

    # store values
    result = cursor.fetchone()
    # check for no class case
    if result is None:
        class_details['querysuccess'] = False
        return

    class_details['courseid'] = result[0]
    class_details['days'] = result[1]
    class_details['starttime'] = result[2]
    class_details['endtime'] = result[3]
    class_details['bldg'] = result[4]
    class_details['roomnum'] = result[5]
    class_details['classid'] = result[6]

    # ----- get course information -----
    # generate query string
    query_string = "SELECT " \
        "courses.area, " \
        "courses.title, " \
        "courses.descrip, " \
        "courses.prereqs "
    query_string += "FROM classes, courses "
    query_string += "WHERE classes.classid=? "
    query_string += "AND courses.courseid = classes.courseid;"

    # execute query
    cursor.execute(query_string, [class_id])

    # store values
    result = cursor.fetchone()
    class_details['area'] = result[0]
    class_details['title'] = result[1]
    class_details['descrip'] = result[2]
    class_details['prereqs'] = result[3]

    # ----- get prof information -----
    # generate query string
    query_string = "SELECT profs.profname "
    query_string += "FROM classes, coursesprofs, profs "
    query_string += "WHERE classes.classid=? "
    query_string += "AND coursesprofs.courseid = classes.courseid " \
        "AND profs.profid = coursesprofs.profid "
    query_string += "ORDER BY profs.profname ASC;"

    # execute query
    cursor.execute(query_string, [class_id])

    # store values
    result = cursor.fetchall()
    for res in result:
        class_details['profname'].append(res[0])

    # ----- get crosslistings information -----
    query_string = "SELECT " \
        "crosslistings.dept, " \
        "crosslistings.coursenum "
    query_string += "FROM classes, crosslistings "
    query_string += "WHERE classes.classid=? "
    query_string += "AND crosslistings.courseid = classes.courseid "
    query_string += "ORDER BY dept ASC, coursenum ASC;"

    # execute query
    cursor.execute(query_string, [class_id])

    # store values
    result = cursor.fetchall()
    for res in result:
        class_details['dept'].append(res[0])
        class_details['coursenum'].append(res[1])

def run_detailed_query(class_id):
    # execute database queries
    try:
        with sqlite3.connect(
            DATABASE_URL,
            isolation_level=None,
            uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:

                # define a datastructure for holding query results
                class_details = {
                    'profname': [],
                    'dept': [],
                    'coursenum': [],
                    'querysuccess': True,
                }

                # execute queries
                execute_queries(cursor, class_details, class_id)

                if not class_details['querysuccess']:
                    return [False, "no class with classid "
                    + str(class_id)
                    + " exists"]

                return [True, class_details]

    except Exception as ex:
        return [False, ex]
