import React from 'react';
import ReactDOM from 'react-dom';
import Links from './links';
import './home.css';

let links = [];
function handleMessage(msg) {
    links.push(msg.data);
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
        let ws = new WebSocket('ws://localhost:8080')
        ws.onopen = () => ws.send(this.state.url);
        ws.onmessage = handleMessage;
        ws.onerror = (error) => {
            console.error(error);
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
