from flask import Flask,render_template,json, request,redirect,url_for, jsonify, send_file
from userQuery import UserQuery
from datetime import datetime
import logging
import os, io
import string
from werkzeug.utils import secure_filename
from convertFormat import TargetFormat

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
   return render_template('Home.html')
   #return "Novel Video Analytics and Tapestry"

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/getTotalCount')
def getTotalCount():
    
    t1 = str(request.values.get("t1"))
    t2 = str(request.values.get("t2"))

    t1 = t1.replace("T"," ") + ":00"
    t1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")

    t2 = t2.replace("T"," ") + ":00"
    t2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
    
    count = UserQuery.get_intruder_count(t1,t2)
    return render_template('TotalCount.html', t1=str(t1), t2=str(t2), count=count)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/getIntruderProfiles')
def getIntruderProfiles():
    t1 = str(request.values.get("t1"))
    t2 = str(request.values.get("t2"))

    t1 = t1.replace("T"," ") + ":00"
    t1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")

    t2 = t2.replace("T"," ") + ":00"
    t2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")

    intruder_id_list = UserQuery.get_intruders(t1,t2)

    return render_template('IntruderProfiles.html', idlist=intruder_id_list, t1=t1, t2=t2)

@app.route('/getTapestry')
def getTapestry():
	
	t1 = str(request.values.get("t1"))
	t2 = str(request.values.get("t2"))
	intruderid = request.values.get("intid")
	
	video_clips_list = UserQuery.get_intruder_video_clips(intruderid,t1,t2)
	
	for video_data in video_clips_list:
		video_data.file_path = string.replace(video_data.file_path,"avi","mp4")
		
   
	print "inside"
	return render_template('Tapestry.html', t1=t1, t2=t2, intid=intruderid, video_list = video_clips_list)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/getVideoClips')
def getVideoClips():
	print "hello"
	

	t1 = request.values.get("t1")
	t2 = request.values.get("t2")

	print "inside"
	try:
		# Input format: YYYY-mm-DDTHH:MM
		t1 = t1.replace('T', ' ').replace('Z', '')
		t1 += ":00"

		t2 = t2.replace('T', ' ').replace('Z', '')
		t2 += ":00"

		clips = UserQuery.get_video_clips(t1,t2)

		for clip in clips:
			path = clip.file_path
			clip.file_path = path.replace("avi","mp4")
			print "The video clip id: {} start time: {} end time: {} ".format(clip.file_path,clip.start_time,clip.end_time)


		return render_template('DisplayVideoClips.html', list=True, idlist=clips)

	except Exception as e:
		logging.exception("Error while processing")

@app.route('/playVideo')
def playVideo():
	path = str(request.values.get("path"))
	return render_template('PlayVid.html', path=path)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/uploadVideo',methods = ['POST'])
def uploadVideo():

	description = request.values.get("description")
	start_time = request.values.get("start_time")
	
	#start_time = start_time.replace('T', ' ').replace('Z', '')
	#start_time += ":00"
	
	start_time = start_time.replace("T"," ") + ":00"
	start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
	
	#print "type: {}".format(type(start_time))
	try:
		for file in request.files:
			print file
		f = request.files['file_path']
		print f
		f.save(secure_filename(f.filename))
		path = secure_filename(f.filename)
		print "path: "+path
	except Exception as e:
		logging.exception(e)
     
	return render_template('upload.html', start_time = start_time,description = description, file_path=path)
	
	
@app.route('/getAnalytics')
def getAnalytics():
	try:
	
		print "true"
		start_time = request.values.get("start_time")
		description = request.values.get("description")
		file_path = request.values.get("file_path")
		
		
		start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
		
		print start_time
		print description
		print file_path

		#print "type: {}".format(type(start_time))
		#print "type: {}".format(type(camera_id))
		
		print "getAnalytics"
		camera = UserQuery.get_analytics(description,file_path,start_time)
		count = UserQuery.get_count_by_id(camera.id)
		clips = UserQuery.get_video_clips_by_id(camera.id)

		
		
		for clip in clips:
			path = clip.file_path
			TargetFormat.convertFile(clip.file_path,TargetFormat.MP4)
			clip.file_path = path.replace("avi","mp4")
		
		print clip.file_path
		
		
		
		#print "count: {}".format(count)
		return render_template("FinalAnalytics.html",description = description,count = count,list=True, idlist=clips)
	except Exception as e:
		logging.exception("Error in getAnalytics")

	
if __name__ == '__main__':
   app.run()