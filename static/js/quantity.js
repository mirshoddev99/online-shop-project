function decrementQuantity() {
  var inputElement = document.querySelector('input[name="num-product"]');
  var currentQuantity = parseInt(inputElement.value);

  if (currentQuantity > 1) {
    inputElement.value = currentQuantity - 1;
  }
}

function incrementQuantity() {
  var inputElement = document.querySelector('input[name="num-product"]');
  var currentQuantity = parseInt(inputElement.value);

  if (currentQuantity < 10) {
    inputElement.value = currentQuantity + 1;
  }
}

function getQuantity() {
  var inputElement = document.querySelector('input[name="num-product"]');
  var quantity = inputElement.value;
  console.log(quantity);
}


console.log("Hi");
