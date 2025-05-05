"""
Utility functions and constants for Colab Print library.

This module provides utility functions, data classes, and constants used throughout
the Colab Print library. It includes helper functions for environment detection,
animation processing, and data validation, as well as predefined styles and themes
for consistent styling across the library.

The module includes:
- Data classes for parameter organization (DFDisplayParams, TableDisplayParams)
- Constants for styling (DEFAULT_THEMES, SPECIAL_STYLES, VALID_ANIMATIONS)
- Utility functions for environment detection (is_in_notebook)
- Animation processing helpers (process_animation_class)
- Data type validation helpers (df_like, array_like)

These utilities provide the foundation for the library's functionality and ensure
consistent behavior across different display components.

Example:
    ```python
    from colab_print.utilities import process_animation_class, is_in_notebook, DFDisplayParams
    
    # Check if running in a notebook environment
    if is_in_notebook():
        # Process an animation name into a valid CSS class
        animation_class = process_animation_class("fadeIn")
        # animation_class -> "animate__animated animate__fadeIn"
        
        # Create display parameters for a DataFrame
        params = DFDisplayParams(
            style="default",
            max_rows=20,
            highlight_cols=["important_column"],
            caption="Dataset Overview"
        )
    ```
"""

from dataclasses import dataclass
from typing import Optional, Union, List, Dict

from colab_print.exception import AnimationError

__all__ = [
    # Classes
    "DFDisplayParams",
    "TableDisplayParams",

    # Functions
    "is_in_notebook",
    "process_animation_class",

    # Variables
    "DEFAULT_THEMES",
    "SPECIAL_STYLES",
    "VALID_ANIMATIONS",
]


@dataclass
class DFDisplayParams:
    """Parameters for DataFrame display styling."""
    style: str = 'default'
    max_rows: Optional[int] = None
    max_cols: Optional[int] = None
    precision: int = 2
    header_style: Optional[str] = None
    odd_row_style: Optional[str] = None
    even_row_style: Optional[str] = None
    index: bool = True
    width: str = '100%'
    caption: Optional[str] = None
    highlight_cols: Optional[Union[List, Dict]] = None
    highlight_rows: Optional[Union[List, Dict]] = None
    highlight_cells: Optional[Dict] = None


@dataclass
class TableDisplayParams:
    """Parameters for table display styling."""
    style: str = 'default'
    width: str = '100%'
    header_style: Optional[str] = None
    row_style: Optional[str] = None
    caption: Optional[str] = None


VALID_ANIMATIONS = [
    # Attention seekers
    'bounce', 'flash', 'pulse', 'rubberBand', 'shakeX', 'shakeY', 'headShake',
    'swing', 'tada', 'wobble', 'jello', 'heartBeat',

    # Back entrances
    'backInDown', 'backInLeft', 'backInRight', 'backInUp',

    # Back exits
    'backOutDown', 'backOutLeft', 'backOutRight', 'backOutUp',

    # Bouncing entrances
    'bounceIn', 'bounceInDown', 'bounceInLeft', 'bounceInRight', 'bounceInUp',

    # Bouncing exits
    'bounceOut', 'bounceOutDown', 'bounceOutLeft', 'bounceOutRight', 'bounceOutUp',

    # Fading entrances
    'fadeIn', 'fadeInDown', 'fadeInDownBig', 'fadeInLeft', 'fadeInLeftBig',
    'fadeInRight', 'fadeInRightBig', 'fadeInUp', 'fadeInUpBig',
    'fadeInTopLeft', 'fadeInTopRight', 'fadeInBottomLeft', 'fadeInBottomRight',

    # Fading exits
    'fadeOut', 'fadeOutDown', 'fadeOutDownBig', 'fadeOutLeft', 'fadeOutLeftBig',
    'fadeOutRight', 'fadeOutRightBig', 'fadeOutUp', 'fadeOutUpBig',
    'fadeOutTopLeft', 'fadeOutTopRight', 'fadeOutBottomLeft', 'fadeOutBottomRight',

    # Flippers
    'flip', 'flipInX', 'flipInY', 'flipOutX', 'flipOutY',

    # Lightspeed
    'lightSpeedInRight', 'lightSpeedInLeft', 'lightSpeedOutRight', 'lightSpeedOutLeft',

    # Rotating entrances
    'rotateIn', 'rotateInDownLeft', 'rotateInDownRight', 'rotateInUpLeft', 'rotateInUpRight',

    # Rotating exits
    'rotateOut', 'rotateOutDownLeft', 'rotateOutDownRight', 'rotateOutUpLeft', 'rotateOutUpRight',

    # Sliding entrances
    'slideInDown', 'slideInLeft', 'slideInRight', 'slideInUp',

    # Sliding exits
    'slideOutDown', 'slideOutLeft', 'slideOutRight', 'slideOutUp',

    # Zooming entrances
    'zoomIn', 'zoomInDown', 'zoomInLeft', 'zoomInRight', 'zoomInUp',

    # Zooming exits
    'zoomOut', 'zoomOutDown', 'zoomOutLeft', 'zoomOutRight', 'zoomOutUp',

    # Specials
    'hinge', 'jackInTheBox', 'rollIn', 'rollOut'
]

