# type: ignore

type ImageFormat = Binary | Grayscale | RGB | RGBA | ...

class Image:

    # Creating Images

    @classmethod
    def open(cls, file: FileDescriptor) -> Image:
        ...

    @classmethod
    def new(cls, format: ImageFormat, size: (Nat, Nat), initialize: Maybe (Image | Color)) -> Image:
        ...

    @classmethod
    def from_array(cls, array: Array, format: ImageFormat) -> Image:
        # Integral a => Array n m a
        ...

    @classmethod
    def from_xxx(cls, xxx) -> Image:
        ...

    # Example methods

    def pixels(self) -> ImagePixels:
        ...

    def copy(self) -> Image:
        ...
    
    def crop(self, xxx) -> Image:
        ...

    def filter(self, xxx) -> Image:
        ...

    def view(self, xxx) -> ImageView:
        ...
    ...

class ImageView:

    def __init__(image: Image, region: ImageRegion):
        ...

    ...

class ImagePixels:
    ...
