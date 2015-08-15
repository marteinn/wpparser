# -*- coding: utf-8 -*-

"""
wpparser
---

Load and parse the wp export file into a readable dictionary.
"""

try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


# Namespaces used by ElementTree with parsing wp xml.
EXCERPT_NAMESPACE = "http://wordpress.org/export/1.2/excerpt/"
CONTENT_NAMESPACE = "http://purl.org/rss/1.0/modules/content/"
WFW_NAMESPACE = "http://wellformedweb.org/CommentAPI/"
DC_NAMESPACE = "http://purl.org/dc/elements/1.1/"
WP_NAMESPACE = "http://wordpress.org/export/1.2/"


def parse(path):
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


def _parse_blog(element):
    """
    Parse and return genral blog data (title, tagline etc).
    """

    title = element.find("./title").text
    tagline = element.find("./description").text
    language = element.find("./language").text
    site_url = element.find("./{%s}base_site_url" % WP_NAMESPACE).text
    blog_url = element.find("./{%s}base_blog_url" % WP_NAMESPACE).text

    return {
        "title": title,
        "tagline": tagline,
        "language": language,
        "site_url": site_url,
        "blog_url": blog_url,
    }


def _parse_authors(element):
    """
    Returns a well formatted list of users that can be matched against posts.
    """

    authors = []
    items = element.findall("./{%s}author" % WP_NAMESPACE)

    for item in items:
        login = item.find("./{%s}author_login" % WP_NAMESPACE).text
        email = item.find("./{%s}author_email" % WP_NAMESPACE).text
        first_name = item.find("./{%s}author_first_name" % WP_NAMESPACE).text
        last_name = item.find("./{%s}author_last_name" % WP_NAMESPACE).text
        display_name = item.find(
            "./{%s}author_display_name" % WP_NAMESPACE).text

        authors.append({
            "login": login,
            "email": email,
            "display_name": display_name,
            "first_name": first_name,
            "last_name": last_name
        })

    return authors


def _parse_categories(element):
    """
    Returns a list with categories with relations.
    """
    reference = {}
    items = element.findall("./{%s}category" % WP_NAMESPACE)

    for item in items:
        term_id = item.find("./{%s}term_id" % WP_NAMESPACE).text
        nicename = item.find("./{%s}category_nicename" % WP_NAMESPACE).text
        name = item.find("./{%s}cat_name" % WP_NAMESPACE).text
        parent = item.find("./{%s}category_parent" % WP_NAMESPACE).text

        category = {
            "term_id": term_id,
            "nicename": nicename,
            "name": name,
            "parent": parent
        }

        reference[nicename] = category

    return _build_category_tree(None, reference=reference)


def _build_category_tree(slug, reference=None, items=None):
    """
    Builds a recursive tree with category relations as children.
    """

    if items is None:
        items = []

    for key in reference:
        category = reference[key]

        if category["parent"] == slug:
            children = _build_category_tree(category["nicename"],
                                            reference=reference)
            category["children"] = children
            items.append(category)

    return items


def _parse_tags(element):
    """
    Retrieves and parses tags into a array/dict.

    Example:

        [{"term_id": 1, "slug": "python", "name": "Python"},
        {"term_id": 2, "slug": "java", "name": "Java"}]
    """

    tags = []
    items = element.findall("./{%s}tag" % WP_NAMESPACE)

    for item in items:
        term_id = item.find("./{%s}term_id" % WP_NAMESPACE).text
        slug = item.find("./{%s}tag_slug" % WP_NAMESPACE).text
        name = item.find("./{%s}tag_name" % WP_NAMESPACE).text

        tag = {
            "term_id": term_id,
            "slug": slug,
            "name": name,
        }

        tags.append(tag)

    return tags


def _parse_posts(element):
    """
    Returns a list with posts.
    """

    posts = []
    items = element.findall("item")

    for item in items:
        title = item.find("./title").text
        link = item.find("./link").text
        pub_date = item.find("./pubDate").text
        creator = item.find("./{%s}creator" % DC_NAMESPACE).text
        guid = item.find("./guid").text
        description = item.find("./description").text
        content = item.find("./{%s}encoded" % CONTENT_NAMESPACE).text
        excerpt = item.find("./{%s}encoded" % EXCERPT_NAMESPACE).text
        post_id = item.find("./{%s}post_id" % WP_NAMESPACE).text
        post_date = item.find("./{%s}post_date" % WP_NAMESPACE).text
        post_date_gmt = item.find("./{%s}post_date_gmt" % WP_NAMESPACE).text
        status = item.find("./{%s}status" % WP_NAMESPACE).text
        post_parent = item.find("./{%s}post_parent" % WP_NAMESPACE).text
        menu_order = item.find("./{%s}menu_order" % WP_NAMESPACE).text
        post_type = item.find("./{%s}post_type" % WP_NAMESPACE).text
        post_name = item.find("./{%s}post_name" % WP_NAMESPACE).text
        is_sticky = item.find("./{%s}is_sticky" % WP_NAMESPACE).text
        ping_status = item.find("./{%s}ping_status" % WP_NAMESPACE).text
        post_password = item.find("./{%s}post_password" % WP_NAMESPACE).text
        category_items = item.findall("./category")

        categories = []
        tags = []

        for category_item in category_items:
            if category_item.attrib["domain"] == "category":
                item_list = categories
            else:
                item_list = tags

            item_list.append(category_item.attrib["nicename"])

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
            "categories": categories,
            "is_sticky": is_sticky,
            "ping_status": ping_status,
            "post_password": post_password,
            "tags": tags,
        }

        post["postmeta"] = _parse_postmeta(item)
        post["comments"] = _parse_comments(item)
        posts.append(post)

    return posts


def _parse_postmeta(element):
    import phpserialize

    """
    Retrive post metadata as a dictionary
    """

    metadata = {}
    fields = element.findall("./{%s}postmeta" % WP_NAMESPACE)

    for field in fields:
        key = field.find("./{%s}meta_key" % WP_NAMESPACE).text
        value = field.find("./{%s}meta_value" % WP_NAMESPACE).text

        if key == "_wp_attachment_metadata":
            stream = StringIO(value.encode())
            try:
                data = phpserialize.load(stream)
                metadata["attachment_metadata"] = data
            except ValueError as e:
                pass
            except Exception as e:
                raise(e)

        if key == "_wp_attached_file":
            metadata["attached_file"] = value

    return metadata


def _parse_comments(element):
    """
    Returns a list with comments.
    """

    comments = []
    items = element.findall("./{%s}comment" % WP_NAMESPACE)

    for item in items:
        comment_id = item.find("./{%s}comment_id" % WP_NAMESPACE).text
        author = item.find("./{%s}comment_author" % WP_NAMESPACE).text
        email = item.find("./{%s}comment_author_email" % WP_NAMESPACE).text
        author_url = item.find("./{%s}comment_author_url" % WP_NAMESPACE).text
        author_ip = item.find("./{%s}comment_author_IP" % WP_NAMESPACE).text
        date = item.find("./{%s}comment_date" % WP_NAMESPACE).text
        date_gmt = item.find("./{%s}comment_date_gmt" % WP_NAMESPACE).text
        content = item.find("./{%s}comment_content" % WP_NAMESPACE).text
        approved = item.find("./{%s}comment_approved" % WP_NAMESPACE).text
        comment_type = item.find("./{%s}comment_type" % WP_NAMESPACE).text
        parent = item.find("./{%s}comment_parent" % WP_NAMESPACE).text
        user_id = item.find("./{%s}comment_user_id" % WP_NAMESPACE).text

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
