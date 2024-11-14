from db import fetch
from my_xml import gen

def main():

  DB_PATH = './data.sqlite'

  # I think these are important ones:
    # Disabled products (with status 0) must not be included in the feed
    # All prices are in Hungarian Forints (HUF)
    # Brand represents the product manufacturer
    # All products are sold as new
    # The base domain for product image URLs is butopea.com

  # The others from Google Merchant product data specifications that I think the db satisfy already:
    # LENGTH(id) <= 50
    # LENGTH(title) <= 150
    # LENGTH(description) <= 5000
    # LENGTH(brand) <= 70
  QUERY = """
    SELECT
      p.product_id AS id,
      pd.name AS title,
      pd.description AS description,
      CONCAT('https://butopea.com/p/', p.product_id) AS link,
      CONCAT('https://butopea.com/', pi.image) AS image_link,
      CASE
        WHEN p.quantity > 0 
          THEN 'in_stock' 
        ELSE 'out_of_stock'
      END AS availability,
      CONCAT(price, ' HUF') AS price,
      m.name AS brand,
      'new' AS condition
    FROM product p, product_description pd, product_image pi, manufacturer m
    WHERE
      p.manufacturer_id = m.manufacturer_id AND
      p.product_id = pd.product_id AND
      p.product_id = pi.product_id AND

      LENGTH(p.product_id) <= 50 AND
      LENGTH(pd.name) <= 150 AND
      LENGTH(pd.description) <= 5000 AND
      p.status != 0 AND
      p.price != 0 AND
      LENGTH(m.name) <= 70;
  """

  results = fetch(DB_PATH, QUERY)

  products = []

  for result in results:
    product = {
      "id":                     result[0],
      "title":                  result[1],
      "description":            result[2],
      "link":                   result[3],
      "image_link":             result[4],
      "additional_image_links": [],
      "availability":           result[5],
      "price":                  result[6],
      "brand":                  result[7],
      "condition":              result[8],
    }
    
    # Additional images must be loaded in their respective sort orders
    # Submit up to 10 additional product images by including this attribute multiple times.
    product['additional_image_links'] = list(map(lambda z: z[0], fetch(
      DB_PATH, 
      query=f"""
        SELECT image, sort_order 
        FROM product_image 
        WHERE product_id = '{product["id"]}'
        ORDER BY 2 ASC
        LIMIT 10;
      """
    )))

    products.append(product)

  gen(products, out_path='./feed.xml', pprint=True)

if __name__ == '__main__':
  main()