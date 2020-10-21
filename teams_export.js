function parseQuestion(q, i){
    var results = document.querySelector('.office-form-result-container');
    var title = [
        q.querySelector('div.office-form-question-title > span:not(.ordinal-number)').innerText,
        ...[...q.querySelectorAll('img:not([alt="Asistivní čtečka"])')].map(e => e.src),
        ...(q.querySelector('div.image-alternative-text') ? ['<IMG>'] : []),
    ].filter(x => x).join('\n');
    var points = q.querySelector('span.office-form-theme-quiz-point');
    points = points ? points.innerText.match(/\(počet bodů: (.+?)\)/)[1] : (results ? '?/?' : '?');
    var possible = [
        ...q.querySelectorAll('div.office-form-question-choice [aria-checked] ~ span'),
    ].filter(x => x);
    var selected = [
        q.querySelector('div.select-placeholder'),
        q.querySelector('input.office-form-textfield-input'),
        ...q.querySelectorAll('div.office-form-question-choice [aria-checked="true"] ~ span'),
        ...q.querySelectorAll('div.office-form-sort-item-content'),
    ].filter(x => x);
    var correct = [...q.querySelectorAll('[title="Správná odpověď"]')].map(e => e.parentNode.querySelector('input')).filter(x => x).map(e => e.type === 'radio' ? e.nextSibling : e);
    var c = q.querySelector('.various-short-text-correct-answer-list');
    if (c) correct = [...correct, ...c.childNodes[c.childNodes.length-1].wholeText.split(', ')];
    if (q.querySelector('.ms-Icon--CheckMark') && !correct.length){
        if (c = q.querySelector('.ms-Icon--CheckMark').parentNode.querySelector('input.office-form-textfield-input, [aria-checked] ~ span'))
            correct.push(c);
        else
            setTimeout(() => console.log(`Answer getter not implemented for ${i+1}.`, q));
    }
    var answers = new Map();
    function smush(ans, t){
        for(var e of ans) answers.set(typeof e === 'string' ? e : e.innerText || e.wholeText || e.value, t);
    }
    smush(possible, 0);
    smush(selected, 1);
    smush(correct, 2);
    var options = [...answers.entries()].map(([a, t]) => `${'?-+'[t]} ${a}`).join('\n');
    return `${i+1}. ${title}\n(${points} points)\n${options}`;
}
console.log([...document.querySelectorAll('div.office-form-question-content')].map(parseQuestion).join('\n\n'));
