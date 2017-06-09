
from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from imgurpython import ImgurClient
import random

import tornado.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.autoreload

from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
        
    return update_wrapper(no_cache, view)


client_id = 'ad00eb8d1bc9750'
client_secret = '3ed9705293df587cef5b37c83ee4fd1bddd2372c'

client = ImgurClient(client_id, client_secret)

# Initialize Flask and set some config values
app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mhoffmann:dbpass@NYC2-PROD-FC-ANALYTICS-1:5432/pic'
db = SQLAlchemy(app)


class Pic(db.Model):
	__tablename__ = 'pic'
	pic_id = db.Column(db.String(255), primary_key=True)
	category = db.Column(db.String(255))
	title = db.Column(db.String(255))
	description = db.Column(db.String(25500))
	datetime = db.Column(db.String(255))
	pic_type = db.Column(db.String(255))
	animated = db.Column(db.String(255))
	width = db.Column(db.String(255))
	height = db.Column(db.String(255))
	size = db.Column(db.String(255))
	i_views = db.Column(db.String(255))
	link = db.Column(db.String(255))
	num_presented = db.Column(db.Integer)
	num_voted = db.Column(db.Integer)
	


	
	def __init__(self, pic_id, category, title, description, datetime, pic_type, animated, width, height, size, i_views, link, num_presented, num_voted):
		
		self.pic_id = pic_id
		self.category = category
		self.title = title
		self.description = description
		self.datetime = datetime
		self.pic_type = pic_type
		self.animated = animated
		self.width = width
		self.height = height
		self.size = size
		self.i_views = i_views
		self.link = link
		self.num_presented = num_presented
		self.num_voted = num_voted
		
		
	def __str__(self):
		return(str(self.title))

	@property
	def serialize(self):
		return {
			'pic_id'        : self.pic_id,
			'category'		: self.category,
			'title'			: self.title,
			'description'	: self.description

		}




#Global list of topics for now, later get this generated from an api call


'''
topics = {'Funny':'xpiEk', 
         'The_More_You_Know':'xYm5j',
         'Science_and_Tech':'6EWCvJM',
         'Gaming':'pgz2W',
         'Eat_What_You_Want':'8aI20sf',
         'Aww':'ANy3hAw',
         'Inspiring':'r1UFj',
         'Awesome':'uKazo',
         'Creativity':'TaHSg',
         'The_Great_Outdoors':'uYXds',
         }
'''
topics = {
		 'Funny':'ZvbxK', 
         'The_More_You_Know':'7B6ZQ',
         #'Science_and_Tech':'6EWCvJM',
         'Gaming':'moIVG',
         #'Eat_What_You_Want':'gvo6s',  #sample size
         #'Aww':'nInetps',
         'Inspiring':'1lYpn',
         #'Awesome':'fjedu3O',
         #'Creativity':'43I173G',
         #'The_Great_Outdoors':'uYXds', # sample size
         'Cat':'uYXds',
         }

# Displays the home page.

# Users must be authenticated to view the home page, but they don't have to have any particular role.
# Flask-Security will display a login form if the user isn't already authenticated.
@app.route('/', methods=['GET'])
@nocache
def index():
		
	titles = {'items':[]}
	for key, value in topics.items():
		print(value)
		d = client.gallery_item(value)
		titles['items'].append({'link':d.images[0]['link'],'title':key})
	
	return render_template('index.html',data=titles['items'])




@app.route('/vote/<path:topic>', methods=['GET'])
@nocache
def vote(topic):
	
	category = client.gallery_tag(topic)
	items = {'data':[]}
	print(topic)
	for item in category.items:
		try:
			print("KKK")
			d = item.cover
		except:
			print("Here")
			items['data'].append(item)
			continue
	
	#return(str(len(items['data'])))
	#return('<br>'.join(items))
	competitors = random.sample(range(0, len(items['data'])-1), 2)
	final = []
	final.append(items['data'][competitors[0]])
	final.append(items['data'][competitors[1]])
	cat = topic
	topic = topic.replace("_", " ")
	
	return render_template('vote.html', data = final, topic=topic, cat=cat)



@app.route('/vote', methods=['POST'])
@nocache
def votethis():
	#db.create_all()
	data = request.get_json(force=True)
	
	pic_id_w = data['id_w']
	cat = data['cat_w']
	pic_id_l = data['id_l']
	
	
	try:
		item_w = Pic.query.filter(Pic.pic_id == pic_id_w).first()
	except:
		item_w = None
		pass
	
	try:
		item_l = Pic.query.filter(Pic.pic_id == pic_id_l).first()
	except:
		item_l = None
		pass
	
	
	if item_w is None:
		image_w = client.gallery_tag_image(cat,pic_id_w)
		i1 = Pic(pic_id = str(image_w.id),
				category = str(cat),
				title = str(image_w.title),
				description = str(image_w.description),
				datetime = str(image_w.datetime),
				pic_type = str(image_w.type),
				animated = str(image_w.animated),
				width = str(image_w.width),
				height = str(image_w.height),
				size = str(image_w.size),
				i_views = str(image_w.views),
				link = str(image_w.link),
				num_presented = 1,
				num_voted = 1,
				)
		db.session.add(i1)
	else:
		item_w.num_presented += 1
		item_w.num_voted += 1
	
	if item_l is None:
		image_l = client.gallery_tag_image(cat,pic_id_l)
		i2 = Pic(pic_id = str(image_l.id),
				category = str(cat),
				title = str(image_l.title),
				description = str(image_l.description),
				datetime = str(image_l.datetime),
				pic_type = str(image_l.type),
				animated = str(image_l.animated),
				width = str(image_l.width),
				height = str(image_l.height),
				size = str(image_l.size),
				i_views = str(image_l.views),
				link = str(image_l.link),
				num_presented = 1,
				num_voted = 0,
				)
		db.session.add(i2)
	else:
		item_l.num_presented += 1
	
	
	db.session.commit()
	
	return "Success"


@app.route('/results/<path:topic>', methods=['GET'])
@nocache
def results(topic):
	
	try:
		res = Pic.query.filter((Pic.category == topic)  ).all()
	except:
		res = None
		pass
	
	scores = {"data":[]}
	cat = ""
	for r in res:
		cat = r.category
		scores['data'].append({'score':int(round( r.num_voted / r.num_presented , 2)*100),
							   'title':r.title,
							   #'description':r.description,
							   'link':r.link})
	print(scores)
	
	return render_template('results.html', scores=scores['data'], topic=topic, cat=cat)


#Testing api call to grab images from category
@app.route('/test', methods=['GET'])
def test():

	category = client.gallery_tag("Awww")
	items = []
	for item in category.items:
		try:
			#print("KKK")
			d = item.cover
		except:
			#print("Here")
			items.append(item.link)
			continue
	
	
	
	return '<br>'.join(items)
'''
def run_server():
    # Create the HTTP server
    http_server = tornado.httpserver.HTTPServer(
        tornado.wsgi.WSGIContainer(app)
    )
    http_server.listen(2000)

    # Reads args given at command line (this also enables logging to stderr)
    tornado.options.parse_command_line()

    # Start the I/O loop with autoreload
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(io_loop)
    try:
        io_loop.start()
    except KeyboardInterrupt:
        pass
'''
# If running locally, listen on all IP addresses, port 8080
if __name__ == '__main__':
    #run_server()
    app.run(host='0.0.0.0',port=2000,debug=True)
