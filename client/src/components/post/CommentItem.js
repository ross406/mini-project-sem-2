import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { deleteComment } from '../../actions/postActions';
import parse from 'html-react-parser';

class CommentItem extends Component {
  onDeleteClick(postId, commentId) {
    this.props.deleteComment(postId, commentId);
  }

  render() {
    const { comment, postId, auth, index } = this.props;

    return (
      <div className="card card-body mb-3">
        <div className="row">
          <div className="col-md-2">
            <a href="">
            <div style={{width:"100px",height:"100px",borderRadius:"50%",backgroundColor:"black",color:"white",textAlign:"center",margin:"auto"}}>
                  <h1 style={{fontSize:"70px"}}>{String(comment.name).toUpperCase().slice(0, 1)}</h1>
                </div>
              {/* <img
                className="rounded-circle d-none d-md-block"
                src={comment.avatar}
                alt=""
              /> */}
            </a>
            <br />
            <p className="text-center">{comment.name}</p>
          </div>
          <div className="col-md-10">
            {/* <p className="lead">{comment.text} </p> */}
            {parse(comment.text)}
            {comment.user === auth.user.id ? (
              <button
                onClick={this.onDeleteClick.bind(this, postId, index)}
                type="button"
                className="btn btn-danger mr-1"
              >
                <i className="fa fa-times" />
              </button>
            ) : null}
          </div>
        </div>
      </div>
    );
  }
}

CommentItem.propTypes = {
  deleteComment: PropTypes.func.isRequired,
  comment: PropTypes.object.isRequired,
  postId: PropTypes.string.isRequired,
  auth: PropTypes.object.isRequired,
};

const mapStateToProps = (state) => ({
  auth: state.auth,
});

export default connect(mapStateToProps, { deleteComment })(CommentItem);
