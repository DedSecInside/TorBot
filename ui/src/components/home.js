import React from 'react';
import ReactDOM from 'react-dom';

import Links from './links';
import './home.css';

var websocket;
var links = [];

/**
 * Handles incoming WebSocket Messages
 *
 * @param msg {object} - contains message from WS server 
 */
function handleMessage(msg) {
    let link = JSON.parse(msg.data);
    if (link.error) {
        console.error(link.error);
        return;
    }
    links.push(link);
    ReactDOM.render(<Links websocket={websocket} links={links}/>, document.getElementById('root'));
}

class Home extends React.Component {
    constructor(props) {
        super(props);
        this.state = {url: ''};
        this.onSubmit = this.onSubmit.bind(this);
        this.onUrlChange = this.onUrlChange.bind(this);
    }

    onUrlChange(event) {
        event.persist();
        this.setState({url: event.target.value}, function() {
            if (event.key === 'Enter') this.onSubmit(event);
        });
    }

    onSubmit(event) {
        event.preventDefault();
        let ws = new WebSocket('ws://localhost:8080');
        websocket = ws;
        let msg = {
            'url': this.state.url,
            'action': 'get_links'
        }
        ws.onopen = () => ws.send(JSON.stringify(msg));
        ws.onmessage = handleMessage;
        ws.onerror = (error) => {
            console.error(error);
        };
        ws.onclose = () => {
            links = [];
        };
    }

    render() {
        return (
            <React.Fragment>
                <form>
                    <h1 align='center'>TorBot</h1>
                    <input onKeyDown={this.onUrlChange} className='search-bar' type='text'/>
                    <input type='button' onClick={this.onSubmit} value='SELECT' className='submit-button'/>
                </form>
            </React.Fragment>
        );
    }
}

export default Home;
