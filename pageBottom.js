function scrollPosition(element) {
    return element.scrollTop;
}
function scrollHeight(element) {
    return element.scrollHeight - element.getBoundingClientRect().height;
}
function isScrolledToBottom(element) {
    return scrollPosition(element) >= scrollHeight(element);
}
