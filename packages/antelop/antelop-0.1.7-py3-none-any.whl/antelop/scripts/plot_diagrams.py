import datajoint as dj
from antelop.schemas import session, ephys, behaviour
from antelop.connection.connect import dbconnect
from PIL import Image, ImageOps, ImageFilter


# import schemas
conn = dbconnect()
session_tables, session_schema = session.schema(conn)
ephys_tables, ephys_schema = ephys.schema(conn)
behaviour_tables, behaviour_schema = behaviour.schema(conn)

for key, DigitalEvents in session_tables.items():
    globals()[key] = DigitalEvents

for key, DigitalEvents in ephys_tables.items():
    globals()[key] = DigitalEvents

for key, DigitalEvents in behaviour_tables.items():
    globals()[key] = DigitalEvents

# plot various diagrams
(dj.Diagram(session_schema)).save("resources/session.png")

(dj.Diagram(session_schema) + dj.Diagram(ephys_schema)).save("resources/ephys.png")

(dj.Diagram(session_schema) + dj.Diagram(behaviour_schema)).save(
    "resources/behaviour.png"
)


# function to remove white background from the images and reshape
def remove_white_background(
    image_path, output_path, target_size, tolerance, radius, target_colour
):
    # Open the image
    img = Image.open(image_path)

    # Convert to RGBA mode if not already
    img = img.convert("RGBA")

    # Get the image data
    img_data = img.getdata()

    # Remove white pixels
    new_data = []
    for item in img_data:
        # Check if the pixel is white or near white within the defined tolerance
        if all(abs(channel - 255) <= tolerance for channel in item[:3]):
            # Set alpha to 0 for white pixels
            new_data.append(target_colour + (item[3],))
        else:
            new_data.append(item)

    # Update image with new data
    img.putdata(new_data)
    if radius != None:
        # Create a mask to identify boundary pixels
        boundary_mask = Image.new("L", img.size, 0)
        for x in range(img.width):
            for y in range(img.height):
                pixel = img.getpixel((x, y))
                if pixel[3] == 0:  # Transparent pixel
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < img.width and 0 <= ny < img.height:
                                neighbor_pixel = img.getpixel((nx, ny))
                                if neighbor_pixel[3] != 0:  # Non-transparent neighbor
                                    boundary_mask.putpixel((x, y), 255)
                                    break

        # Apply Gaussian blur to boundary pixels
        blurred_boundary_mask = boundary_mask.filter(
            ImageFilter.GaussianBlur(radius=radius)
        )  # Adjust radius as needed

        # Apply blur only to boundary pixels
        blurred_img = img.copy()
        for x in range(img.width):
            for y in range(img.height):
                if blurred_boundary_mask.getpixel((x, y)) > 0:
                    blurred_img.putpixel((x, y), (255, 255, 255, 0))  # Set alpha to 0

        img = blurred_img.copy()

    # Pad the image to the target size
    img = img.resize(target_size)
    padded_img = ImageOps.expand(img, border=(300, 200), fill=target_colour)

    # Save the new image
    padded_img.save(output_path, "PNG")


# remove white background from the images
target_size = (400, 600)
tolerance = 0
target_colour = (29, 34, 41)
remove_white_background(
    "resources/session.png",
    "resources/session.png",
    (200, 300),
    tolerance,
    radius=None,
    target_colour=target_colour,
)
remove_white_background(
    "resources/ephys.png",
    "resources/ephys.png",
    target_size,
    tolerance,
    radius=None,
    target_colour=target_colour,
)
remove_white_background(
    "resources/behaviour.png",
    "resources/behaviour.png",
    target_size,
    tolerance,
    radius=None,
    target_colour=target_colour,
)