# Define the theme types
DEFAULT_THEMES = {
    'default': 'color: #000000; font-size: 16px; font-family: Arial, sans-serif; letter-spacing: 0.3px; line-height: 1.5; padding: 4px 6px; border-radius: 2px;',
    'highlight': 'color: #E74C3C; font-size: 18px; font-weight: 600; font-family: Arial, sans-serif; text-shadow: 1px 1px 3px rgba(231, 76, 60, 0.3); letter-spacing: 0.6px; background-color: rgba(231, 76, 60, 0.05); padding: 6px 10px; border-radius: 4px; border-left: 3px solid #E74C3C;',
    'info': 'color: #3498DB; font-size: 16px; font-style: italic; font-family: Arial, sans-serif; border-bottom: 1px dotted #3498DB; letter-spacing: 0.3px; background-color: rgba(52, 152, 219, 0.05); padding: 4px 8px; border-radius: 3px;',
    'success': 'color: #27AE60; font-size: 16px; font-weight: 600; font-family: Arial, sans-serif; text-shadow: 1px 1px 2px rgba(39, 174, 96, 0.2); letter-spacing: 0.3px; background-color: rgba(39, 174, 96, 0.05); padding: 4px 8px; border-radius: 3px; border-left: 2px solid #27AE60;',
    'warning': 'color: #F39C12; font-size: 16px; font-weight: 600; font-family: Arial, sans-serif; text-shadow: 1px 1px 2px rgba(243, 156, 18, 0.2); letter-spacing: 0.3px; background-color: rgba(243, 156, 18, 0.05); padding: 4px 8px; border-radius: 3px; border-left: 2px solid #F39C12;',
    'error': 'color: #C0392B; font-size: 16px; font-weight: 600; font-family: Arial, sans-serif; text-shadow: 1px 1px 2px rgba(192, 57, 43, 0.2); letter-spacing: 0.3px; background-color: rgba(192, 57, 43, 0.05); padding: 4px 8px; border-radius: 3px; border-left: 2px solid #C0392B;',
    'muted': 'color: #7F8C8D; font-size: 14px; font-family: Arial, sans-serif; font-style: italic; letter-spacing: 0.2px; opacity: 0.85; padding: 2px 4px;',
    'code': 'color: #2E86C1; font-size: 14px; font-family: Arial, sans-serif; background-color: rgba(46, 134, 193, 0.07); padding: 2px 6px; border-radius: 3px; border: 1px solid rgba(46, 134, 193, 0.2); letter-spacing: 0.2px;',
    'primary': 'color: #3498DB; font-size: 16px; font-weight: 600; font-family: Arial, sans-serif; letter-spacing: 0.3px; background-color: rgba(52, 152, 219, 0.08); padding: 6px 10px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);',
    'secondary': 'color: #9B59B6; font-size: 16px; font-weight: 600; font-family: Arial, sans-serif; letter-spacing: 0.3px; background-color: rgba(155, 89, 182, 0.08); padding: 6px 10px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);',
}

