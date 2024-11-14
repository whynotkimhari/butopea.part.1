import sys
from db import fetch
from my_xml import gen

def main():

  if len(sys.argv) < 3:
    print("Usage: python ./main.py <db_path> <out_path> <pretty print: True/False (optional)>")
    sys.exit(1)
  
  if len(sys.argv) > 3 and sys.argv[3].lower() not in ['true', 'false']:
    print("pretty print must be either true or false!")
    sys.exit(1)

  DB_PATH = sys.argv[1]
  OUT_PATH = sys.argv[2]
  PPRINT = sys.argv[3].lower() == 'true'

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
      'new' AS condition,

      pi.product_image_id AS pi_id
      
    FROM 
      product p, 
      product_description pd, 
      product_image pi, 
      manufacturer m
      
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

  products = fetch(DB_PATH, QUERY)

  for product in products:
    # Additional images must be loaded in their respective sort orders
    # Submit up to 10 additional product images by including this attribute multiple times.
    product['additional_image_links'] = list(
      map(lambda row: row['additional_image_link'], fetch(
      DB_PATH, 
      query=f"""
        SELECT 
          CONCAT('https://butopea.com/', image) AS additional_image_link, 
          sort_order 
        FROM product_image 
        WHERE 
          product_id = '{product["id"]}' AND
          product_image_id != '{product["pi_id"]}'
        ORDER BY 2 ASC
        LIMIT 10;
      """
      ))
    )

    # We won't use this in XML file
    del product["pi_id"]

  gen(products, out_path=OUT_PATH, pprint=PPRINT)

if __name__ == '__main__':
  main()