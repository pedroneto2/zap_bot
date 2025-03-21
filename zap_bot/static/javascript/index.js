window.onload = goToTop

function goToTop(){
  scrollTo({ top: 0, left: 0, behavior: 'smooth' })
}

function addNewOrder(access_token) {
  const cName = document.querySelector('#cname').value
  const cPhone = document.querySelector('#cphone').value
  const cAddress = document.querySelector('#caddress').value

  const xhttp = new XMLHttpRequest()
  xhttp.onload = (data) => parseRequestResponse(data.target.response, 'Novo pedido adicionado!')
  xhttp.open("POST", `orders/new?cname=${cName}&cphone=${cPhone}&caddress=${cAddress}&access_token=${access_token}`)
  xhttp.send()
}

function loadTableAndPaginator(data, perPage, dataLength, access_token) {
  loadTable(data, access_token)
  loadPaginator(dataLength, perPage)
}

function loadTable(data, access_token){
  const table = document.querySelector('#orders-table')

  data.forEach((order, index) => {
    table.innerHTML += `
      <tr style="background: ${index%2 ? '#ddd' : '#fff'}">
        <td style="font-weight: bold; font-size: large">${order.id}</td>
        <td>${order.customer_name}</td>
        <td>${formatPhone(order.customer_phone)}</td>
        <td>${order.customer_address}</td>
        <td>${order.customer_products.map((product, index) => `
            <div class='product-container ${index%2 ? 'product-container-odd' : 'product-container-even'}'>
              <p class="product-header">Produto ${index + 1}</p>
              <hr>
              <p><span class="product-description">codigo: </span><span>${product.id}</span></p>
              <p><span class="product-description">nome: </span><span>${product.name}</span></p>
              <p><span class="product-description">preço/un: </span><span>${product.price_per_unit}</span></p>
              <p><span class="product-description">quantidade: </span><span>${product.quantity}</span></p>
            </div>`).join('')}
        </td>
        <td>${order.total_price}</td>
        <td>${order.created_at}</td>
        <td>
            <button onclick="deleteOrder(${order.id}, '${access_token}')">Deletar</button>
            <button onclick="editOrder(${order.id})">Editar</button>
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

function deleteOrder(orderId, access_token){
  if (confirm("Você tem certeza?") == true) {
    const xhttp = new XMLHttpRequest()
    xhttp.onload = (data) => parseRequestResponse(data.target.response, 'Pedido deletado!')
    xhttp.open("DELETE", `orders/delete?id=${orderId}&access_token=${access_token}`)
    xhttp.send()
  }
}

function editOrder(orderId){
  window.location.href = `orders/edit/${orderId}`
}

function formatPhone(phone){
  return `+${phone.slice(0, 2)} (${phone.slice(2, 4)})${phone.slice(5, phone.length)}`
}

function loadPaginator(dataLength, per_page){
  if(typeof dataLength == 'object'){
    return
  }

  const params = new URLSearchParams(document.location.search)
  const currentPage = +params.get('page') || 1
  const table = document.querySelector('#paginator-container')

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