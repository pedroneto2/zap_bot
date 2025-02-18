window.addEventListener('load', function () {
  const table = document.querySelector('#orders-table')

  loadOrders()

  function loadTableWithOrders() {
    const data = JSON.parse(this.responseText)

    data.reverse().forEach((order, index) => {
      table.innerHTML += `
        <tr style="background: ${index%2 ? '#ddd' : '#fff'}">
          <td style="font-weight: bold; font-size: large">${order.id}</td>
          <td>${order.customer_name}</td>
          <td>${order.customer_phone}</td>
          <td>${order.customer_address}</td>
          <td>${order.items.map((item, index) => `
              <div style="margin: 5px;padding: 2px;text-align: left; background: ${index%2 ? '#b1c4da' : '#9eaec2'}">
                <p style="text-align: center; font-weight: bold">Produto ${index + 1}</p>
                <p>ID do produto: ${item.product_id}</p>
                <p>Quantidade do produto: ${item.quantity}</p>
              </div>`).join('')}
          </td>
          <td>${order.total_price}</td>
          <td>${order.created_at}</td>
          <td>
              <button onclick="deleteOrder(${order.id})" style="margin-bottom: 5px; color: red">Deletar</button>
          </td>
        </tr>
      `
    })
  }

  function loadOrders() {
    const xhttp = new XMLHttpRequest()
    xhttp.onload = loadTableWithOrders
    xhttp.open("GET", "orders/get")
    xhttp.send()
  }
})

function deleteOrder(orderId){
  if (confirm("Você tem certeza?") == true) {
    const xhttp = new XMLHttpRequest()
    xhttp.open("GET", `orders/delete?id=${orderId}`)
    xhttp.send()
    alert('Pedido deletado!')
    window.location.reload(1)
  }
}

function editOrder(orderId){
  console.log(orderId + ' editada')
  window.location.reload(1)
}