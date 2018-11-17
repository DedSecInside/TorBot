import React from 'react';
import ReactDOM from 'react-dom';
import Links from './links';
import './home.css';

/**
 * Handles incoming WebSocket Messages
 *
 * @param msg {object} - contains message from WS server 
 */
let links = [];
function handleMessage(msg) {
    let response = JSON.parse(msg.data);
    if (response.error) {
        console.error(response.error);
        return;
    }
    links.push(response.link);
    ReactDOM.render(<Links links={links}/>, document.getElementById('root'));
}

class Home extends React.Component {
    constructor(props) {
        super(props);
        this.state = {url: ''};
        this.onSubmit = this.onSubmit.bind(this);
        this.onUrlChange = this.onUrlChange.bind(this);
    }
    
    onUrlChange(event) {
        if (event.key === 'Enter') this.onSubmit(event);
        this.setState({url: event.target.value});
    }

    onSubmit(event) {
        event.preventDefault();
        let ws = new WebSocket('ws://localhost:8080');
        let msg = {
            'url': this.state.url,
            'action': 'get_links'
        }
        ws.onopen = () => ws.send(JSON.stringify(msg));
        ws.onmessage = handleMessage;
        ws.onerror = (error) => {
            console.error(error);
        };
        this.setState({url: ''});
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
