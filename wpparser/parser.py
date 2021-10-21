"""
wpparser
---

Load and parse the wp export file into a readable dictionary.
"""
import logging
import xml.etree.ElementTree as ET
from io import BytesIO as StringIO
from pathlib import Path
from typing import Dict, List, Optional, Union

import phpserialize

# Namespaces used by ElementTree with parsing wp xml.
EXCERPT_NAMESPACE = "http://wordpress.org/export/1.2/excerpt/"
CONTENT_NAMESPACE = "http://purl.org/rss/1.0/modules/content/"
WFW_NAMESPACE = "http://wellformedweb.org/CommentAPI/"
DC_NAMESPACE = "http://purl.org/dc/elements/1.1/"
WP_NAMESPACE = "http://wordpress.org/export/1.2/"


def parse(path: Union[str, Path]) -> dict:
    """
    Parses xml and returns a formatted dict.

    Example:

        wpparser.parse("./blog.wordpress.2014-09-26.xml")

    Will return:

        {
        "blog": {
            "tagline": "Tagline",
            "site_url": "http://marteinn.se/blog",
            "blog_url": "http://marteinn.se/blog",
            "language": "en-US",
            "title": "Marteinn / Blog"
        },
        "authors: [{
            "login": "admin",
            "last_name": None,
            "display_name": "admin",
            "email": "martin@marteinn.se",
            "first_name": None}
        ],
        "categories": [{
            "parent": None,
            "term_id": "3",
            "name": "Action Script",
            "nicename": "action-script",
            "children": [{
                "parent": "action-script",
                "term_id": "20",
                "name": "Flash related",
                "nicename": "flash-related",
                "children": []
            }]
        }],
        "tags": [{"term_id": "36", "slug": "bash", "name": "Bash"}],
        "posts": [{
            "creator": "admin",
            "excerpt": None,
            "post_date_gmt": "2014-09-22 20:10:40",
            "post_date": "2014-09-22 21:10:40",
            "post_type": "post",
            "menu_order": "0",
            "guid": "http://marteinn.se/blog/?p=828",
            "title": "Post Title",
            "comments": [{
                "date_gmt": "2014-09-24 23:08:31",
                "parent": "0",
                "date": "2014-09-25 00:08:31",
                "id": "85929",
                "user_id": "0",
                "author": u"Author",
                "author_email": None,
                "author_ip": "111.111.111.111",
                "approved": "1",
                "content": u"Comment title",
                "author_url": "http://example.com",
                "type": "pingback"
            }],
            "content": "Text",
            "post_parent": "0",
            "post_password": None,
            "status": "publish",
            "description": None,
            "tags": ["tag"],
            "ping_status": "open",
            "post_id": "828",
            "link": "http://www.marteinn.se/blog/slug/",
            "pub_date": "Mon, 22 Sep 2014 20:10:40 +0000",
            "categories": ["category"],
            "is_sticky": "0",
            "post_name": "slug"
        }]
        }
    """

    doc = ET.parse(path).getroot()

    channel = doc.find("./channel")

    blog = _parse_blog(channel)
    authors = _parse_authors(channel)
    categories = _parse_categories(channel)
    tags = _parse_tags(channel)
    posts = _parse_posts(channel)

    return {
        "blog": blog,
        "authors": authors,
        "categories": categories,
        "tags": tags,
        "posts": posts,
    }


def _get_wp_element(element: ET.Element, name: str) -> str:
    return element.find(f"./{{{WP_NAMESPACE}}}{name}").text


def _parse_blog(element: ET.Element) -> Dict[str, str]:
    """
    Parse and return general blog data (title, tagline etc).
    """

    title = element.find("./title").text
    tagline = element.find("./description").text
    language = element.find("./language").text
    site_url = _get_wp_element(element, "base_site_url")
    blog_url = _get_wp_element(element, "base_blog_url")

    return {
        "title": title,
        "tagline": tagline,
        "language": language,
        "site_url": site_url,
        "blog_url": blog_url,
    }


def _parse_authors(element: ET.Element) -> List[Dict[str, str]]:
    """
    Returns a well formatted list of users that can be matched against posts.
    """

    authors = []

    for item in element.findall(f"./{{{WP_NAMESPACE}}}author"):
        login = _get_wp_element(item, "author_login")
        email = _get_wp_element(item, "author_email")
        first_name = _get_wp_element(item, "author_first_name")
        last_name = _get_wp_element(item, "author_last_name")
        display_name = _get_wp_element(item, "author_display_name")

        authors.append({
            "login": login,
            "email": email,
            "display_name": display_name,
            "first_name": first_name,
            "last_name": last_name
        })

    return authors


def _parse_categories(element: ET.Element) -> List[Dict[str, str]]:
    """
    Returns a list with categories with relations.
    """
    reference = {}

    for item in element.findall(f"./{{{WP_NAMESPACE}}}category"):
        term_id = _get_wp_element(item, "term_id")
        nicename = _get_wp_element(item, "category_nicename")
        name = _get_wp_element(item, "cat_name")
        parent = _get_wp_element(item, "category_parent")

        category = {
            "term_id": term_id,
            "nicename": nicename,
            "name": name,
            "parent": parent
        }

        reference[nicename] = category

    return _build_category_tree(None, reference=reference)


