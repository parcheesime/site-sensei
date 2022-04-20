from webchecks import *

tags_dict = get_tags("https://codeprojects.org/iNV5eM-Z6G6SNxKaJS03VwgNHr-oRk1jdsQe3BvcROY/")

for k, v in tags_dict.items():
    if v == 0:
        print("You have no {} tags. Please fix your web page.".format(k))
    else:
        print("All {} tags are complete.".format(k))