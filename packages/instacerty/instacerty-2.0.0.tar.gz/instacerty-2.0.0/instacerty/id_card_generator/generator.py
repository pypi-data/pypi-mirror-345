from PIL import Image, ImageDraw, ImageFont
from ._common import PROFILE_PIC_PATH
import barcode
from barcode.writer import ImageWriter
from .enums import ProfileShape
import os
from datetime import *
from .employee_card import Employee, CompanyInfo, EmpCardCustomization

class EmployeeIDCardGenerator:
    def __init__(self, employee: Employee, company:CompanyInfo,customization: EmpCardCustomization = None):
        self.employee = employee
        self.company=company
        self.customization = customization if customization else EmpCardCustomization()
        self.fonts={
            "font_large": ImageFont.truetype(self.customization.font_paths["font_bold"], 45),
            "font_medium": ImageFont.truetype(self.customization.font_paths["font_regular"], 28),
            "font_small": ImageFont.truetype(self.customization.font_paths["font_light"], 20),
            "company_name_font": ImageFont.truetype(self.customization.font_paths["font_medium"], 40),
            "company_address_font": ImageFont.truetype(self.customization.font_paths["font_light"], 30),
            "label_font": ImageFont.truetype(self.customization.font_paths["font_regular"], 20),
            "value_font": ImageFont.truetype(self.customization.font_paths["font_regular"], 30),
        }
    

    def __resize_background(self,background, card_size):
        """Resize background image to fit the card size exactly."""
        return background.resize(card_size, Image.Resampling.LANCZOS)


    # def center_text(self,draw, text, font, card_width, y_position, fill="black"):
    #     """Center the text horizontally and return the X position."""
    #     #text_width, text_height = draw.textsize(text, font=font)
    #     bbox = draw.textbbox((0, 0), text, font=font)  # ✅ Correct way in Pillow 10+
    #     text_width = bbox[2] - bbox[0]  # Width
    #     text_height = bbox[3] - bbox[1]  # Height
    #     x_position = (card_width - text_width) // 2  # Center horizontally
    #     draw.text((x_position, y_position), text, font=font, fill=fill)
    #     return x_position  # Return the X coordinate for left alignment


    def __profile_picture_shape(self,image, shape="circle"):
        """Convert a profile picture into a specific shape (circle or square)."""
        if shape == ProfileShape.CIRCLE.value:
            return self.__make_circle(image)
        elif shape == ProfileShape.ROUNDED.value:
            return self.__make_rounded_rectangle(image, radius=20)
        elif shape == ProfileShape.SQUARE.value:
            return self.__make_square(image)
        else:
            raise ValueError("Shape must be 'circle' or 'square'")



    def __make_circle(self,image):
        """Convert a profile picture into a circular image with transparency."""
        size = min(image.size)  # Get smallest dimension
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)

        circular_img = image.resize((size, size), Image.Resampling.LANCZOS)
        circular_img.putalpha(mask)  # Apply mask to make circular

        return circular_img


    def __make_square(self,image):
        """Convert a profile picture into a square image with transparency."""
        size = min(image.size)  # Get smallest dimension
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rectangle((0, 0, size, size), fill=255)

        circular_img = image.resize((size, size), Image.Resampling.LANCZOS)
        circular_img.putalpha(mask)  # Apply mask to make circular

        return circular_img


    def __make_rounded_rectangle(self,image, radius=20):
        """Convert an image into a rounded rectangle shape."""
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius=radius, fill=255)
        rounded_img = image.copy()
        rounded_img.putalpha(mask)  # Apply mask

        return rounded_img

    def __split_address(self,address):
        """Splits an address into multiple lines based on commas."""
        return [line.strip() for line in address.split(";")]


    def __draw_address(self,draw, address, start_x, start_y, font, line_spacing=5):
        """Draws the formatted address on the ID card."""
        address_lines = self.__split_address(address)  # Format address into lines
        y = start_y
        count=0

        for index, line in enumerate(address_lines):
            bbox = draw.textbbox((0, 0), line, font=self.fonts["company_name_font"] if index == 0 else font)  
            line_height = bbox[3] - bbox[1]  # Calculate text height
            
            # Use a different font for the first line (Company Name)
            draw.text((start_x, y), line, fill="black", font=self.fonts["company_name_font"] if index == 0 else font)  
            
            # Apply extra spacing only after the first line (Company Name)
            y += line_height + (10 if index == 0 else line_spacing)


    def __draw_multiple_labels(self,draw, x, y, data, label_font, value_font, fill="black", label_value_spacing=8, pair_spacing=20):
        """
        Draws multiple labels with values below them with adjustable spacing.
        
        Parameters:
        - draw: ImageDraw object
        - x, y: Starting coordinates
        - data: Dictionary with labels as keys and values as values
        - label_font: Font for labels (smaller size)
        - value_font: Font for values (larger size)
        - fill: Text color
        - label_value_spacing: Space between label and value
        - pair_spacing: Space between different label-value pairs
        """

        for label, value in data.items():

            if value is not None:
                # Draw label (small text)
                draw.text((x, y), label, font=self.fonts["label_font"], fill=fill)

                # Calculate the height of label text to position the value correctly
                label_bbox = draw.textbbox((0, 0), label, font=self.fonts["label_font"])
                label_height = label_bbox[3] - label_bbox[1]

                # Draw value (big text) below the label with extra spacing
                draw.text((x, y + label_height + label_value_spacing), value, font=self.fonts["value_font"], fill=fill)

                # Calculate the height of the value text
                value_bbox = draw.textbbox((0, 0), value, font=self.fonts["value_font"])
                value_height = value_bbox[3] - value_bbox[1]

                # Move y down for the next label-value pair with extra spacing
                y += label_height + value_height + label_value_spacing + pair_spacing


    def __create_bar_code(self,employee_id):
        """Generate a barcode image for the given employee ID."""
        #BAR CODE DATA
        # Generate barcode (without numbers)
        barcode_data = employee_id  # Example employee ID used as barcode data
        barcode_obj = barcode.Code128(barcode_data, writer=ImageWriter())
        # barcode_path = os.path.join(DEFAULT_OUTPUT_DIR, "barcode")
        barcode_path = os.path.join(self.customization.output_directory, "barcode")

        barcode_obj.save(barcode_path, {"write_text": False})  # Hide numbers
        barcode_image = Image.open(f"{barcode_path}.png").convert("RGBA")

        # Resize barcode to 2-3 cm height (~60-90px)
        barcode_width = 400  # Keep barcode width large for better scanning
        barcode_height = 70  # Approximate 2-3 cm height
        barcode_image = barcode_image.resize((barcode_width, barcode_height))
        return barcode_image


    def __generate_unique_number(self):
        # # Get the current date and time
        now = datetime.now()
        number = now.strftime("%Y%m%d%H%M%S%f")  # adds microseconds
        return int(number)
    

    def generate_id_card(self):

        """Generate the ID card with front and back sides."""
        CARD_SIZE = (600, 900)  # ID Card dimensions

        idcard_name_along=self.__generate_unique_number()

        barcode_image = self.__create_bar_code(self.employee.employee_id)

        if self.customization.display_elements.get("front_template") and os.path.exists(self.customization.template_front):
            front_template_ = Image.open(self.customization.template_front).convert("RGBA")
            #background = Image.open("background.png")  # Load your background image
            front_template = self.__resize_background(front_template_, (600, 900))  # Resize it to fit the card
        else:
            front_template = Image.new("RGBA", CARD_SIZE, "white")  # White background


        if self.customization.display_elements.get("back_template") and os.path.exists(self.customization.template_back):
            back_template_ = Image.open(self.customization.template_back).convert("RGBA")
            back_template = self.__resize_background(back_template_, (600, 900))  # Resize it to fit the card
        else:
            back_template = Image.new("RGBA", CARD_SIZE, "white")  # White background


        # Load company logo (with transparency handling)
        if self.customization.display_elements.get("front_logo") and os.path.exists(self.customization.logo_path):
            logo = Image.open(self.customization.logo_path).convert("RGBA")
            logo = logo.resize((100, 100))  # Resize logo if needed
        else:
            logo = None  # No logo available


        if self.customization.display_elements.get("back_logo") and os.path.exists(self.customization.back_logo_path):
            b_logo = Image.open(self.customization.back_logo_path).convert("RGBA")
            b_logo = b_logo.resize((100, 100))  # Resize logo if needed
            back_logo=b_logo.resize((150, 150))
        else:
            back_logo=None

        # Load profile picture (with transparency handling)
        if self.employee.profile_pic_path is not None:
            if os.path.exists(self.employee.profile_pic_path):
                profile_pic = Image.open(self.employee.profile_pic_path).convert("RGBA")
                profile_pic = profile_pic.resize((300, 300))  # Profile pic size
        else: # No profile pic available
            profile_pic = Image.open(PROFILE_PIC_PATH ).convert("RGBA")
            profile_pic = profile_pic.resize((300, 300))

        #get center position
        bar_img_width, bar_img_height = barcode_image.size
        x_position = (CARD_SIZE[0] - CARD_SIZE[1]) // 2

        bar_img_width, bar_img_height = barcode_image.size
        barc_x_position = (CARD_SIZE[0] - bar_img_width) // 2


        #===========================================================================
        # Draw on the front side
        #===========================================================================
        front_draw = ImageDraw.Draw(front_template)

        # Paste company logo (top)
        if logo:
            front_template.paste(logo, (50, 50), logo.split()[3])  # Paste logo with transparency

        # Paste profile picture (centered on card)
        if profile_pic:
            profile_img_width, profile_img_height = profile_pic.size
            profile_pic = self.__profile_picture_shape(profile_pic, shape=self.customization.profile_shape.value)  # Convert to circle or square
            profile_x_position = (CARD_SIZE[0] - profile_img_width) // 2
            front_template.paste(profile_pic, (profile_x_position, 138), profile_pic.split()[3])  # Centered below logo


        #---------------------------------------------------------------------------
        # Employee details
        #----------------------------------------------------------------------------

        # front_draw.text((170, 480), self.employee.name, font=font_large, fill="black")
        front_draw.text((170, 480), self.employee.name, font=self.fonts["font_large"], fill="black")
        front_draw.text((170, 535), self.employee.designation, font=self.fonts["font_medium"], fill="black")
        front_draw.text((170, 580), f"Employee ID: {self.employee.employee_id}", font=self.fonts["font_small"], fill="black")
        front_draw.text((170, 620), f"Phone: {self.employee.phone}", font=self.fonts["font_small"], fill="black")
        front_draw.text((170, 660), f"Email: {self.employee.email}", font=self.fonts["font_small"], fill="black")

        # Paste barcode on the front
        if self.customization.display_elements.get("barcode"):
            front_template.paste(barcode_image, (barc_x_position, 720), barcode_image.split()[3])  # Below details

        # Draw company website on the front side
        if self.company.company_website and self.customization.display_elements.get("company_website") :
            front_draw.text((190, 810), f"{self.company.company_website}", font=self.fonts["font_small"], fill="black")


        #=============================================================================
        # Draw on the back side
        #=============================================================================
        back_draw = ImageDraw.Draw(back_template)

        # Paste company logo on the back side (top)
        if back_logo:
            logo_img_width, logo_img_height = back_logo.size
            logo_x_position = (CARD_SIZE[0] - logo_img_width) // 2
            back_template.paste(back_logo, (logo_x_position, 90), back_logo.split()[3])

        date_info = {
            "Employee ID": self.employee.employee_id,
            "Department": self.employee.department,
            "Joined Date": self.employee.join_date, #self.employee.join_date.strftime("%d/%m/%Y") if self.employee.join_date else "N/A",
            "Emergency Number":self.employee.emegency_number,
            "Blood Group":self.employee.blood_group
        }

        self.__draw_multiple_labels(back_draw, 150, 280, date_info, self.fonts["label_font"], self.fonts["value_font"])

        self.__draw_address(back_draw, self.company.company_address, 150, 670, font=self.fonts["company_address_font"])  # Draw formatted address

        front_output_path = os.path.join(self.customization.output_directory, f"{self.employee.employee_id}_{idcard_name_along}_Front.png")
        back_output_path = os.path.join(self.customization.output_directory, f"{self.employee.employee_id}_{idcard_name_along}_Back.png")
        front_template.save(front_output_path)
        back_template.save(back_output_path)

        os.remove(f"{self.customization.output_directory}/barcode.png")  # Remove barcode image after saving

        return front_output_path, back_output_path


