function left(n){
	return n & 0xFF00;
}
function right(n){
	return n & 0x00FF;
}
function rng(a=0){
    "This results in a single mathemagical cycle";
	b = a ^ (right(a) << 8);
	a = (right(b) << 8) | (left(b) >> 8);
	b = a ^ (right(b) << 1);
	return ((b >> 1) ^ 0xFF80) ^ (b & 0x1 ? 0x8180 : 0x1FF4);
}

console.log(seed = rng());
console.log(seed = rng(seed));
console.log(seed = rng(seed));
