from dataclasses import dataclass
from datetime import*
from .enums import ProfileShape
from .import _common
import os
from instacerty.utils import get_save_directory

@dataclass
class Employee:
    name: str
    employee_id: str
    designation: str
    phone: str
    email: str
    department: str = None
    join_date: str =None
    profile_pic_path: str = None
    emegency_number:str=None
    blood_group:str=None


@dataclass
class CompanyInfo:
    company_name:str
    company_address:str
    company_front_logo:str=None
    company_back_logo:str=None
    company_website:str=None


class EmpCardCustomization:
    def __init__(
        self,
        profile_shape=None,
        logo_path=None,
        back_logo_path=None,
        font_paths=None,
        template_front=None,
        template_back=None,
        display_elements=None,
        output_directory= None
    ):
        # Default paths for fonts and templates
        # You can change these paths to your actual font and template paths
        # or use the default ones provided here.
        # Ensure the paths are correct and accessible in your environment
        # or package them with your application.
        # Example paths are provided below, but you should replace them with your actual paths.

        # Load Different Fonts with Different Sizes

        #Default assets Paths
        default_template_front =  _common.DEFAULT_FRONT_TEMPLATES[1] if profile_shape==ProfileShape.ROUNDED.value else _common.DEFAULT_FRONT_TEMPLATES[2] if profile_shape==ProfileShape.SQUARE.value else _common.DEFAULT_FRONT_TEMPLATES[0] #DEFAULT_TEMPLATE_FRONT
        default_template_back =  _common.DEFAULT_TEMPLATE_BACK
        default_logo = _common.LOGO_PATH
        default_back_logo = _common.COMPANY_LOGO_BACK_PATH

        self.profile_shape = self.__get_profile_shape(profile_shape)
        self.logo_path =self.__validate_path(logo_path,"logo" ,default_logo)
        self.back_logo_path = self.__validate_path(back_logo_path,"back_logo", default_back_logo)
        self.font_paths = self.__validate_custom_fonts_path(font_paths,self.__load_default_fonts())
        self.template_front = self.__validate_path(template_front,"front_template",default_template_front)
        self.template_back = self.__validate_path(template_back,"back_template",default_template_back)
        self.display_elements = self.__load_display_elements(display_elements)
        self.output_directory = self.__set_output_directory(output_directory)


    def __get_profile_shape(self,user_input: str) -> ProfileShape:
        try:
            if user_input is None or user_input == "":
                return ProfileShape.CIRCLE
            else:
                for shape in ProfileShape:
                    if user_input.lower() == shape.value:
                        return shape
                else:
                    return ProfileShape.CIRCLE
        except ValueError:
            return ProfileShape.CIRCLE
        
    # Load Different Fonts
    def __load_default_fonts(self):
        return {
            "font_bold": os.path.join(_common.DEFAULT_FONTS_PATH, "Roboto-Bold.ttf"),
            "font_regular": os.path.join(_common.DEFAULT_FONTS_PATH, "Roboto-Regular.ttf"),
            "font_medium": os.path.join(_common.DEFAULT_FONTS_PATH, "Roboto-Medium.ttf"),
            "font_light": os.path.join(_common.DEFAULT_FONTS_PATH, "Roboto-Light.ttf"),
        }
    

    def __load_display_elements(self, user_display_elements: dict[str, bool] | None) -> dict[str, bool]:
        default_display = self.__load_default_display_elements()
        user_display = user_display_elements 
        if not isinstance(user_display, dict):
            user_display = {}

        return {key: user_display.get(key, default_display[key]) for key in default_display}



    def __load_default_display_elements(self):
        return {
            "front_logo": True,
            "back_logo": True,
            "front_template": True,
            "back_template": True,
            "barcode": True,
            "company_website": True,
        }
    

    def __validate_path(self,path: str, file_type: str = "file", default_path: str = None) -> str:
        """
        Validates whether a path exists. Returns the path if valid.
        If not valid and `required` is True, raises an error.
        If not valid and `required` is False, returns default_path.
        """
        if path and os.path.exists(path):
            return path
        # if required:
        #     raise FileNotFoundError(f"{file_type.capitalize()} path does not exist: {path}")
        else:
            if default_path and os.path.exists(default_path):
                # print(f"Warning: {file_type.capitalize()} path '{path}' is invalid. Using default: {default_path}")
                return default_path

        raise FileNotFoundError(f"{file_type.capitalize()} path '{path}' is invalid and no default provided.")


    def __validate_custom_fonts_path(self,font_paths: dict[str, str] | None, default_font_paths: dict[str, str]) -> dict[str, str]:
        """
        Validates that all 4 custom font paths exist. 
        If font_paths is None or any font path is invalid, returns default font paths.
        """
        required_keys = {"font_regular", "font_medium", "font_light", "font_bold"}

        if not font_paths or not isinstance(font_paths, dict):
            # print("[WARNING] Custom font paths not provided or invalid. Using default fonts.")
            return default_font_paths

        if not required_keys.issubset(font_paths.keys()):
            # print("[WARNING] One or more required font keys are missing. Using default fonts.")
            return default_font_paths

        for key in required_keys:
            path = font_paths.get(key)
            if not path or not os.path.isfile(path):
                # print(f"[WARNING] Font file not found for '{key}': {path}")
                return default_font_paths

        # print("[INFO] All custom font paths are valid.")
        return font_paths
    
    def __set_output_directory(self, custom_directory: str = None) -> str:
        custom_dir = custom_directory
        if custom_dir:
            if not os.path.exists(custom_dir):
                os.makedirs(custom_dir)
                # print(f"[INFO] Created custom output directory: {custom_dir}")
            return custom_dir
        else:
            if not os.path.exists(get_save_directory()):
                os.makedirs(get_save_directory())
            return get_save_directory()
        
