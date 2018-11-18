import React from 'react';
import ReactDOM from 'react-dom';

import Links from './links';
import './home.css';


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
        ReactDOM.render(<Links host='localhost' port='8080' url={this.state.url}/>, document.getElementById('root')); 
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
