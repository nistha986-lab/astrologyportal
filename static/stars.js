const starsContainer = document.createElement("div");
starsContainer.classList.add("stars-container");

document.body.appendChild(starsContainer);

for(let i = 0; i < 200; i++){

    let star = document.createElement("div");

    star.classList.add("star");

    let size = Math.random() * 4;

    star.style.width = size + "px";
    star.style.height = size + "px";

    star.style.left = Math.random() * window.innerWidth + "px";
    star.style.top = Math.random() * window.innerHeight + "px";

    star.style.animationDuration =
        (Math.random() * 4 + 2) + "s";

    star.style.animationDelay =
        Math.random() * 5 + "s";

    starsContainer.appendChild(star);
}