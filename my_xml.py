import xml.etree.ElementTree as ET
import xml.dom.minidom

def gen(products: list[dict[str, str | list[str]]], out_path: str, pprint=False) -> None:
  """
    Generate the feed.xml file with given list of product to the given path.
    Follow the format [RSS 2.0 specification](https://support.google.com/merchants/answer/14987622?hl=en&ref_topic=14963864&sjid=2492092616701478416-EU).
    You may choose to have nice format too.

    products: the list of product

    out_path: output path

    pprint: print in nice format if True
  """
  rss = ET.Element("rss", attrib={"xmlns:g": "http://base.google.com/ns/1.0", "version": "2.0"})
  channel = ET.SubElement(rss, "channel")

  title = ET.SubElement(channel, "title")
  title.text = "Butopêa"
  link = ET.SubElement(channel, "link")
  link.text = "https://butopea.com/"
  description = ET.SubElement(channel, "description")
  description.text = "Hi, my name is Butopêa!"

  for product in products:
    item = ET.SubElement(channel, "item")
    for tag, info in product.items():

      # info here is a list
      if tag == 'additional_image_links':
        for img in info:

          # 'additional_image_links' -> 'g:additional_image_link'
          elem = ET.SubElement(item, f'g:{tag}'[:-1])
          elem.text = img
      
      # simply a str
      else:

        # 'tag' -> 'g:tag'
        elem = ET.SubElement(item, f'g:{tag}')
        elem.text = info

  # Print in compact format
  if not pprint:
    tree = ET.ElementTree(rss)
    with open(out_path, "wb") as file:
      tree.write(file, encoding="utf-8", xml_declaration=True)
  
  # Pretty print
  else:
    rough_string = ET.tostring(rss, 'utf-8')
    parsed = xml.dom.minidom.parseString(rough_string)
    pretty_xml = parsed.toprettyxml(indent="  ")

    # Save pretty XML to a file
    with open(out_path, "w", encoding="utf-8") as file:
      file.write(pretty_xml)