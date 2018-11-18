import React from 'react';
import ReactDOM from 'react-dom';
import Home from './home';
import './links.css';

class Links extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            host: props.host,
            port: props.port,
            url: props.url,
            links: []
        };
        this.onHome = this.onHome.bind(this);
        this.onMsg = this.onMsg.bind(this);
        this.initWS();
    }

    initWS() {
        this.websocket = new WebSocket('ws://' + this.state.host + ':' + this.state.port)
        let msg = {'url': this.state.url, 'action': 'get_links'};
        this.websocket.onopen = () => this.websocket.send(JSON.stringify(msg));
        this.websocket.onmessage = this.onMsg;
        this.websocket.onerror = (error) => console.error(error);
    }

    onMsg(msg) {
        let link = JSON.parse(msg.data);
        if (link.error) {
            console.error(link.error);
            return;
        }
        let stateLinks = this.state.links;
        stateLinks.push(link)
        this.setState({links: stateLinks});
    }

    onHome(event) {
        this.websocket.close(1000); // Send normal closure code
        ReactDOM.render(<Home/>, document.getElementById('root'));
    }

    render() {
        let links = this.state.links;
        if (!links.length) {
            return <h1>Links Incoming</h1>;
        }
        return (
            <React.Fragment>
            <ol>
                {
                    links.map(function(link, i) {
                        if (link.status) {
                            return <li className="good-link" key={i}>{link.name}</li>;
                        } else {
                            return <li className="bad-link" key={i}>{link.name}</li>;
                        }
                    }
                )}
            </ol>
            <input type='button' onClick={this.onHome} value='HOME' className='home-button'/>
            </React.Fragment>
        )
    }
}

export default Links;
