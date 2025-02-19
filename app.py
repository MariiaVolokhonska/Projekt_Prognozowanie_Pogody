from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import requests

app = Flask(__name__)
amount_of_days=0
token="e7c31fcb17cf0064a514"
sort_order = ""
miasto_from_input = "krakow"

@app.route("/", methods=['GET', 'POST'])
def home():
    global miasto_from_input 
    if request.method == "POST":
        miasto_from_input=request.form.get("miasto","krakow").casefold()

    (date,max_temp,min_temp, humidity,pressure)=get_weather_by_city(miasto_from_input,0)
    
    return render_template("index.html",date=date,max_temp=max_temp,min_temp=min_temp, humidity=humidity,pressure=pressure)
    
    

       
   

def get_weather_by_city(miasto,days):
    response = requests.get(f"https://dobrapogoda24.pl/api/v1/weather/simple?city={miasto}&day={days}&token={token}")
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from external API"}), 500
    if not response:
        return jsonify({"error": "No JSON received"}), 400
    data=response.json() # tutaj jest konwertowany json w slownik
    date = data.get("date", "Неизвестно")
    max_temp= data["day"]["temp_max"]
    min_temp=data["day"]["temp_min"]
    humidity=data["day"]["humidity"]
    pressure=data["day"]["pressure"]
    return (date,max_temp,min_temp, humidity,pressure)

@app.route("/forcast/<int:days>", methods=['GET', 'POST'])
def show_forcast(days):
    global sort_order
    global miasto_from_input 
    global amount_of_days
    amount_of_days=days

    if request.method == "POST":
        miasto_from_input = request.form.get("miasto","krakow").casefold()

    list_of_days = show_forcast_for_n_days(days, miasto_from_input)
    sorted_list = list_of_days
    if sort_order!="":
        sorted_list = sorted(list_of_days, key=lambda x: x[1], reverse=(sort_order == "desc"))
    
    
    return render_template("forcast.html", items=sorted_list, days=days, sort_order=sort_order)


def show_forcast_for_n_days(days,miasto):
    weather_n_days = [get_weather_by_city(miasto, i) for i in range(days)] 
    return weather_n_days
    
@app.route("/change-order", methods=['GET', 'POST'])
def change_order():
    global sort_order
    sort_order = "desc" if sort_order == "asc" else "asc" 

    return redirect(url_for('show_forcast', days=amount_of_days))

if __name__ == '__main__':
    app.run()

