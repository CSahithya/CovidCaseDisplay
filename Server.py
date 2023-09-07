import requests
from flask import Flask, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def get_state_data(state):
    url = f"https://api.covidtracking.com/v1/states/{state}/daily.json"
    response = requests.get(url)
    print(url)
    if response.status_code == 200:       
        api_data = response.json()
        selected_days = api_data[:7]  
        dates = [datetime.strptime(str(day['date']), "%Y%m%d").strftime("%Y-%m-%d") for day in selected_days]
        positives = [day['positive'] for day in selected_days]
        negatives = [day['negative'] for day in selected_days]
        return dates,positives,negatives
    else:
        return "Failed to retrieve the API"


def get_dates_data(state,fromDate,toDate):
    from_date = datetime.strptime(fromDate, "%Y-%m-%d")
    to_date = datetime.strptime(toDate, "%Y-%m-%d")
    if to_date < from_date:
        alert_message = "Start date must be before the end date. You can go back and try"
        return render_template('Error.html', alert_message=alert_message)
    temp_date = from_date
    dates = ""
    positives = ""
    negatives = ""
    while temp_date <= to_date:
        temp_date_str = temp_date.strftime("%Y%m%d")
        # print(temp_date_str)
        url = f"https://api.covidtracking.com/v1/states/{state}/{temp_date_str}.json"
        response = requests.get(url)
        if response.status_code == 200:       
            api_data = response.json()
            res = ","
            if temp_date == from_date: 
                res = ""
            dates += res + str(temp_date.strftime("%Y-%m-%d"))
            positives += res + str(api_data['positive'])
            negatives += res + str(api_data['negative'])
        else:
            break
        temp_date += timedelta(days=1)
    return dates,positives,negatives



@app.route('/states', methods=['POST'])
def submit():
    state_v = request.form.get('states')
    # print(state_v)
    dates,positive,negative = get_state_data(state_v)
    dts = ", ".join([str(item) for item in dates])
    pos = ", ".join([str(item) for item in positive])
    neg = ", ".join([str(item) for item in negative])
    if dates and positive and negative:
        return render_template('states.html',dts=dts,pos=pos,neg=neg,state=state_v)        
    else:
        # print("It enters",result)
        return render_template('error.html')

@app.route('/dates', methods=['POST'])
def dates():
    fromDate =request.form.get('fromDate')
    toDate =request.form.get('toDate')
    state = request.form.get('state')
    dates,positive,negative = get_dates_data(state,fromDate=fromDate,toDate=toDate)
    # print(dates,positive,negative)
    if dates and positive and negative:
        return render_template('date.html',dts=dates,pos=positive,neg=negative,state=state,fromDate=fromDate,toDate=toDate)
    else:
        return render_template('error.html')
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
