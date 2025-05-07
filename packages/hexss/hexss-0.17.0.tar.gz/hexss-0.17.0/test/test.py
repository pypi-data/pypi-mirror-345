import svgwrite

# Create a new SVG canvas
dwg = svgwrite.Drawing('output.svg', profile='tiny')

# Add the base SVG
base_svg = dwg.add(dwg.g(id='base'))
base_svg.add(dwg.rect(insert=(0, 0), size=(200, 200), fill='blue'))

# Add the top SVG
top_svg = dwg.add(dwg.g(id='top'))
top_svg.add(dwg.circle(center=(100, 100), r=50, fill='red'))

# Save the combined SVG
dwg.save()