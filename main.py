from typing import List

def rtg(time: List, blood_glucose: List,  uge: float, egfr: float, h_step: float = 0.01, v_step: float = 0.005):
    import numpy as np
    from scipy.interpolate import interp1d
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
    
    return results

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
            return jsonify(rtg(time=time, blood_glucose=blood_glucose, uge=uge, egfr = gfr/1000))
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