# Define specialized style variables for easy access
SPECIAL_STYLES = {
    'header': 'color: #1A237E; font-size: 24px; font-weight: bold; font-family: Arial, sans-serif; text-align: center; letter-spacing: 1px; padding: 16px 10px; border-top: 2px dashed #1A237E; border-bottom: 2px dashed #1A237E; margin: 30px 0; background-color: rgba(26, 35, 126, 0.05); display: block; clear: both;',

    'subheader': 'color: #283593; font-size: 20px; font-weight: bold; font-family: Arial, sans-serif; letter-spacing: 0.7px; padding: 8px 10px; border-left: 4px solid #283593; margin: 25px 0; background-color: rgba(40, 53, 147, 0.03); display: block; clear: both;',

    'title': 'color: #3F51B5; font-size: 28px; font-weight: bold; font-family: Arial, sans-serif; text-align: center; text-shadow: 1px 1px 1px rgba(63, 81, 181, 0.2); letter-spacing: 1.2px; padding: 10px; margin: 35px 0 25px 0; display: block; clear: both;',

    'subtitle': 'color: #5C6BC0; font-size: 18px; font-weight: 600; font-style: italic; font-family: Arial, sans-serif; text-align: center; letter-spacing: 0.5px; margin: 20px 0 30px 0; display: block; clear: both;',

    'code_block': 'color: #424242; font-size: 14px; font-family: Arial, sans-serif; background-color: #F5F5F5; padding: 15px; border-radius: 5px; border-left: 4px solid #9E9E9E; margin: 25px 0; overflow-x: auto; white-space: pre-wrap; display: block; clear: both;',

    'quote': 'color: #455A64; font-size: 16px; font-style: italic; font-family: Arial, sans-serif; background-color: #ECEFF1; padding: 15px 20px; border-left: 5px solid #78909C; margin: 30px 0; letter-spacing: 0.3px; line-height: 1.6; display: block; clear: both;',

    'card': 'color: #333333; font-size: 16px; font-family: Arial, sans-serif; background-color: #FFFFFF; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); margin: 30px 0; border: 1px solid #E0E0E0; display: block; clear: both;',

    'notice': 'color: #004D40; font-size: 16px; font-weight: 600; font-family: Arial, sans-serif; background-color: #E0F2F1; padding: 15px; border-radius: 5px; border: 1px solid #80CBC4; margin: 25px 0; letter-spacing: 0.2px; display: block; clear: both;',

    'badge': 'color: #FFFFFF; font-size: 12px; font-weight: bold; font-family: Arial, sans-serif; background-color: #00897B; padding: 3px 8px; border-radius: 12px; display: inline-block; letter-spacing: 0.5px; margin: 5px 5px 5px 0;',

    'footer': 'color: #757575; font-size: 13px; font-style: italic; font-family: Arial, sans-serif; text-align: center; border-top: 1px solid #E0E0E0; padding-top: 10px; margin: 35px 0 15px 0; letter-spacing: 0.3px; display: block; clear: both;',

    'data_highlight': 'color: #0D47A1; font-size: 18px; font-weight: bold; font-family: Arial, sans-serif; background-color: rgba(13, 71, 161, 0.08); padding: 5px 8px; border-radius: 4px; letter-spacing: 0.3px; text-align: center; display: block; margin: 25px 0; clear: both;',

    'section_divider': 'color: #212121; font-size: 18px; font-weight: bold; font-family: Arial, sans-serif; border-bottom: 2px solid #BDBDBD; padding-bottom: 5px; margin: 35px 0 25px 0; letter-spacing: 0.4px; display: block; clear: both;',

    'df': 'color: #000000; font-size: 14px; font-family: Arial, sans-serif; background-color: #FFFFFF; border-collapse: collapse; width: 100%; margin: 15px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);',

    'table': 'color: #0f67A9; font-size: 15px; font-family: Arial, sans-serif; width: 100%; border-collapse: collapse; margin: 15px 0; box-shadow: 0 1px 4px rgba(0,0,0,0.15); border-radius: 4px; overflow: hidden;',

    'list': 'color: #000000; font-size: 16px; font-family: Arial, sans-serif; padding-left: 20px; line-height: 1.6; margin: 25px 0; display: block; clear: both;',

    'dict': 'color: #000000; font-size: 16px; font-family: Arial, sans-serif; background-color: rgba(0,0,0,0.02); padding: 12px; border-radius: 4px; margin: 25px 0; border-left: 3px solid #607D8B; display: block; clear: both;',

    'highlight': 'color: #E74C3C; font-size: 18px; font-weight: 600; font-family: Arial, sans-serif; text-shadow: 1px 1px 3px rgba(231, 76, 60, 0.3); letter-spacing: 0.6px; background-color: rgba(231, 76, 60, 0.05); padding: 6px 10px; border-radius: 4px; border-left: 3px solid #E74C3C; display: block; margin: 25px 0; clear: both;',

    'info': 'color: #3498DB; font-size: 16px; font-style: italic; font-family: Arial, sans-serif; border-bottom: 1px dotted #3498DB; letter-spacing: 0.3px; background-color: rgba(52, 152, 219, 0.05); padding: 8px; border-radius: 3px; display: block; margin: 25px 0; clear: both;',

    'success': 'color: #27AE60; font-size: 16px; font-weight: 600; font-family: Arial, sans-serif; text-shadow: 1px 1px 2px rgba(39, 174, 96, 0.2); letter-spacing: 0.3px; background-color: rgba(39, 174, 96, 0.05); padding: 8px; border-radius: 3px; border-left: 2px solid #27AE60; display: block; margin: 25px 0; clear: both;',

    'warning': 'color: #F39C12; font-size: 16px; font-weight: 600; font-family: Arial, sans-serif; text-shadow: 1px 1px 2px rgba(243, 156, 18, 0.2); letter-spacing: 0.3px; background-color: rgba(243, 156, 18, 0.05); padding: 8px; border-radius: 3px; border-left: 2px solid #F39C12; display: block; margin: 25px 0; clear: both;',

    'error': 'color: #C0392B; font-size: 16px; font-weight: 600; font-family: Arial, sans-serif; text-shadow: 1px 1px 2px rgba(192, 57, 43, 0.2); letter-spacing: 0.3px; background-color: rgba(192, 57, 43, 0.05); padding: 8px; border-radius: 3px; border-left: 2px solid #C0392B; display: block; margin: 25px 0; clear: both;',

    'muted': 'color: #7F8C8D; font-size: 14px; font-family: Arial, sans-serif; font-style: italic; letter-spacing: 0.2px; opacity: 0.85; padding: 4px; display: block; margin: 20px 0; clear: both;',

    'primary': 'color: #3498DB; font-size: 16px; font-weight: 600; font-family: Arial, sans-serif; letter-spacing: 0.3px; background-color: rgba(52, 152, 219, 0.08); padding: 6px 10px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); display: block; margin: 25px 0; clear: both;',

    'secondary': 'color: #9B59B6; font-size: 16px; font-weight: 600; font-family: Arial, sans-serif; letter-spacing: 0.3px; background-color: rgba(155, 89, 182, 0.08); padding: 6px 10px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); display: block; margin: 25px 0; clear: both;',

    'progress': 'color: #2C3E50; font-size: 14px; font-weight: 500; font-family: "Segoe UI", Roboto, sans-serif; background: linear-gradient(to right, #f7f9fc, #edf2f7); padding: 18px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.04), 0 0 1px rgba(0,0,0,0.1); margin: 24px 0; border: none; display: block; clear: both;',

    'interactive_button': 'background-color: #3498db; color: white; padding: 12px 24px; font-size: 16px; border: none; border-radius: 8px; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1); position: relative; outline: none;',
}


