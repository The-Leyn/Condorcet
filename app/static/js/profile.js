const toggleBtnProfil = document.querySelector(".profil-menu-burger")
const aside = document.querySelector("aside")

toggleBtnProfil.addEventListener('click', ()=> {
  toggleBtnProfil.classList.toggle('active')
  aside.classList.toggle('active')

  toggleBtn.classList.remove('active')
  navLinksContainer.classList.remove('active')
})