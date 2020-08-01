import sys
sys.path.append('..')
import flask
import argparse
from flask import request,jsonify
from torBot import test

app=flask.Flask(__name__)

app.config["DEBUG"]=True

@app.route('/postApi',methods=['POST'])
def callTor():
    content = request.get_json(force = True)
    url=content['url']
    port=content['port']
    args={'ip':'127.0.0.1','port':9050,'no_socks':False,'url':url,'gather':'False','version':'False','update':'False',
          'quiet':'False','mail':'False','info':'False','save':'False','visualize':'False','depth':'False','download':'False'
    
    }
    data1=test(args)
    return jsonify(data =str(data1)),201,{'Access-Control-Allow-Origin':'*'}
    
app.run()
