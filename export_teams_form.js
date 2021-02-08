Node.prototype.q = function(regex){
  return regex.global
    ? [...this.querySelectorAll(regex.source)]
    : this.querySelector(regex.source);
}
Node.prototype.Q = function(regex){
  return this.matches(regex.source)
    ? this
    : this.parentNode
        ? this.parentNode.Q(regex)
        : null;
}
function getValue(e){
  if(e === null) return '';
  return (e.constructor === String
    ? e
    : e.innerText || e.wholeText || e.value || [...e.children].map(f => getValue(f)).join('\n')
  ).replace(/\n{2,}/, '\n').trim();
}
function getTitle(e){
  return [
    getValue(e.q(/div.office-form-question-title > span:not(.ordinal-number)/)),
    ...[...e.q(/img:not([alt="Asistivní čtečka"])/g)].map(e => e.src),
    ...(e.q(/div.image-alternative-text/) ? ['<IMG>'] : []),
  ].filter(x => x).join('\n').replace(/\n{2,}/, '\n');
}
function getResults(e){
    return getValue(e.q(/.office-form-theme-quiz-point/));
}
answerMap = '?-++'; // option, answer, correct, correct answer
function getRole(e){
    var role = e.getAttribute('role') || e.className.trim();
    if(role) return role;
    if(e.q(/input[type="radio"]/)) return 'radiogroup';
    if(e.q(/input[type="checkbox"]/)) return 'group';
}
function getAnswers(e, i){
  var f = e.q(/.office-form-question-element > div/);
  switch(getRole(f, i)){
    case 'radiogroup': // radio
      var answers = f.q(/.office-form-question-choice/g);
      var answer = f.q(/:checked/);
      answer = answer
        ? answer.Q(/.office-form-question-choice/)
        : null;
      var correct = f.q(/.office-form-answerkey/)
      correct = correct
        ? correct.Q(/.office-form-question-choice/)
        : null;
      return answers.map(g =>
        `${answerMap[2*(g === correct) + (g === answer)]} ${getValue(g)}`
      ).join('\n');
    case 'group': // checkbox
      var answers = f.q(/.office-form-question-choice/g);
      var answer = new Set(f.q(/:checked/g).map(g => g.Q(/.office-form-question-choice/)));
      var correct = new Set(f.q(/.office-form-answerkey/g).map(g => g.Q(/.office-form-question-choice/)));
      return answers.map(g =>
        `${answerMap[2*(correct.has(g)) + (answer.has(g))]} ${getValue(g)}`
      ).join('\n');
    case 'listbox': // ordered list
      var answers = f.q(/.office-form-sort-item/g);
      var answer = answers.map(g => getValue(g.q(/.office-form-sort-item-content/)));
      var correct = f.q(/.various-short-text-correct-answer-list/);
      correct = correct
        ? getValue(correct).split(':', 2)[1].split(',').map(x => getValue(x))
        : f.q(/.office-form-right-answerkey/)
          ? answer
          : null
      return (correct || answer).map((x, j) => `${answerMap[2*!!correct + 1]} ${j+1} ${x}`).join('\n');
    case 'student-feedback-view-short-text-field-with-correctness': // text
      var answer = getValue(f.q(/input,textarea/));
      var correct = f.q(/.various-short-text-correct-answer-list/);
      correct = correct
        ? getValue(correct).split(':', 2)[1].split(',').map(x => getValue(x))
        : f.q(/.image-button-answerkey/)
          ? answer
          : null // TODO: fill missing data based on points?
      return `${answerMap[2*!!correct + !!answer]} ${correct || answer}`;
  }
  setTimeout(() => console.log(`Unimplemented ${i+1}:`, f));
  return getValue(f).split('\n').map(line => `? ${line}`).join('\n');
}
function parseQuestion(e, i){
  return `${i+1}\n${getTitle(e, i)}\n${getResults(e, i)}\n${getAnswers(e, i)}`;
}
console.log([...document.q(/div.office-form-question-content/g)].map(parseQuestion).join('\n\n'));
