import React, { Component } from 'react';
import PropTypes from 'prop-types';
import CommentItem from './CommentItem';

class CommentFeed extends Component {
  render() {
    const { comments, postId } = this.props;

    return comments.map((comment,index) => (
      <CommentItem key={comment.id} comment={comment} postId={postId} index={index}/>
    ));
  }
}

CommentFeed.propTypes = {
  comments: PropTypes.array.isRequired,
  postId: PropTypes.string.isRequired,
};

export default CommentFeed;
