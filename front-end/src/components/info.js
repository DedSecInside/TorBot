import React from 'react';

class Info extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            url: props.url,
            host: props.host,
            port: props.port
        };
        this.onMsg = this.onMsg.bind(this);
        this.initWS();
    }

    initWS() {
        this.websocket = new WebSocket('ws://' + this.state.host + ':' + this.state.port);
        let msg = {'url': this.state.url, 'action': 'get_info'};
        this.websocket.onopen = () => this.websocket.send(JSON.stringify(msg));
        this.websocket.onmessage = this.onMsg;
        this.websocket.onerror = (error) => console.error(error);
    }

    onMsg(msg) {
        let info = JSON.parse(msg.data);
        for (var key in info) {
            console.log(key + ': ' + info[key]);
        }
    }

    render() {
        return <h1>INFO</h1>
    }
}

export default Info;
