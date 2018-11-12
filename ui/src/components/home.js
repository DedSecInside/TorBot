import React from 'react';


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
                <h1 align='center'>TorBot</h1>
                <input onKeyDown={this.onUrlChange} type='text'/>
                <button onClick={this.onSubmit}></button>
            </React.Fragment>
        );
    }
}

export default Home;
