header = document.querySelector('.wishlist_header').innerText;

function parsePrice(e){
    var a, b;
    if(a = e.querySelector('.discount_final_price')){
        if(b = e.querySelector('.discount_original_price'))
            return `~~${b.innerText}~~ ${a.innerText}`;
        else
            return a.innerText;
    }
    else if(a = e.querySelector('.coming_soon_link')){
        return 'NaN€';
    }
    else
        return '0€';
}
titles = document.querySelectorAll('.title');
prices = document.querySelectorAll('.purchase_container');
games = Array(titles.length).fill().map((_, i) => {return {name: titles[i].innerText, url: `https://store.steampowered.com${new URL(titles[i].href).pathname}`, price: parsePrice(prices[i])}});

games = games.filter(x => x.price !== 'NaN€' && x.price !== '0€');
console.log(`${header}
${games.map(x => `\t- ${x.name} ${x.price}\n\t (${x.url})`).join('\n')}`);
