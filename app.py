from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""
    plants_data = mongo.db.plants.find()  # Retrieve all plants from the 'plants' collection
    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        new_plant = {
            'name': request.form['plant_name'],
            'variety': request.form['variety'],
            'photo_url': request.form['photo'],
            'date_planted': request.form['date_planted']
        }
        result = mongo.db.plants.insert_one(new_plant)  # Insert the new plant into the 'plants' collection
        return redirect(url_for('detail', plant_id=str(result.inserted_id)))

    return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""
    plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})  # Find the plant by its ID
    harvests = mongo.db.harvests.find({'plant_id': plant_id})  # Find all harvests for this plant

    context = {
        'plant': plant_to_show,
        'harvests': harvests
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """Accept a POST request with data for 1 harvest and inserts into database."""
    new_harvest = {
        'quantity': request.form['harvested_amount'],  # Amount harvested
        'date': request.form['date_planted'],  # Date harvested
        'plant_id': plant_id  # Link to the plant ID
    }
    mongo.db.harvests.insert_one(new_harvest)  # Insert the harvest into the 'harvests' collection

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        updated_plant = {
            'name': request.form['plant_name'],
            'variety': request.form['variety'],
            'photo_url': request.form['photo'],
            'date_planted': request.form['date_planted']
        }
        mongo.db.plants.update_one(
            {'_id': ObjectId(plant_id)},
            {'$set': updated_plant}  # Update the plant with the new data
        )
        return redirect(url_for('detail', plant_id=plant_id))
    else:
        plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})  # Fetch the plant data
        context = {
            'plant': plant_to_show
        }
        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    mongo.db.plants.delete_one({'_id': ObjectId(plant_id)})  # Delete the plant
    mongo.db.harvests.delete_many({'plant_id': plant_id})  # Delete all associated harvests

    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)

