import React from 'react';
import ReactDOM from 'react-dom';
import Home from './home';
import './links.css';

class Links extends React.Component {
    constructor(props) {
        super(props);
        this.links = props.links;
        this.onHome = this.onHome.bind(this);
    }

    onHome(event) {
        ReactDOM.render(<Home/>, document.getElementById('root'));
    }

    render() {
        let items = this.links;
        return (
            <React.Fragment>
            <ol>
                {items.map((item, i) => <li key={i}>{item}</li>)}
            </ol>
            <input type='button' onClick={this.onHome} value='HOME' className='home-button'/>
            </React.Fragment>
        )
    }
}

export default Links;
