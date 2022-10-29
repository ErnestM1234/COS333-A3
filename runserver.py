#-----------------------------------------------------------------------
# runserver.py
# authors: Ernest McCarter and Elise Kratzer
#-----------------------------------------------------------------------
import argparse
from email.policy import strict
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
        return [False, "database error"]
    return [True, output]

def get_details(classid):
    try:
        result = run_detailed_query(classid)
    except Exception:
        return [False, "database error"]

    return result

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

    courses = get_courses(dept,coursenum,area,title)
    if not courses[0]:
        print(str(courses[1]), file=sys.stderr)
        return render_template(
            "error.html",
            ErrorMessage="A server error occured." \
            " Please contact the system administrator."
        )

    response = flask.make_response(render_template(
        'search.html',
        Courses=courses[1],
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
    if classid is None:
        return render_template(
            "error.html",
            ErrorMessage="missing classid"
        )

    if not classid.isnumeric():
        return render_template(
            "error.html",
            ErrorMessage="non-integer classid"
        )

    # added the below
    result = get_details(classid)

    if result is None:
        return render_template(
            "error.html",
            ErrorMessage="A server error occured." \
            " Please contact the system administrator."
        )

    if result[0] is False:
        if 'no class with classid' not in str(result[1]):
            print(str(result[1]), file=sys.stderr)
            result[1] = "A server error occured." \
            " Please contact the system administrator."
        return render_template(
            "error.html",
            ErrorMessage=result[1]
        )

    details = result[1]

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
