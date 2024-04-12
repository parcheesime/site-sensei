from webchecks import get_links, get_class, get_tags, html_output
from linkchecks import link_status
# import emoji

url = "https://codeprojects.org/VoP_lzaZzLWjc7BGzEYbFSMyTbHfdb29WN12Rg4U-Hw/"
tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'img', 'li', 'br', 'a']

# URL status message, type string
url_status_message = link_status(url)

# Sort dictionary of tags from student web page into missing and present
tags_dict = get_tags(url, tags)
missing_tags = [k for k, v in tags_dict.items() if v == 0]
present_tags = [k for k, v in tags_dict.items() if v != 0]
# Tags message, type string
tags_message = "HTML Tags UPDATE: <br> Found {} tags <br> {} Missing {} tags <br> See Rubric.".format(present_tags, '\n', missing_tags)
# Class attribute message type string
class_message = get_class(url)

# Search links on page, list of links
listof_links = get_links(url)
page_links = [url+link for link in listof_links]

# Create a list of status messages for any links on the page
# If the list is empty, it means the student did not link a new html page, or they used an outside link
page_links_status_messages = [link_status(page_link) for page_link in page_links if "html" in page_link]


def create_message():
    big_message = "<li>{}</li>\n<li>{}</li>\n<li>{}</li>\n ".format(tags_message, class_message, url_status_message)
    if len(page_links_status_messages) == 0:
        big_message = big_message + "{} {} {} {}".format("\n", "<li>", "Missing link on page or incorrect link. <br> "
                                                                       "See Rubric.", "</li>")
    else:
        for link_message in page_links_status_messages:
            big_message = big_message + "{} {} {} {}". format("\n", "<li>", link_message, "</li>")
    html_output(big_message)


create_message()
