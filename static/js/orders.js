function filterByCategory(categoryId) {
  const productsGrid = document.getElementById('productsGrid')
  const products = productsGrid.getElementsByClassName('col-md-4')
  for (let product of products) {
    if (categoryId) {
      if (product.dataset.category === categoryId) {
        product.style.display = 'block'
      } else {
        product.style.display = 'none'
      }
    } else {
      product.style.display = 'block'
    }
  }
}

let order = {
  type: 'F',
  items: []
}

function updateOrderType(type) {
  order.type = type
  renderOrder()
}

function addToOrder(productId, productName) {
  order.items.push({
    product: productId,
    quantity: 1,
    name: productName
  })
  renderOrder()
}

function removeFromOrder(index) {
  order.items.splice(index, 1)
  renderOrder()
}

function updateOrderJson() {
  const orderJsonPre = document.getElementById('order-json')
  const orderJsonInput = document.getElementById('order-json-input')
  const generateOrderButton = document.getElementById('generate-order-button')
  const orderJson = JSON.stringify(order, null, 2)
  orderJsonPre.textContent = orderJson
  orderJsonInput.value = orderJson
  generateOrderButton.disabled = order.items.length === 0
}

window.copyPreContentToHiddenInput = function () {
  orderJsonInput.value = orderJsonPre.textContent
}

function renderOrder() {
  const orderItemsList = document.getElementById('order-items')
  orderItemsList.innerHTML = ''
  order.items.forEach((item, index) => {
    const listItem = document.createElement('li')
    listItem.className = 'list-group-item'

    const row = document.createElement('div')
    row.className = 'row'

    const nameCol = document.createElement('div')
    nameCol.className = 'col-md-4'
    nameCol.textContent = item.name
    row.appendChild(nameCol)

    const quantityCol = document.createElement('div')
    quantityCol.className = 'col-md-4'
    const quantityInput = document.createElement('input')
    quantityInput.type = 'number'
    quantityInput.className = 'form-control'
    quantityInput.value = item.quantity
    quantityInput.min = 1
    quantityInput.onchange = (e) => {
      item.quantity = parseInt(e.target.value)
      renderOrder()
    }
    quantityCol.appendChild(quantityInput)
    row.appendChild(quantityCol)

    const buttonCol = document.createElement('div')
    buttonCol.className = 'col-md-4'
    const removeButton = document.createElement('button')
    removeButton.innerHTML = '<i class="fas fa-trash-alt"></i>'
    removeButton.className = 'btn btn-danger btn-sm ml-2'
    removeButton.onclick = () => removeFromOrder(index)
    const commentButton = document.createElement('button')
    commentButton.innerHTML = '<i class="fas fa-comment"></i>'
    commentButton.className = 'btn btn-secondary btn-sm ml-2'
    commentButton.onclick = () => {
      const comment = prompt('Ingrese su comentario:')
      if (comment) {
        item.description = comment
        renderOrder()
      }
    }
    buttonCol.appendChild(removeButton)
    buttonCol.appendChild(commentButton)
    row.appendChild(buttonCol)

    listItem.appendChild(row)

    if (item.description) {
      const commentRow = document.createElement('div')
      commentRow.className = 'row mt-2'
      const commentCol = document.createElement('div')
      commentCol.className = 'col-md-12'
      commentCol.textContent = `Comentario: ${item.description}`
      commentRow.appendChild(commentCol)
      listItem.appendChild(commentRow)
    }

    orderItemsList.appendChild(listItem)
  })
  updateOrderJson()
}
