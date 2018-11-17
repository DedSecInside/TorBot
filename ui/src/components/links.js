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
        let links = this.links;
        return (
            <React.Fragment>
            <ol>
                {
                    links.map(function(link, i) {
                        if (link.status) {
                            return <li className="good-link" key={i}>{link.name}</li>;
                        } else {
                            return <li className="bad-link" key={i}>{link.name}</li>;
                        }
                    }
                )}
            </ol>
            <input type='button' onClick={this.onHome} value='HOME' className='home-button'/>
            </React.Fragment>
        )
    }
}

export default Links;
