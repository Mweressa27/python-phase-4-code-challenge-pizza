#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os
from flask import jsonify
from sqlalchemy.exc import IntegrityError


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in restaurants], 200

api.add_resource(Restaurants, "/restaurants")


class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        return restaurant.to_dict(rules=("restaurant_pizzas", "restaurant_pizzas.pizza")), 200

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204

api.add_resource(RestaurantByID, "/restaurants/<int:id>")


class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict(rules=("-restaurant_pizzas",)) for pizza in pizzas], 200

api.add_resource(Pizzas, "/pizzas")


class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        try:
            rp = RestaurantPizza(
                price=data["price"],
                restaurant_id=data["restaurant_id"],
                pizza_id=data["pizza_id"]
            )
            db.session.add(rp)
            db.session.commit()
            return rp.to_dict(rules=("restaurant", "pizza")), 201

        except (KeyError, ValueError, IntegrityError):
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400


api.add_resource(RestaurantPizzas, "/restaurant_pizzas")



if __name__ == "__main__":
    app.run(port=5555, debug=True)
