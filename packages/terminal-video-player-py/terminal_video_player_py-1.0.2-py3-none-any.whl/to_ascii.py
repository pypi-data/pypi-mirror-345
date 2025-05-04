from PIL import Image


class to_ascii:
    def __init__(self, file, downscale, width_multiplication = 2.5, chars_list = [' ', '.', "'", '`', '^', ',', ':', ';', 'I', 'l', '!', 'i', '>', '<', '~', '+', '_', '-', '?', ']', '[', '}', '{', '1', ')', '(', '|', '/', 't', 'f', 'j', 'r', 'x', 'n', 'u', 'v', 'c', 'z', 'X', 'Y', 'U', 'J', 'C', 'L', 'Q', '0', 'O', 'Z', 'm', 'w', 'q', 'p', 'd', 'b', 'k', 'h', 'a', 'o', '*', '#', 'M', 'W', '&', '8', '%', 'B', '@', '$']):
        
        if type(file) is str:
            self.frame = Image.open(file)
        
        elif isinstance(file, Image.Image):
            self.frame = file

        else:
            raise Exception("Unsupported File Format")
        
        self.scale = downscale
        self.frame = self.frame.resize((int(self.frame.width//self.scale*width_multiplication), self.frame.height//self.scale))
        self.grayscale_pixels = list(self.frame.convert("L").getdata())
        self.rgb_pixels = list(self.frame.convert('RGB').getdata())
        self.chars_list = chars_list
        self.character_value = len(self.chars_list)/256

    def asciify(self) -> str:
        return "".join([self.chars_list[int(pixel*self.character_value)] if pixel_count % self.frame.width != 0 else "\n" for pixel_count, pixel in enumerate(self.grayscale_pixels)])[1:]

    def asciify_colored(self) -> str:
        return "".join([f"\u001b[38;2;{b};{g};{r}m{self.chars_list[int(self.grayscale_pixels[pixel_count]*self.character_value)]}" if pixel_count % self.frame.width != 0 else "\n" for pixel_count, (r, g, b) in enumerate(self.rgb_pixels)])[1:]

    def colors_list(self) -> list:
        return self.rgb_pixels

    def asciify_colored_test(self) -> str:
        result = ""
        for pixel_count, (r, g, b) in enumerate(self.rgb_pixels):
            if pixel_count % self.frame.width == 0 and pixel_count != 0:
                result += "\n"
            
            result += f"\u001b[38;2;{b};{g};{r}m{self.chars_list[int(self.grayscale_pixels[pixel_count]*self.character_value)]}"
    
        return result