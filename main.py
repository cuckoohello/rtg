from typing import List
import tempfile

import matplotlib as mpl
mpl.use("Agg")

import matplotlib.pyplot as plt

def rtg(time: List, blood_glucose: List,  uge: float, egfr: float, uge_unit: str = "mmol", gfr_unit: str = "mmol/L", h_step: float = 0.01, v_step: float = 0.005):
    import numpy as np
    from scipy.interpolate import interp1d

    if uge_unit == 'g':
        uge = uge*5.551 # 1g = 5.551mmol
    elif uge_unit != 'mmol':
        raise Exception(f"{uge_unit} is not a valid uge unit")

    if gfr_unit == 'mg/dl':
        uge = uge / 0.05551
    elif gfr_unit != 'mmol/L':
        raise Exception(f"{gfr_unit} is not a vlid gfr unit")

    # if gfr_unit == 'mg/dl':
    #     blood_glucose = [ blood*0.05551 for blood in blood_glucose]
    # elif gfr_unit != 'mmol/L':
    #     raise Exception(f"{gfr_unit} is not a vlid gfr unit")

    f = interp1d(time, blood_glucose, kind='cubic')
    x, h_step = np.linspace(min(time), max(time), num=int((max(time)-min(time))/h_step+1), endpoint=True, retstep=True)
    y = f(x)

    last = None
    results = []
    for i in np.arange(0, max(y), v_step):
        tmp = y -i
        area = tmp[tmp>0].sum()*egfr*h_step
        if i == 0:
            last = area
        
        if area == uge:
            results.append(i)
        elif (area-uge)*(last-uge) < 0:
            results.append(i-v_step/2)
        
        last = area
    
    # if gfr_unit == 'mg/dl':
    #     results = [value/0.05551 for value in results]

    if len(results) != 1:
        return []

    filename = f"static/imgs/{next(tempfile._get_candidate_names())}.png"

    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    ax.plot(x, y, color='orange')
    ax.plot(time, blood_glucose, 'o')
    ax.axhline(y=results[0], color='g', linestyle='-', label='rtg')
    ax.annotate(F"RTG={round(results[0], 2)}{gfr_unit}", xy=(50, results[0]-0.4))
    ax.set(xlabel='time(min)', ylabel=f'BG({gfr_unit})')
    ax.set_xlim(0, np.max(time))

    fig.savefig(filename)   # save the figure to file
    plt.close(fig)    # close the figure window

    return [{"value": results[0], "url": filename}]


def create_app():
    from flask import Flask, request, jsonify, abort, send_from_directory
    app = Flask(__name__)

    @app.route("/rtg", methods=["POST"])
    def post_rtg():
        import math
        try:
            gfr = request.json.get("gfr")
            uge = request.json.get("uge")
            height = request.json.get("height")
            weight = request.json.get("weight")
            uge = uge/math.sqrt(height*weight/3600)*1.73
            time = request.json.get("x")
            blood_glucose = request.json.get("y")
            uge_unit = request.json.get("ugeUnit")
            gfr_unit = request.json.get("gfrUnit")
            return jsonify(rtg(time=time, blood_glucose=blood_glucose, uge=uge, egfr = gfr/1000, uge_unit=uge_unit, gfr_unit=gfr_unit))
        except:
            return jsonify([])
    
    @app.route("/")
    def index():
        return send_from_directory('static/', 'index.html')

    @app.route('/<path:path>')
    def send_lib(path):
        return send_from_directory('static/', path)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=False)