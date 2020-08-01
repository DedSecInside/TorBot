import flask
import argparse
from flask import request,jsonify
import torBot as tor
app=flask.Flask(__name__)

app.config["DEBUG"]=True

@app.route('/<string:name>')
def callTor(name: str):
    url="http://danielas3rtn54uwmofdo3x2bsdifr47huasnmbgqzfrec5ubupvtpid.onion/"
    args={'ip':'127.0.0.1','port':9050,'no_socks':False,'url':'http://danielas3rtn54uwmofdo3x2bsdifr47huasnmbgqzfrec5ubupvtpid.onion/','gather':'False','version':'False','update':'False',
          'quiet':'False','mail':'False','info':'False','save':'False','visualize':'False','depth':'False','download':'False'
    
    }
    data1=tor.test(args)
    return jsonify(data =str(data1)),200,{'Access-Control-Allow-Origin':'*'}
    
app.run()
