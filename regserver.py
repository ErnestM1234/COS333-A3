#!/usr/bin/env python

#-----------------------------------------------------------------------

# regserver.py
# Author: Ernest McCarter, Elise Kratzer

#-----------------------------------------------------------------------

import argparse
import pickle
import socket
import sys
import os
from courseinfo import run_info_query
from coursedetails import run_detailed_query


#-----------------------------------------------------------------------

def handle_client(sock):

    # read
    in_flow = sock.makefile(mode = 'rb')
    query = pickle.load(in_flow)
    # add input error handling here??
    result = database_call(query)

     # write back to the client (reg.py)
    out_flow = sock.makefile(mode='wb')
    pickle.dump(result, out_flow)
    out_flow.flush()


def database_call(query):
    # check what kind of query this is
    if "dept" in query.keys() and "coursenum" in query.keys() \
        and "area" in query.keys() \
        and "title" in query.keys():
        print("Received command: get_detail")
        # call course info
        course_infos = [True, []]
        try:
            raw_courses = run_info_query(query)
            if not raw_courses[0]:
                return raw_courses

            for course in raw_courses[1]:
                course_infos[1].append({
                    "classid": int(course[0]),
                    "dept": course[1],
                    "coursenum": course[2],
                    "area": course[3],
                    "title": course[4],
                })
        except Exception:
            return [False, "database error"]

        return course_infos

    if "classid" in query.keys():
        # call course details
        print("Received command: get_overviews")
        result = run_detailed_query(query["classid"])

        if result[0] is False:
            print(result[1], file=sys.stderr)
            msg = "A server error occured." \
                " Please contact the system administrator."
            if "no class with classid" in str(result[1]):
                msg = result[1]
            return [False, msg]

        return [True, result[1]]


    print("Supplied Argument Error: Invalid Parameters",
        file=sys.stderr)
    return [False, "Supplied Argument Error: Invalid Parameters"]



def main():
    # add in custom arguments
    parser = argparse.ArgumentParser(
        description='Server for the registrar application')
    parser.add_argument('port', metavar='port', type=int,
       help='the port at which the server should listen')
    args = parser.parse_args()

    try:
        server_sock = socket.socket()
        print('Opened server socket')
        if os.name != 'nt':
            server_sock.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('', args.port))
        print('Bound server socket to port')
        server_sock.listen()
        print('Listening')

        # our server loops infinitely:
        while True:
            try:
                sock, _ = server_sock.accept() # should be transient

                with sock:
                    print('Accepted connection, opened socket.socket')

                    # read from client
                    handle_client(sock)

                    sock.close()

                    print("Closed socket.socket")

            except Exception as ex:
                print(ex, file=sys.stderr)


    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------
if __name__ == '__main__':
    main()
