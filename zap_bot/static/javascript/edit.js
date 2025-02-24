function createSelectListeners(orderProducts, products){
  orderProducts.forEach((orderProduct, index) =>{
    const orderProductField = document.querySelector(`#oproduct${index + 1}`)
    populateOrderProductPricesPerUnitSelects(orderProduct, products, index + 1, orderProductField)
    orderProductField.addEventListener('change', (element) => populateOrderProductPricesPerUnitSelects(orderProduct, products, index + 1, element.target))
  })
}


function populateOrderProductPricesPerUnitSelects(orderProduct, products, index, element){
  const selectField = document.querySelector(`#uprice${index}`) 

  let prices_per_unit = products[0].prices_per_unit

  if(element.value){
    const elementValue = JSON.parse(element.value.replace(/'/g, '"'))
    prices_per_unit = products.find(product => product.id == elementValue.id).prices_per_unit
  }

  selectField.innerHTML = ''

  prices_per_unit.forEach((price_per_unit, index) => {
    selected = orderProduct ? price_per_unit == orderProduct.price_per_unit : index == 0

    selectField.innerHTML += `
      <option value="${price_per_unit}" ${selected ? 'selected' : ''}>${price_per_unit}</option>
    `
  })
}


function addProduct(products){
  const orderProductContainer = document.querySelector('#order-product-container')
  const productCount = document.querySelectorAll('.product-container').length + 1

  orderProductContainer.innerHTML += `
    <div class="product-container product-container-${productCount%2 ? 'odd' : 'even'}">
      <label for="oproduct${productCount}">Produto ${productCount}:</label>
      <select class="input-field" id="oproduct${productCount}" name="oproduct${productCount}">
      ${products.map((product, index) =>
        `<option value="{ 'id': ${product.id}, 'name': '${product.name}' }" ${ index == 0 ? "selected" : ''}>${product.name} (id: ${product.id})</option>`
      ).join('')}
      </select><br><br>
      <label for="uprice${productCount}">Preço/un do Produto ${productCount}:</label>
      <select class="input-field" id="uprice${productCount}" name="uprice${productCount}"></select><br><br>
      <label for="pquantity${productCount}">Quantidade do Produto${productCount}:</label>
      <input class="input-field" type="number" step=".01" id="pquantity${productCount}" name="pquantity${productCount}" value="1"><br><br>
    </div>
  `

  const newOrderProductField = document.querySelector(`#oproduct${productCount}`)

  populateOrderProductPricesPerUnitSelects(null, products, productCount, newOrderProductField)
  newOrderProductField.addEventListener('change', (e) => populateOrderProductPricesPerUnitSelects(undefined, products, productCount, e.target))

  const productAmountElement = document.querySelector('#product-amount')
  productAmountElement.value = productCount
}