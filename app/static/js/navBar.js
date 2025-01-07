const toggleBtn = document.querySelector("button.menu-burger")
const navLinksContainer = document.querySelector(".nav-container")

toggleBtn.addEventListener('click', ()=> {
  toggleBtn.classList.toggle('active')
    navLinksContainer.classList.toggle('active')
    document.body.classList.toggle('no-scroll')
})
