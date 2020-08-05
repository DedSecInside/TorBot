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
    ip=content['ip']
    port=content['port']
    no_socks=content['no_socks']
    url=content['url']
    gather=content['gather']
    version=content['version']
    update=content['update']
    mail=content['mail']
    info=content['info']
    save=content['save']
    visualize=content['visualize']
    depth=content['depth']
    download=['download']
    
    
    args={'ip':ip,'port':port,'no_socks':no_socks,'url':url,'gather':gather,'version':version,'update':update,
          'mail':mail,'info':info,'save':save,'visualize':visualize,'depth':depth,'download':download
    
    }
    data1=test(args)
    return jsonify(data=str(data1)), 200, {'Access-Control-Allow-Origin': '*'} 
    
app.run()
