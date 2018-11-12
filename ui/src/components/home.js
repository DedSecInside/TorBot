import React from 'react';


class Home extends React.Component {
    
    constructor(props) {
        super(props);
        this.state = {url: ''};
        this.onBtnClick = this.onBtnClick.bind(this);
    }

    onBtnClick(event) {
        this.setState({url: event.target.value});
        debugger;
    }

    render() {
        return (
            <React.Fragment>
                <h1 align='center'>TorBot</h1>
                <input type='text'/>
                <button onClick={this.onBtnClick}></button>
            </React.Fragment>
        );
    }
}

export default Home;
