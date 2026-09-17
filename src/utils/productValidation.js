export function validateProduct(product) {
  const errors = {}
  if (!product.name?.trim()) errors.name = 'Product name is required.'
  if (!product.category?.trim()) errors.category = 'Category is required.'
  if (product.category !== 'Pizza' && (!Number.isFinite(Number(product.price)) || Number(product.price) < 0)) {
    errors.price = 'Enter a valid price.'
  }
  if (product.category === 'Pizza') {
    for (const size of ['small', 'medium', 'large']) {
      if (!Number.isFinite(Number(product.prices?.[size])) || Number(product.prices[size]) < 0) {
        errors[`${size}Price`] = `Enter a valid ${size} pizza price.`
      }
    }
  }
  return errors
}