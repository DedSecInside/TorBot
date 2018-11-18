import React from 'react';
import Home from './components/home';
import './app.css';

/**
 * Entrypoint for TorBot app, displays home-page
 * @class App
 */
class App extends React.Component {
    render() {
        return <Home/>;
    }
}

export default App;
