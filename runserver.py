#-----------------------------------------------------------------------
# runserver.py
# authors: Ernest McCarter and Elise Kratzer
#-----------------------------------------------------------------------
import argparse
import os
import sys
from flask import render_template
from flask import Flask
import flask
from flask import request
from courseinfo import run_info_query
from coursedetails import run_detailed_query

#-----------------------------------------------------------------------
app = Flask(__name__)

def get_courses(dept, coursenum, area, title):
    # generate query args:
    query = {
        "dept":dept,
        "coursenum":coursenum,
        "area":area,
        "title":title,
    }
    output = []

    try:
        raw_courses = run_info_query(query)
        if not raw_courses[0]:
            return raw_courses

        for course in raw_courses[1]:
            output.append({
                "classid": int(course[0]),
                "dept": course[1],
                "coursenum": course[2],
                "area": course[3],
                "title": course[4],
            })
    except Exception:
        return ["database error"]
    return output

def get_details(classid):
    try:
        print("Received command: get_overviews")
        result = run_detailed_query(classid)
        if result[0] is False:
            print(result[1], file=sys.stderr)
            if "no class with classid" in str(result[1]):
                return result[1]
            return "A server error occured." \
                " Please contact the system administrator."
    except Exception:
        return "database error"

    return result[1]

def main():
    # add in custom arguments
    parser = argparse.ArgumentParser(
        description='The registrar application'
    )
    parser.add_argument(
        'port',
        metavar='port',
        type=int,
        help='the port at which the server should listen'
    )
    args = parser.parse_args()

    # run app
    app.run(port=args.port)

@app.route('/')
def root():
    dept = request.args.get('dept')
    coursenum = request.args.get('coursenum')
    area = request.args.get('area')
    title = request.args.get('title')

    # make these values empty strings if they are None
    dept = dept if dept is not None else ''
    coursenum = coursenum if coursenum is not None else ''
    area = area if area is not None else ''
    title = title if title is not None else ''

    response = flask.make_response(render_template(
        'search.html',
        Courses=get_courses(dept,coursenum,area,title),
        Dept=dept,
        Coursenum=coursenum,
        Area=area,
        Title=title
    ))

    response.set_cookie('dept', dept)
    response.set_cookie('coursenum', coursenum)
    response.set_cookie('area', area)
    response.set_cookie('title', title)

    return response

@app.route('/regdetails')
def regdetails():
    classid = request.args.get('classid')
    # added the below
    details = get_details(classid)

    # get cookie
    dept = flask.request.cookies.get('dept')
    coursenum = flask.request.cookies.get('coursenum')
    area = flask.request.cookies.get('area')
    title = flask.request.cookies.get('title')


    # make these values empty strings if they are None
    dept = dept if dept is not None else ''
    coursenum = coursenum if coursenum is not None else ''
    area = area if area is not None else ''
    title = title if title is not None else ''

    return render_template(
        'details.html',
        Details=details,
        DeptAndNum=zip(details["dept"],details["coursenum"]),
        Dept=dept,
        Coursenum=coursenum,
        Area=area,
        Title=title
    )


#-----------------------------------------------------------------------
if __name__ == '__main__':
    main()