def process_animation_class(animate: Optional[str]) -> Optional[str]:
    """
    Process animation class to match Animate.css naming conventions.
    
    Args:
        animate: Animation name (e.g., 'fadeIn', 'bounceOut') or full animation class
                with configuration (e.g., 'zoomIn animate__delay-2s')
        
    Returns:
        Fully qualified animation class name or None if not provided
        
    Example:
        process_animation_class('fadeIn') -> 'animate__animated animate__fadeIn'
        process_animation_class('zoomIn animate__delay-2s') -> 'animate__animated animate__zoomIn animate__delay-2s'
        
    Raises:
        AnimationError: If the animation name is not a valid Animate.css animation
    """
    if animate is None:
        return None

    # Split and extract components
    parts = _split_animation_string(animate)
    base_animation = _extract_base_animation(parts)
    additional_configs = _extract_additional_configs(parts)

    # Validate the animation name
    valid_animation_name = _validate_animation_name(base_animation)

    # Construct the final result
    return _build_animation_class_string(valid_animation_name, additional_configs)


def _split_animation_string(animate: str) -> List[str]:
    """Split the animation string into its component parts."""
    return animate.strip().split()


def _extract_base_animation(parts: List[str]) -> str:
    """Extract the base animation name from the parts list."""
    base_animation = parts[0]

    # Clean up the base animation name
    if base_animation.startswith('animate__animated'):
        base_animation = parts[1].replace('animate__', '')
    elif base_animation.startswith('animate__'):
        base_animation = base_animation.replace('animate__', '')

    return base_animation


