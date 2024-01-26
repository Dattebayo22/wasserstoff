from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

def applying_filters(launch, search_filter, starting_year_filter, ending_year_filter, launch_success_filter, manufacturer_filter):
    # filters launches based on the search criteria.
    launch_year = int(launch.get('launch_year', '0'))
    launch_success_filter_value = str(launch.get('launch_success', '')).lower()
    manufacturer_value = str(launch.get('manufacturer', '')).lower()

    search_conditions = (
        (not search_filter or any(query.lower() in launch[field].lower() for query, field in [(search_filter, 'mission_name'), (search_filter, 'rocket_name')])) and
        (not starting_year_filter or launch_year >= int(starting_year_filter)) and
        (not ending_year_filter or launch_year <= int(ending_year_filter)) and
        (not launch_success_filter or launch_success_filter_value == launch_success_filter.lower()) and
        (not manufacturer_filter or manufacturer_value == manufacturer_filter.lower())
    )

    return search_conditions


@app.route('/')
def index():
    #renders the index page by fetching the data from the api
    response = requests.get('https://api.spacexdata.com/v3/launches')
    launches = response.json()

    #created a list of dictionaries to pass to the HTML template
    launch_data = []
    for launch in launches:
        try:
            manufacturer = launch['rocket']['second_stage']['payloads'][0]['manufacturer']
        except (KeyError, IndexError):
            manufacturer = 'N/A' 
        launch_info = {
            'flight_number': launch['flight_number'],
            'launch_year': launch['launch_year'],
            'launch_success': launch.get('launch_success', ''),
            'mission_name': launch['mission_name'],
            'rocket_name': launch['rocket']['rocket_name'],
            'manufacturer': manufacturer
        }
        launch_data.append(launch_info)

    #retrieve the values from the html template and ' ' as default values
    search_filter = request.args.get('search', default='')
    starting_year_filter = request.args.get('starting_year_filter', default='')
    ending_year_filter = request.args.get('ending_year_filter', default='')
    launch_success_filter = request.args.get('launch_success_filter', default='')
    manufacturer_filter = request.args.get('manufacturer_filter', default='')

    #filter launches based on the search query and filters
    new_launches = [launch for launch in launch_data if 
                         applying_filters(launch, search_filter, starting_year_filter, ending_year_filter, 
                                         launch_success_filter, manufacturer_filter)]

    #render the html template with the filtered list of launches
    return render_template('index.html', launches=new_launches, search_filter=search_filter,
                           starting_year_filter=starting_year_filter, ending_year_filter=ending_year_filter, launch_success_filter=launch_success_filter,
                           manufacturer_filter=manufacturer_filter)




@app.route('/details')
def get_launch_results():

    #used to check on the json fields
    response = requests.get('https://api.spacexdata.com/v3/launches')
    launches = response.json()
    return jsonify(launches)

if __name__ == '__main__':
    app.run(debug=True)
