import React, { Component } from 'react';
import TextFieldGroup from '../components/common/TextFieldGroup';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { addProduct } from '../actions/productActions';

class SellPosts extends Component {
  constructor() {
    super();
    this.state = {
      title: '',
      description: '',
      category: '',
      price: '',
      location: '',
      phone: '',
      errors: {},
    };

    this.onChange = this.onChange.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
  }

  componentWillReceiveProps(newProps) {
    if (newProps.errors) {
      this.setState({ errors: newProps.errors });
    }
  }

  onChange(e) {
    this.setState({ [e.target.name]: e.target.value });
  }

  onSubmit(e) {
    e.preventDefault();

    const newProduct = {
      title: this.state.title,
      description: this.state.description,
      category: this.state.category,
      location: this.state.location,
      phone: this.state.phone,
      price: this.state.price,
    };

    this.props.addProduct(newProduct);
  }

  render() {
    const errors = this.state.errors;

    return (
      <div className="container">
        <h1>Sell your PRODUCT</h1>

        <div>
          <form onSubmit={this.onSubmit}>
            <TextFieldGroup
              placeholder="Title"
              name="title"
              value={this.state.title}
              onChange={this.onChange}
              error={errors.title}
            />

            <TextFieldGroup
              placeholder="Description"
              name="description"
              value={this.state.description}
              onChange={this.onChange}
              error={errors.description}
            />

            <TextFieldGroup
              placeholder="Category"
              name="category"
              value={this.state.category}
              onChange={this.onChange}
              error={errors.category}
            />

            <TextFieldGroup
              placeholder="Price"
              name="price"
              value={this.state.price}
              onChange={this.onChange}
              error={errors.price}
            />

            <TextFieldGroup
              placeholder="Location"
              name="location"
              value={this.state.location}
              onChange={this.onChange}
              error={errors.location}
            />

            <TextFieldGroup
              placeholder="Mobile Phone Number"
              name="phone"
              value={this.state.phone}
              onChange={this.onChange}
              error={errors.phone}
            />
            <input type="submit" className="btn btn-info btn-block mt-4" />
          </form>
        </div>
      </div>
    );
  }
}

SellPosts.propTypes = {
  addProduct: PropTypes.func.isRequired,
  errors: PropTypes.object.isRequired,
};

const mapStateToProps = (state) => ({
  errors: state.errors,
});

export default connect(mapStateToProps, { addProduct })(SellPosts);