def _extract_additional_configs(parts: List[str]) -> List[str]:
    """Extract and format additional configuration classes."""
    additional_configs = []

    # Process any additional configuration classes
    for part in parts[1:]:
        if part != 'animate__animated':  # Skip if it's the animated class
            # Ensure proper prefix for additional configurations
            if not part.startswith('animate__'):
                additional_configs.append(f"animate__{part}")
            else:
                additional_configs.append(part)

    return additional_configs


def _validate_animation_name(base_animation: str) -> str:
    """
    Validate the animation name against the list of valid animations.
    
    Raises:
        AnimationError: If the animation name is not valid
    """
    # Check against valid animations (case-insensitive)
    # This helps catch common capitalization errors like 'fadein' instead of 'fadeIn'
    valid_animation_name = None
    for valid_name in VALID_ANIMATIONS:
        if valid_name.lower() == base_animation.lower():
            valid_animation_name = valid_name
            break

    if valid_animation_name is None:
        raise AnimationError(
            animation_name=base_animation,
            message=f"Invalid animation name: '{base_animation}'. Valid animations are: {', '.join(VALID_ANIMATIONS[:10])}... "
                    f"See https://animate.style/ for the complete list."
        )

    return valid_animation_name


def _build_animation_class_string(valid_animation_name: str, additional_configs: List[str]) -> str:
    """Build the final animation class string with all components."""
    # Construct the final animation class string
    result = f"animate__animated animate__{valid_animation_name}"

    # Add any additional configuration classes
    if additional_configs:
        result += " " + " ".join(additional_configs)

    return result


# Add a function to check if we're in an IPython environment
def is_in_notebook() -> bool:
    """
    Check if code is running inside an IPython/Jupyter notebook.
    
    Returns:
        True if in a notebook, False otherwise
    """
    try:
        from IPython import get_ipython
        if get_ipython() is None:
            return False
        if 'IPKernelApp' not in get_ipython().config:
            return False
        return True
    except ImportError:
        return False


