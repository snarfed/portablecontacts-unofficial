/*
 * Minor utilities for the demo form on the front page.
 */

var USER_ID_BLURB = 'user id (optional)';
var ACCESS_TOKEN_RE = new RegExp('access_token=([^&]+)');

function get_demo_url() {
  var all_or_self = document.getElementById('all_or_self').value;
  var url = '/poco/@me/@' + all_or_self;

  var userid_elem = document.getElementById('userid');
  var userid = userid_elem.value;
  if (userid_elem.disabled != 'disabled' && userid != USER_ID_BLURB)
    url += '/' + userid;

  return url;
}

// the user id field's style depends on @all vs @self, whether the user has
// entered a value or not, and whether it has focus.
function update_userid_field() {
  var all_or_self = document.getElementById('all_or_self').value;
  var userid_elem = document.getElementById('userid');
  var userid = userid_elem.value;

  if (all_or_self == 'self') {
    userid_elem.disabled = 'disabled';
    userid_elem.style.display = 'none';
  } else {
    userid_elem.disabled = null;
    userid_elem.style.display = 'inline';
    if (userid == '' || userid == USER_ID_BLURB) {
      
      userid_elem.value = USER_ID_BLURB;
      userid_elem.style.color = 'gray';
    } else {
      userid_elem.style.color = 'black';
    }
  }
}

/* Only used for Facebook's client side OAuth flow, which returns the access
 * token in the URL fragment.
 */
function access_token_from_fragment() {
  var match = window.location.hash.match(ACCESS_TOKEN_RE);
  if (match)
    document.getElementById('access_token').value = match[1];
}
