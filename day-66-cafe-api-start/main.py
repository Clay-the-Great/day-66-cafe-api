from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
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

    def to_dictionary(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random_one")
def random_one():
    all_cafes = Cafe.query.all()
    random_cafe = random.choice(all_cafes)
    return jsonify(
        cafe=random_cafe.to_dictionary()
    )


@app.route("/all")
def all():
    all_cafes = Cafe.query.all()
    all_cafes_dict = {cafe.id: cafe.to_dictionary() for cafe in all_cafes}
    return jsonify(all_cafes=all_cafes_dict)


@app.route("/search")
def search():
    location = request.args.get("loc")
    cafes_found = Cafe.query.filter_by(location=location).all()
    if len(cafes_found) == 0:
        return jsonify(
            error={
                "Not found": "No cafe at that location.",
            }
        )
    cafes_found_dict = {cafe.id: cafe.to_dictionary() for cafe in cafes_found}
    return jsonify(cafes_found=cafes_found_dict)


@app.route("/add", methods=["POST"])
def add():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.form["name"],
            map_url=request.form["map_url"],
            img_url=request.form["img_url"],
            location=request.form["location"],
            seats=request.form["seats"],
            has_toilet=(request.form["has_toilet"].lower() == "yes"),
            has_wifi=(request.form["has_wifi"].lower() == "yes"),
            has_sockets=(request.form["has_sockets"].lower() == "yes"),
            can_take_calls=(request.form["can_take_calls"].lower() == "yes"),
            # can_take_calls=bool(int(request.form["can_take_calls"])),
            coffee_price=request.form["coffee_price"],
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(
            response={
                "success": "New cafe added successfully.",
            }
        )


@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def patch(cafe_id):
    new_price = request.args.get("new_price")
    cafe_to_update = Cafe.query.get(cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(
            response={
                "success": "Coffee price successfully updated.",
            }
        ), 200
    else:
        return jsonify(
            error={
                "Not found": "No cafe with that ID found."
            }
        ), 404


@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    if request.args.get("api-key") == "TopSecretAPIKey":
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(
                response={
                    "success": "Cafe successfully deleted from database."
                }
            ), 200
        else:
            return jsonify(
                error={
                    "Not found": "No cafe with that ID found."
                }
            ), 404
    else:
        return jsonify(
            error="You are not authorized to delete anything in the database, fuck off."
        ), 403

# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
