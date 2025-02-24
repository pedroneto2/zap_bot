function addUnitListeners(ppuCount){
  for(let i = 1; i <= ppuCount; i++){
    const unitElement = document.querySelector(`#unit-ppu${i}`)
    unitElement.addEventListener('change', (e) => validateUnit(e.target))
  }
}

function addPricePerUnit(){
  const ppuContainer = document.querySelector('#ppu-product-container')
  const ppuCount = document.querySelectorAll('.ppu-product-container').length + 1

  ppuContainer.innerHTML += `
    <div class="ppu-product-container ppu-product-container-${ppuCount%2 ? 'odd' : 'even'}">
      <h3 class="ppu-product-header">Preço por Unidade ${ppuCount}</h3>
      <label for="price-ppu${ppuCount}">Preço:</label>
      <input class="input-field" id="price-ppu${ppuCount}" name="price-ppu${ppuCount}" type="number" step=".01" value="0"><br><br>
      <label for="unit-ppu${ppuCount}">Unidade:</label>
      <input class="input-field" id="unit-ppu${ppuCount}" name="unit-ppu${ppuCount}" type="text"><br><br>
    </div>
  `

  const newUnitElement = document.querySelector(`#unit-ppu${ppuCount}`)

  newUnitElement.addEventListener('change', (e) => validateUnit(e.target))

  const ppuProductAmountElement = document.querySelector('#ppu-product-amount')
  ppuProductAmountElement.value = ppuCount
}

function validateUnit(target){
  target.value = target.value.replace(/[^a-z]/gi, '')
}