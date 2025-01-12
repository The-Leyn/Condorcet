document.addEventListener("DOMContentLoaded", () => {
  const addOptionBtn = document.querySelector(".add-option");
  const optionsContainer = document.querySelector("#options-container");

  let optionIndex = 2;
  
  addOptionBtn.addEventListener("click", () => {
    optionIndex++;
    
    const optionDiv = document.createElement("div");
    optionDiv.classList.add("option");
    
    const input = document.createElement("input");
    input.type = "text";
    input.required = true;
    input.placeholder = `OPTION ${optionIndex}*`;
    input.name = `option${optionIndex}`;

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.innerHTML = `<img src="/static/assets/svg/delete.svg" alt="Icone supprimer">`;
    deleteButton.addEventListener("click", () => {
      optionDiv.remove();
    });

    optionDiv.appendChild(input);
    optionDiv.appendChild(deleteButton);
    optionsContainer.insertBefore(optionDiv, addOptionBtn);
  });


  document.addEventListener('click', event => {
    // Vérifie si le clic provient d'un élément ayant la classe .delete-option
    const deleteBtn = event.target.closest('.delete-option');
    if (deleteBtn) {
      const parentOption = deleteBtn.closest('.option');
      if (parentOption) {
        parentOption.remove();
      }
    }
  });
});
