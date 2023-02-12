from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice



app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    
    def to_dic(self):
        """converts to dictionary"""
        return {column.name: getattr(self ,column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")
    


@app.route('/all' , methods = ["GET"])
def all():
    cafes = db.session.query(Cafe).all()
    
    return jsonify(cafes=[cafe.to_dic() for cafe in cafes])

@app.route('/search' , methods = ["GET"])
def search():
    
    cafes = db.session.query(Cafe).all()
    user_location = request.args.get('location')
    print(user_location)
    wanted_location = [cafe.to_dic() for cafe in cafes if cafe.location == user_location]
    
    if wanted_location:
        return jsonify(cafes = wanted_location)
    else:
        return jsonify(error = {
            "Not Found" : "Sorry, we don't have a cafe at that location."
        })


## HTTP GET - Read Record
@app.route('/random' , methods = ["GET"])
def random():
    cafes = db.session.query(Cafe).all()
    random_user = choice(cafes)


    return jsonify(cafe={
        "name" : random_user.name,
        "map_url" : random_user.map_url,
        'location' : random_user.location,
        
        "ammenities" :{
            "seats" : random_user.seats,
            "has_toilet" : random_user.has_toilet,
        }
    })

## HTTP POST - Create Record
@app.route('/add' , methods = ["POST"])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    
    return  jsonify(response = {
        "success" : "Succesfully added Cafe"
    })

## HTTP PUT/PATCH - Update Record

@app.route('/update-price/<int:cafe_id>' , methods = ["PATCH"])
def update_price(cafe_id):
    
    try:
        data = db.session.query(Cafe).get(cafe_id)
        data.coffee_price = request.args.get('new_price')
        db.session.commit()
        return jsonify(response = {"success" : "Successfully Updated The Price"}) , 200
    
    except Exception as e:
        return jsonify( error = {
            "Not Found" : "Sorry a cafe with that Id was not found"
        }) , 404

## HTTP DELETE - Delete Record
@app.route('/report-closed/<int:cafe_id>' , methods = ["DELETE"])
def closed(cafe_id):
    try:
        delete_cafe = db.session.query(Cafe).get(cafe_id)
        if delete_cafe:
            db.session.delete(delete_cafe)
            db.session.commit()
            return jsonify(response = {
                "Success" : "Cafe Deleted Successfully"
            }) , 200
        else:
            return jsonify(error = {
            "Not Found" : "The id Doesn't exist"
        }) , 404
    except Exception:
        return jsonify(error = {
            "Forbidden" : "Sorry , Not Allowed. Check your api key"
        }) , 403


if __name__ == '__main__':
    app.run(debug=True)
