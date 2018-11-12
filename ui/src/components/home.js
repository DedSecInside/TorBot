import React from 'react';
import './home.css';
import img from './images/tor-onion.jpg'


function handleMessage(msg) {
    console.info(msg.data);
}

class Home extends React.Component {
    
    constructor(props) {
        super(props);
        this.state = {url: ''};
        this.onSubmit = this.onSubmit.bind(this);
        this.onUrlChange = this.onUrlChange.bind(this);
    }
    
    onUrlChange(event) {
        if (event.key === 'Enter') this.onSubmit();
        this.setState({url: event.target.value});
    }

    onSubmit(event) {
        let ws = new WebSocket('ws://localhost:8080')
        ws.onopen = () => ws.send(this.state.url);
        ws.onmessage = handleMessage;
    }

    render() {
        return (
            <React.Fragment>
                <form>
                    <h1 align='center'>TorBot</h1>
                    <input onKeyDown={this.onUrlChange} className='search-bar' type='text'/>
                    <img onClick={this.onSubmit} className='submit-button' src={img}/>
                </form>
            </React.Fragment>
        );
    }
}

export default Home;
