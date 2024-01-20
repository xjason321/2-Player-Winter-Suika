from PIL import Image

listOfFruits = ["blueberry", "raspberry", "grapes", "banana", "orange", "apple", "lemon", "pomegranate", "plum", "melon"] # i removed the pineapple lol

def convert_to_grayscale(input_path, output_path):
    # Open the image file
    original_image = Image.open(input_path)

    # Convert the image to grayscale
    grayscale_image = original_image.convert("LA")

    # Save the grayscale image
    grayscale_image.save(output_path)


for fruit in listOfFruits:
    # Replace 'input.png' with the path to your PNG file
    input_path = f'blits/{fruit}.png'

    # Replace 'output_grayscale.png' with the desired output filename
    output_path = f'blits/{fruit}_grayscale.png'

    convert_to_grayscale(input_path, output_path)
