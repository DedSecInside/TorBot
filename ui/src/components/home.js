import React from 'react';
import ReactDOM from 'react-dom';

import Links from './links';
import './home.css';

/**
 * Home page of TorBot 
 * @class Home
 */
class Home extends React.Component {
    constructor(props) {
        super(props);
        this.state = {url: ''};
        this.onSubmit = this.onSubmit.bind(this);
        this.onUrlChange = this.onUrlChange.bind(this);
    }

    /**
     * Sets state of url when user enters text
     * @memberof Home 
     * @param {object} event - event received from typing
     */
    onUrlChange(event) {
        event.persist();
        this.setState({url: event.target.value}, function() {
            if (event.key === 'Enter') this.onSubmit(event);
        });
    }

    /**
     * Asynchronously displays links from the state's url
     * @memberof Home
     * @param {object} event - event received from submitting form
     */
    onSubmit(event) {
        event.preventDefault();
        ReactDOM.render(<Links host='localhost' port='8080' url={this.state.url}/>, document.getElementById('root')); 
    }

    /**
     * Renders Home 
     * @memberof Home
     */
    render() {
        return (
            <React.Fragment>
                <form>
                    <h1 align='center'>TorBot</h1>
                    <input onKeyDown={this.onUrlChange} onPaste={this.onUrlChange} className='search-bar' type='text'/>
                    <input type='button' onClick={this.onSubmit} value='SELECT' className='submit-button'/>
                </form>
            </React.Fragment>
        );
    }
}

export default Home;
