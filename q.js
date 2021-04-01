function q(input, n = undefined) {
  if (input == null) return null;
  if (input instanceof Node) return q_multiply(input, n);
  switch(input.constructor){
    case RegExp: return document.q(input, n);
    case Array: return q_multiply(input.map((x) => q(x)), n);
    default:
      let template = document.createElement('template');
      template.innerHTML = input;
      let children = template.content.childNodes;
      switch(children.length){
        case 0: return q_multiply(new Text(), n);
        case 1: return q_multiply(children[0], n);
        default: return q_multiply([...children], n);
      }
  }
}
function q_multiply(input, n) {
  return n == null ? input : new Array(n).fill().map(_ =>
    input instanceof Node ? input.cloneNode(!0) : input.map(arguments.callee)
  );
}
