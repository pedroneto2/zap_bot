function addNewProduct(access_token) {
  const productName = document.querySelector('#pname').value

  const xhttp = new XMLHttpRequest()
  xhttp.onload = (data) => parseRequestResponse(data.target.response, 'Novo produto adicionado!')
  xhttp.open("POST", `products/new?pname=${productName}&access_token=${access_token}`)
  xhttp.send()
}


function loadTableAndPaginator(data, perPage, dataLength, access_token) {
  loadTable(data, access_token)
  loadPaginator(dataLength, perPage)
}

function loadTable(data, access_token){
  const table = document.querySelector('#products-table')

  data.forEach((product, index) => {
    table.innerHTML += `
      <tr style="background: ${index%2 ? '#ddd' : '#fff'}">
        <td style="font-weight: bold; font-size: large">${product.id}</td>
        <td>${product.name}</td>
        <td>${product.prices_per_unit.map(unit => `<p class="product-unit">${unit}</p>`).join('')}</td>
        <td>${product.created_at}</td>
        <td>
            <button onclick="deleteProduct(${product.id}, '${access_token}')">Deletar</button>
            <button onclick="editProduct(${product.id})">Editar</button>
        </td>
      </tr>
    `
  })
}

function parseRequestResponse(response, successResponse){
  parsedResponse = JSON.parse(response)

  msg = parsedResponse.success ? successResponse : `Erro: ${parsedResponse.error}`

  alert(msg)

  window.location.reload(1)
}

function deleteProduct(orderId, access_token){
  if (confirm("Você tem certeza?") == true) {
    const xhttp = new XMLHttpRequest()
    xhttp.onload = (data) => parseRequestResponse(data.target.response, 'Produto deletado!')
    xhttp.open("DELETE", `products/delete?id=${orderId}&access_token=${access_token}`)
    xhttp.send()
  }
}

function editProduct(orderId){
  window.location.href = `products/edit/${orderId}`
}

function loadPaginator(dataLength, per_page){
  if(typeof dataLength == 'object'){
    return
  }

  const params = new URLSearchParams(document.location.search)
  const currentPage = +params.get('page') || 1
  const table = document.querySelector('#product-paginator-container')

  const totalBtnCount = Math.ceil(dataLength / per_page)

  let btnCount = 5

  if(totalBtnCount > 5) { btnCount = 5 } else { btnCount = totalBtnCount }

  const beforeMidNumCount = Math.floor(btnCount / 2)

  const firstNum = Math.min(Math.max(currentPage - beforeMidNumCount, 1), totalBtnCount - btnCount + 1)

  const lastNum = Math.min(firstNum + btnCount - 1, totalBtnCount)
  
  if(firstNum > 1) {
    table.innerHTML += `<button onclick="goToPage(1)"><<</button>`
  }
  if(currentPage > 1) {
    table.innerHTML += `<button style="margin-right: 10px" onclick="goToPage(${currentPage - 1})"><</button>`
  }
  for(let num = firstNum; num <= lastNum; num++ ){
    table.innerHTML += `<button class="${ num == currentPage ? 'active-page' : '' }" onclick="goToPage(${num})">${num}</button>`
  }
  if(currentPage < totalBtnCount) {
    table.innerHTML += `<button style="margin-left: 10px" onclick="goToPage(${currentPage + 1})">></button>`
  }
  if(lastNum < totalBtnCount) {
    table.innerHTML += `<button onclick="goToPage(${totalBtnCount})">>></button>`
  }
}

function goToPage(num){
  window.location.href = `?page=${num}`
}