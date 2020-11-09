header = document.querySelector('.wishlist_header').innerText;

titles = document.querySelectorAll('.title');
prices = document.querySelectorAll('.discount_final_price');
games = Array(4).fill().map((_, i) => {return {name: titles[i].innerText, url: titles[i].href, price: prices[i].innerText}});

console.log(`${header}
${games.map(x => `\t- ${x.name} ${x.price}\n\t (${x.url})`).join('\n')}`)
