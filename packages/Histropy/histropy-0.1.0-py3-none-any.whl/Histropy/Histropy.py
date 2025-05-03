from Histropy.InterHist import InterHist
import easygui
def main_function():
    # 1. Prompts user to select image.
    path = easygui.fileopenbox()
    # 2. Opens InterHist Object, running preliminary calculations and opening the Histropy window.
    ih = InterHist(path)

if __name__ == "__main__":
    main_function()

