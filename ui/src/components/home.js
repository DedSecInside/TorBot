import React from 'react';
import ReactDOM from 'react-dom';

import Links from './links';
import Info from './info';
import './home.css';

/**
 * Home page of TorBot 
 * @class Home
 */
class Home extends React.Component {
    constructor(props) {
        super(props);
        this.state = {url: '', action: 'get_links'};
        this.onSubmit = this.onSubmit.bind(this);
        this.onUrlChange = this.onUrlChange.bind(this);
        this.onActionChange = this.onActionChange.bind(this);
        this.onSelection = this.onSelection.bind(this);
    }

    /**
     * Sets state of action when user makes selection from dropdown 
     * @memberof Home 
     * @param {object} event - event received from typing
     */
    onActionChange(event) {
        this.setState({action: event.target.value});
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
        switch (this.state.action) {
            case 'get_links':
                ReactDOM.render(<Links host='localhost' port='8080' url={this.state.url}/>, document.getElementById('root')); 
                break;
            case 'get_info':
                ReactDOM.render(<Info host='localhost' port='8080' url={this.state.url}/>, document.getElementById('root'));
                break;
        }
    }

    onSelection(event) {
        this.setState({action: event.target.value});
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
                    <br/>
                    <input 
                        onChange={this.onSelection} 
                        type="checkbox" 
                        value="get_links" 
                        checked={this.state.action === 'get_links'}
                    /> Get Links<br/> 
                    <input 
                        onChange={this.onSelection} 
                        type="checkbox" 
                        value="get_info" 
                        checked={this.state.action === 'get_info'}
                    /> Get Info<br/>
                </form>
            </React.Fragment>
        );
    }
}

export default Home;
