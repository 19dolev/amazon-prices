import React from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';

class NameForm extends React.Component {


  constructor(props) {
    super(props);
    this.state = {value: '', respo: ''};
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({value: event.target.value});

  }

  handleSubmit(event) {
  //this.state.value
  event.preventDefault();
  const amazon_url = this.state.value;
  axios.post('http://localhost:5000/calculate', {amazon_url})
      .then(res => {
        console.log(res);
        console.log(res.data);
        this.setState({respo: JSON.stringify(res.data)});
      })
  }

  render() {
    return (
      <div>
        <form onSubmit={this.handleSubmit}>
          <label>
            Amazon URL:
            <input type="text" value={this.state.value} onChange={this.handleChange} />
          </label>
          <input type="submit" value="Submit" />
        </form>
        <br></br>
        <label>{this.state.respo}</label>
      </div>
    );
  }
}
ReactDOM.render(<NameForm/>, document.getElementById("root"));
