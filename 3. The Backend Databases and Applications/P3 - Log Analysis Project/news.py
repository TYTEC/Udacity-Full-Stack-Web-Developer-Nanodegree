#!/usr/bin/env python3

# This Log Analysis project is a part of Udacity Full Stack Nanodegree 

# Import modules
import psycopg2


def connect(database_name="news"):
    # Connect to the news database
    try:
        # connect to the database
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    # If not possible to connect to the database 
    except:
        print ("It is not possible to connect to the database!")


def get_query_results(query):
    # # connect to the database
    db, cursor = connect()
    cursor.execute(query)
    # Return result of the query
    return cursor.fetchall()
    # Close database
    db.close()


question1 = ("What are the most popular three articles of all time?")

query1 = """SELECT title,count(*) AS num FROM articles,log 
             WHERE log.path=CONCAT('/article/',articles.slug) AND log.status like '%200%'
             GROUP BY articles.title 
             ORDER BY num DESC LIMIT 3;"""

question2 = ("Who are the most popular article authors of all time?")


query2 = """SELECT authors.name, count(*) as views FROM articles inner 
             JOIN authors on articles.author = authors.id inner 
             JOIN log on log.path LIKE concat('%', articles.slug, '%')
             WHERE log.status LIKE '%200%'
             GROUP BY authors.name
             ORDER BY views DESC;"""


question3 = ("On which days did more than 1% of requests lead to errors?")

query_3 = """SELECT * FROM (SELECT date(time),round(100.0*sum(CASE log.status
            WHEN '200 OK'  THEN 0 ELSE 1 END)/count(log.status),3)
            AS error FROM log 
            GROUP BY date(time) 
            ORDER BY error DESC) AS subquery 
            WHERE error > 1;"""