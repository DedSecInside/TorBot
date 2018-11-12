import React from 'react';

class Links extends React.Component {
    constructor(props) {
        super(props);
        this.links = props.links;
    }

    render() {
        let items = this.links;
        return (
            <ol>
                {items.map((item, i) => <li key={i}>{item}</li>)}
            </ol>
        )
    }
}

export default Links;
