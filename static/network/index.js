document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.edit-btn').forEach((button) => {
      button.addEventListener('click', () => {
          editPost(button);
      });
  });

  // edit post
  function editPost(button) {
      var parentElem = button.parentElement // access the "footer" div, which includes the button
      var grandparentElem = parentElem.parentElement; // access the "post" div, which includes the footer and the content
      var contentElement = getChildElement(grandparentElem, 'content');
      var oldContent = contentElement.innerHTML;
      var contentTextArea = document.createElement('textarea');
      contentTextArea.value = contentElement.innerHTML;
      contentTextArea.className = 'form-control';
      grandparentElem.replaceChild(contentTextArea, contentElement);

      var saveBtn = document.createElement('button')
      saveBtn.innerHTML = 'Save';
      saveBtn.id = 'save-btn';
      saveBtn.addEventListener('click', () => savePost(saveBtn, oldContent));
      parentElem.replaceChild(saveBtn, button)
  }

  // save post
  function savePost(button, oldContent) {
      var parentElem = button.parentElement
      var grandparentElem = parentElem.parentElement;
      var contentTextArea = getChildElement(grandparentElem, 'form-control');
      var contentElement = document.createElement('div');
      contentElement.innerHTML = contentTextArea.value;
      contentElement.className = 'content';
      grandparentElem.replaceChild(contentElement, contentTextArea);

      var editBtn = document.createElement('button')
      editBtn.innerHTML = 'Edit';
      editBtn.className = 'edit-btn';
      editBtn.addEventListener('click', () => editPost(editBtn))
      parentElem.replaceChild(editBtn, button);

      var postId = getChildElement(parentElem, 'key').innerHTML;

      // TODO: save info to server

      fetch(window.location.href, {
          method: 'PUT',
          body: JSON.stringify({
              type: 'edit',
              old_content: oldContent,
              new_content: contentElement.innerHTML,
              post_id: postId
          }),
          credentials: 'same-origin',
          headers: {
              'X-CSRFToken': getCookie('csrftoken')
          }
      });
  }

  // get cookies for CSRF token
  function getCookie(name) {
      // no cookie
      if (!document.cookie) {
          return null;
      }

      const token = document.cookie.split(';')
          .map(c => c.trim())
          .filter(c => c.startsWith(name + '='));

      // no cookie
      if (token.length === 0) {
          return null;
      }

      return decodeURIComponent(token[0].split('=')[1]);
  }


  function getChildElement(parentNode, wantedClass) {
      var children = parentNode.childNodes;
      for (child in children) {
          if (children[child].className === wantedClass) {
              return children[child];
          }
      }
  };

  document.querySelectorAll('.likes').forEach((button) => {
      button.addEventListener('click', () => {
          likePost(button);
      });
  });

  function likePost(button) {
      button.removeEventListener('click', likePost);
      var likeIcon = getChildElement(button, 'far fa-heart');
      var likedIcon = document.createElement('i');
      likedIcon.className = 'fas fa-heart';
      button.replaceChild(likedIcon, likeIcon);
      button.className = "liked";
      button.addEventListener('click', () =>{
          unlikePost(button);
      });
      var likes = getChildElement(button, 'like-num').innerHTML;
      likes++;
      getChildElement(button, 'like-num').innerHTML = likes;

      var footer = getChildElement(button.parentElement, 'footer');
      var postId = getChildElement(footer, 'key').innerHTML;

      fetch(window.location.href, {
          method: 'PUT',
          body: JSON.stringify({
              type: 'like',
              post_id: postId
          }),
          credentials: 'same-origin',
          headers: {
              'X-CSRFToken': getCookie('csrftoken')
          }
      });
  }

  document.querySelectorAll('.liked').forEach((button) => {
      button.addEventListener('click', () => {
          unlikePost(button)
      })
  })

  function unlikePost(button) {
      button.removeEventListener('click', unlikePost);
      var likedIcon = getChildElement(button, 'fas fa-heart');
      var likeIcon = document.createElement('i');
      likeIcon.className = 'far fa-heart';
      button.replaceChild(likeIcon, likedIcon);
      button.className = "likes";
      button.addEventListener('click', () =>{
          likePost(button);
      });
      var likes = getChildElement(button, 'like-num').innerHTML;
      likes--;
      getChildElement(button, 'like-num').innerHTML = likes;

      var footer = getChildElement(button.parentElement, 'footer');
      var postId = getChildElement(footer, 'key').innerHTML;

      fetch(window.location.href, {
          method: 'PUT',
          body: JSON.stringify({
              type: 'unlike',
              post_id: postId
          }),
          credentials: 'same-origin',
          headers: {
              'X-CSRFToken': getCookie('csrftoken')
          }
      });
  }

});