# noinspection PyCompatibility
def df_like(df, debug: bool = False, threshold: float = 0.7) -> bool:
    """
    Check if an object is dataframe-like by examining common dataframe attributes and methods.
    
    This function checks for the presence of common attributes and methods that are 
    typically found in dataframe implementations across different libraries
    (pandas, polars, modin, dask, etc.).
    
    Args:
        df: The object to check
        debug: If True, print debugging information
        threshold: The minimum ratio of common properties and methods to consider the object dataframe-like
    Returns:
        bool: True if the object is dataframe-like, False otherwise
    """
    if df is None:
        return False

    # Define common properties (attributes) found in dataframes
    properties = [
        'shape',  # Tuple of (rows, columns)
        'columns',  # Column labels
        'index',  # Row labels
        'values',  # Underlying data as array
        'dtypes',  # Data types of columns
    ]

    # Define common methods found in dataframes
    methods = [
        'head',  # Return first n rows
        'tail',  # Return last n rows
        'describe',  # Generate descriptive statistics
        'copy',  # Return a copy of the dataframe
        'iloc',  # Integer-location based indexing
        'loc',  # Label-based indexing
        'apply',  # Apply a function
    ]

    # Check properties - they should exist as attributes
    property_count = sum(hasattr(df, prop) for prop in properties)

    # Check methods - they should be callable
    method_count = sum(hasattr(df, method) and callable(getattr(df, method)) for method in methods)

    # Calculate total score
    total_items = len(properties) + len(methods)
    total_present = property_count + method_count

    # We consider it dataframe-like if it has at least 70% of the common attributes and methods
    _threshold = threshold * total_items

    if debug:
        # For debugging (can be removed in production)
        from pprint import pprint
        print("*" * 100)

        pprint(f"{properties = }")
        pprint(f"{methods = }")

        print("*" * 50)
        print(f"Properties: {property_count}/{len(properties)}")
        print(f"Methods: {method_count}/{len(methods)}")
        print(f"Total: {total_present}/{total_items} (threshold: {threshold})")

        print("*" * 100)

    return total_present >= _threshold


def array_like(obj) -> bool:
    """
    Check if an object is array-like by examining common array attributes and methods.
    
    This function checks for the presence of common attributes and methods that are 
    typically found in array implementations across different libraries
    (numpy arrays, torch tensors, tensorflow tensors, jax arrays, etc.).
    
    Args:
        obj: The object to check
        
    Returns:
        bool: True if the object is array-like, False otherwise
    """
    if obj is None:
        return False

    # Define common properties (attributes) found in arrays
    properties = [
        'shape',  # Dimensions of the array
        'size',  # Total number of elements
        'ndim',  # Number of dimensions
        'dtype',  # Data type of elements
        'T',  # Transpose of the array
        'flat',  # Flattened version of the array
        'real',  # Real part of complex array
        'imag'  # Imaginary part of complex array
    ]

    # Define common methods found in arrays
    methods = [
        'reshape',  # Change shape of array
        'transpose',  # Transpose dimensions
        'flatten',  # Return flattened copy
        'astype',  # Convert to different type
        'copy',  # Return a copy
        'sum',  # Sum of elements
        'mean',  # Mean of elements
        'min',  # Minimum value
        'max',  # Maximum value
        'argmin',  # Index of minimum value
        'argmax',  # Index of maximum value
        'all',  # Test if all elements are True
        'any',  # Test if any element is True
        'tolist',  # Convert to list
        '__getitem__'  # Support for indexing/slicing
    ]

    # Special handling for sequence protocol
    try:
        len(obj)
        has_len = True
    except (TypeError, AttributeError):
        has_len = False

    try:
        _ = obj[0]
        has_getitem = True
    except (TypeError, IndexError, AttributeError):
        has_getitem = False

    # Check properties - they should exist as attributes
    property_count = sum(hasattr(obj, prop) for prop in properties)

    # Check methods - they should be callable
    method_count = sum(hasattr(obj, method) and callable(getattr(obj, method)) for method in methods)

    # Calculate total score from standard properties and methods
    total_items = len(properties) + len(methods)
    total_present = property_count + method_count

    # Add sequence protocol checks
    if has_len:
        total_present += 1
    if has_getitem:
        total_present += 1
    total_items += 2

    # Special case for standard Python lists/tuples
    if isinstance(obj, (list, tuple)) and has_len and has_getitem:
        return True

    # We consider it array-like if it has at least 50% of the common attributes and methods
    # Lower threshold than dataframe check because array implementations vary more
    threshold = 0.5 * total_items

    # For debugging (can be removed in production)
    # print(f"Properties: {property_count}/{len(properties)}")
    # print(f"Methods: {method_count}/{len(methods)}")
    # print(f"Sequence protocol: {has_len + has_getitem}/2")
    # print(f"Total: {total_present}/{total_items} (threshold: {threshold})")

    return total_present >= threshold
