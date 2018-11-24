import React from 'react';
import ReactDOM from 'react-dom';
import { library, dom } from '@fortawesome/fontawesome-svg-core';
import { faSpinner } from '@fortawesome/free-solid-svg-icons/faSpinner';
import './global.css';
import App from './app';

/**
 * Initially renders app and sets FontAwesome library
 */
library.add(faSpinner);
dom.watch();
ReactDOM.render(<App/>, document.getElementById('root'));