def _build_category_tree(slug: Optional[str],
                         reference: Optional[Dict[str, Dict[str, str]]] = None,
                         items: Optional[List[Dict[str, str]]] = None
                         ) -> List[Dict[str, str]]:
    """
    Builds a recursive tree with category relations as children.
    """

    if items is None:
        items = []

    for key in reference:
        category = reference[key]

        if category["parent"] == slug:
            category["children"] = _build_category_tree(category["nicename"], reference=reference)
            items.append(category)

    return items


def _parse_tags(element: ET.Element) -> List[Dict[str, str]]:
    """
    Retrieves and parses tags into an array/dict.

    Example:

        [{"term_id": 1, "slug": "python", "name": "Python"},
        {"term_id": 2, "slug": "java", "name": "Java"}]
    """

    tags = []

    for item in element.findall(f"./{{{WP_NAMESPACE}}}tag"):
        term_id = _get_wp_element(item, "term_id")
        slug = _get_wp_element(item, "tag_slug")
        name = _get_wp_element(item, "tag_name")

        tag = {
            "term_id": term_id,
            "slug": slug,
            "name": name,
        }

        tags.append(tag)

    return tags


def _parse_posts(element: ET.Element) -> List[Dict[str, str]]:
    """
    Returns a list with posts.
    """

    posts = []
    items = element.findall("item")

    for item in items:
        title = item.find("./title").text
        link = item.find("./link").text
        pub_date = item.find("./pubDate").text
        creator = item.find(f"./{{{DC_NAMESPACE}}}creator").text
        guid = item.find("./guid").text
        description = item.find("./description").text
        content = item.find(f"./{{{CONTENT_NAMESPACE}}}encoded").text
        excerpt = item.find(f"./{{{EXCERPT_NAMESPACE}}}encoded").text
        post_id = _get_wp_element(item, "post_id")
        post_date = _get_wp_element(item, "post_date")
        post_date_gmt = _get_wp_element(item, "post_date_gmt")
        status = _get_wp_element(item, "status")
        post_parent = _get_wp_element(item, "post_parent")
        menu_order = _get_wp_element(item, "menu_order")
        post_type = _get_wp_element(item, "post_type")
        post_name = _get_wp_element(item, "post_name")
        is_sticky = _get_wp_element(item, "is_sticky")
        ping_status = _get_wp_element(item, "ping_status")
        post_password = _get_wp_element(item, "post_password")
        category_items = item.findall("./category")

        category_domains = {}

        for category_item in category_items:
            if category_item.attrib["domain"] not in category_domains:
                category_domains[category_item.attrib["domain"]] = []
            category_domains[category_item.attrib["domain"]].append({'nicename': category_item.attrib["nicename"], 'text': category_item.text})

        post = {
            "title": title,
            "link": link,
            "pub_date": pub_date,
            "creator": creator,
            "guid": guid,
            "description": description,
            "content": content,
            "excerpt": excerpt,
            "post_id": post_id,
            "post_date": post_date,
            "post_date_gmt": post_date_gmt,
            "status": status,
            "post_parent": post_parent,
            "menu_order": menu_order,
            "post_type": post_type,
            "post_name": post_name,
            "is_sticky": is_sticky,
            "ping_status": ping_status,
            "post_password": post_password,
        }

        # Include all categories with a prefix inorder to avoid collisions
        for k, v in category_domains.items():
            post[f'category_{k}'] = v

        post["postmeta"] = _parse_postmeta(item)
        post["comments"] = _parse_comments(item)
        posts.append(post)

    return posts


def _parse_postmeta(element: ET.Element) -> Dict[str, str]:
    """
    Retrieve post metadata as a dictionary
    """

    metadata = {}
    fields = element.findall(f"./{{{WP_NAMESPACE}}}postmeta")

    for field in fields:
        key = _get_wp_element(field, 'meta_key')
        value = _get_wp_element(field, 'meta_value')

        if key == "_wp_attachment_metadata":
            stream = StringIO(value.encode())
            try:
                data = phpserialize.load(stream)
                metadata["attachment_metadata"] = data
            except ValueError as e:
                logging.warning(e)
            except Exception as e:
                raise e

        elif key == "_wp_attached_file":
            metadata["attached_file"] = value
        else:
            metadata[key] = value

    return metadata


def _parse_comments(element: ET.Element) -> List[Dict[str, str]]:
    """
    Returns a list with comments.
    """

    comments = []
    items = element.findall(f"./{{{WP_NAMESPACE}}}comment")

    for item in items:
        comment_id = _get_wp_element(item, 'comment_id')
        author = _get_wp_element(item, 'comment_author')
        email = _get_wp_element(item, 'comment_author_email')
        author_url = _get_wp_element(item, 'comment_author_url')
        author_ip = _get_wp_element(item, 'comment_author_IP')
        date = _get_wp_element(item, 'comment_date')
        date_gmt = _get_wp_element(item, 'comment_date_gmt')
        content = _get_wp_element(item, 'comment_content')
        approved = _get_wp_element(item, 'comment_approved')
        comment_type = _get_wp_element(item, 'comment_type')
        parent = _get_wp_element(item, 'comment_parent')
        user_id = _get_wp_element(item, 'comment_user_id')

        comment = {
            "id": comment_id,
            "author": author,
            "author_email": email,
            "author_url": author_url,
            "author_ip": author_ip,
            "date": date,
            "date_gmt": date_gmt,
            "content": content,
            "approved": approved,
            "type": comment_type,
            "parent": parent,
            "user_id": user_id,
        }

        comments.append(comment)

    return comments
