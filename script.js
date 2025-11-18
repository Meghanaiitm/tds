const messages = [
    "AI makes hard tasks easier.",
    "GitHub Pages is ideal for static sites.",
    "You clicked the button.",
    "Learning is continuous.",
    "LLMs enhance productivity."
];
document.getElementById("generate").addEventListener("click", () => {
    const random = Math.floor(Math.random() * messages.length);
    document.getElementById("output").textContent = messages[random];
});