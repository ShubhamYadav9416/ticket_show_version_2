# import all essential libraries
import json
from flask import request,jsonify
from flask_restful import Resource,reqparse,abort,fields,marshal_with
from flask_jwt_extended.view_decorators import jwt_required

# impo tables and internal functions
from application.data.models import db,Theater,TheaterMovie,Booking,UserTheaterRating
from application.data.data_access import get_all_theaters

# post args
theater_post_args = reqparse.RequestParser()
theater_post_args.add_argument('theater_name', type=str, required=True, help="theater name is required")
theater_post_args.add_argument('theater_place', type=str, required=True, help="theater place is required")
theater_post_args.add_argument('theater_location', type=str, required=True, help="theater location is required")
theater_post_args.add_argument('theater_capacity', type=str, required=True, help="theater capacity is required")


# put args
theater_put_args = reqparse.RequestParser()
theater_put_args.add_argument('theater_name', type=str)
theater_put_args.add_argument('theater_place', type=str)
theater_put_args.add_argument('theater_location', type=str)
theater_put_args.add_argument('theater_capacity', type=str)


# resource fields for marshaliing
resource_fields = {
    'theater_id': fields.Integer,
    'theater_name' : fields.String,
    'theater_place': fields.String,
    'theater_location': fields.String,
    'theater_capacity': fields.Integer,
    'theater_image_path' : fields.String
}



class AllTheaterAPI(Resource):
    # --------------------------------------------------
    # --------------theater caching--------------------
    # -------------------------------------------------
    # get all movies
    @jwt_required()
    def get(resource):
        theaters_list = get_all_theaters()
        return theaters_list
    
    # post a theater
    @marshal_with(resource_fields)
    @jwt_required()
    def post(resource):
        args = theater_post_args.parse_args()
        theater= Theater.query.filter_by(theater_name=args["theater_name"]).first()
        if theater:
            abort(409,message= "theater is already exist")
        input = Theater(theater_name = args["theater_name"], theater_place = args['theater_place'], theater_location = args['theater_location'], theater_capacity = int(args['theater_capacity']))  #, theater_image_path = args['theater_image_path'])
        db.session.add(input)
        db.session.commit()
        return input, 201
    
class TheaterAPI(Resource):
    # get specific theater
    @marshal_with(resource_fields)
    @jwt_required()
    def get(self,theater_id):
        theater = Theater.query.filter_by(theater_id=theater_id).first()
        print(theater)
        if not theater:
            abort(404, message="Could not found theater with this id")
        return theater
    
    # API for theater edit
    @marshal_with(resource_fields)
    @jwt_required()
    def put(self,theater_id):
        args = theater_put_args.parse_args()
        theater = Theater.query.filter_by(theater_id = theater_id).first()
        if not theater:
            abort(404, message="theater doesn't exist.")
        # input = theater(theater_id=theater_id, theater_name = args["theater_name"], theater_place = args['theater_place'], theater_location = args['theater_location'], theater_capacity = args['theater_capacity'], theater_image_path = args['theater_image_path'])
        if args['theater_name']:
            theater.theater_name = args['theater_name']
        if args['theater_place']:
            theater.theater_place = args['theater_place']
        if args['theater_location']:
            theater.theater_location = args['theater_location']
        if args['theater_capacity']:
            theater.theater_capacity = args['theater_capacity']
        db.session.commit()
        return theater
    
    # API for deleting theater
    @marshal_with(resource_fields)
    @jwt_required()
    def delete(self, theater_id):
        theater_ratings = UserTheaterRating.query.filter_by(theater_id = theater_id).all()
        if theater_ratings:
            for theater_rating in theater_ratings:
                db.session.delete(theater_rating)
                db.session.commit()
        theatermovies = TheaterMovie.query.filter_by(theater_id = theater_id).all()
        if theatermovies:
            for theatermovie in theatermovies:
                print(theatermovie)
                bookings = Booking.query.filter_by(theater_movie_id = theatermovie.theater_movie_id).all()
                if bookings:
                    for booking in bookings:
                        db.session.delete(booking)
                        db.session.commit()
            db.session.delete(theatermovie)
            db.session.commit()
        theater = Theater.query.filter_by(theater_id = theater_id).first()
        if not theater:
            abort(404,message= "movie id not exist")
        db.session.delete(theater)
        db.session.commit()
        return jsonify({'status':"success",'message' : 'Theater has been deleted!'})


# {
#     "theater_name" : "INox",
#     "theater_place": "New delhi",
#     "theater_location" : "connaugt palace",
#     "theater_capacity": 50,
#     "theater_image_path" : "image_path.png"
# }
