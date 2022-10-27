#-----------------------------------------------------------------------
# runserver.py
# authors: Ernest McCarter and Elise Kratzer
#-----------------------------------------------------------------------
import argparse
from re import T
import sys
from flask import Flask
from courseinfo import run_info_query
from coursedetails import run_detailed_query
from flask import request

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

    return get_courses(dept,coursenum,area,title)


@app.route('/regdetails')
def regdetails():
    classid = request.args.get('classid')
    return get_details(classid)


#-----------------------------------------------------------------------
if __name__ == '__main__':
    main()
