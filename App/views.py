from flask import render_template, request
from flaskexample import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from a_Model import ModelIt
from gmaps import Geocoding
api = Geocoding()

#import request

user = 'tson' #add your username here (same as previous postgreSQL)            
host = 'localhost'
dbname = 'yelp_db'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

@app.route('/')
@app.route('/DatePlannr')
def index():
    return render_template("dateplannr.html",
       title = 'Home', user = { 'nickname': 'Miguel' },
       )

@app.route('/db')
def birth_page():
    sql_query = """                                                             
                SELECT * FROM birth_data_table WHERE delivery_method='Cesarean'\
;                                                                               
                """
    query_results = pd.read_sql_query(sql_query,con)
    births = ""
    print(query_results[:10])
    for i in range(0,10):
        births += query_results.iloc[i]['birth_month']
        births += "<br>"
    return births

@app.route('/db_fancy')
def cesareans_page_fancy():
    sql_query = """
               SELECT index, attendant, birth_month FROM birth_data_table WHERE delivery_method='Cesarean';
                """
    query_results=pd.read_sql_query(sql_query,con)
    births = []
    for i in range(0,query_results.shape[0]):
        births.append(dict(index=query_results.iloc[i]['index'], attendant=query_results.iloc[i]['attendant'], birth_month=query_results.iloc[i]['birth_month']))
    return render_template('cesareans.html',births=births)

@app.route('/input')
def cesareans_input():
    return render_template("input.html")

@app.route('/output')
def cesareans_output():
		#pull 'address' from input field and store it
		addy = request.args.get('address')
		print addy
		occay = request.args.get('occasion')
		print occay
		numq = request.args.get('nuQuery')
		print numq
		sb = request.args.get('sort_by')
		print sb
		a=api.geocode(addy)
		lat=a[0][u'geometry'][u'location'][u'lat']
		lng=a[0][u'geometry'][u'location'][u'lng']
		#find closest address
		if occay.lower() =="anniversary":
			sel= 'anniversary'
		elif occay.lower() =="birthday":
			sel= 'birthday'
		elif occay.lower() =="celebration":
			sel= 'celebration'
		elif occay.lower() =="date night":
			sel='date_night'
		query = "SELECT * FROM final_table WHERE %s > 0" % sel		
		tdf=pd.read_sql_query(query,con)
		ttdf=tdf[tdf.anniversary>0]
		if occay.lower() =="anniversary":
			ttdf=tdf[tdf.anniversary>0]
		elif occay.lower() =="birthday":
			ttdf=tdf[tdf.birthday>0]
		elif occay.lower() =="celebration":
			ttdf=tdf[tdf.celebration>0]
		elif occay.lower() =="date night":
			ttdf=tdf[tdf.date_night>0]
		ttdf.reset_index(level=0, inplace=True)
		ds=find_dist(lat,lng,ttdf['latitude'],ttdf['longitude'])
		ttdf['ds']=ds
		ds.sort_values(inplace=True)
		plc=ds[:int(numq)]
		plc=plc.index[:]
		plc=plc.values.tolist()
		if sb =="Distance":
			query_results=ttdf.iloc[plc].sort_index(by='ds', ascending=1)
		elif sb =="Ratings (dates)":
			query_results=ttdf.iloc[plc].sort_index(by='stars_y', ascending=0)
		elif sb=="Ratings (others)":
			query_results=ttdf.iloc[plc].sort_index(by='stars_z', ascending=0)
		elif sb =="# Reviews (others)":
			query_results=ttdf.iloc[plc].sort_index(by='review_count', ascending=0)
		elif sb =="# Reviews (dates)":
			query_results=ttdf.iloc[plc].sort_index(by='num', ascending=0)
		restrts = []
		for i in range(0,query_results.shape[0]):
		    restrts.append(dict(distance=query_results.iloc[i]['ds'],name=query_results.iloc[i]['name'].decode('utf-8'), address=query_results.iloc[i]['full_address'].decode('utf-8'), stars1=query_results.iloc[i]['stars_y'], stars2=query_results.iloc[i]['stars_z'], reviews1=query_results.iloc[i]['num'], reviews2=query_results.iloc[i]['review_count']))
		the_result = ''
		the_result = 1#ModelIt(patient,births)
		return render_template("output.html", addy = addy, numq = numq, occay = occay, sb = sb,restrts = restrts, the_result = the_result)
def find_dist(lat1,lng1,lat2,lng2):
    return ((lat1-lat2)**2+(lng1-lng2)**2)**.5*97.76

