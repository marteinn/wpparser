# wpparser

wpparser parses wordpress export files and returns them as well formatted python dictionaries, for python 2.7+.

## How it works

The library uses ElementTree to traverse through the export file.

## Usage

	import wpparser
	
	data = wpparser.parse("./blog.wordpress.2014-09-26.xml")
	>>> {"blog": {"tagline": "Tagline",...


## What it returns

It returns a well formatted dict, containing the following datatypes:

- Blog: The general blog information, such as tagline, site url.
- Authors: A list with the different authors.
- Categories: The categories in use, organized as a nested array.
- Tags: A list with the different tags.
- Posts: An array that contains all posts, the post object might also contain the different comments belonging to the post.

### Example:


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
        "tags": [{
        	"term_id": "1", 
        	"slug": "bash", 
        	"name": "Bash"
        }],
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
            "post_id": "1",
            "link": "http://www.marteinn.se/blog/slug/",
            "pub_date": "Mon, 22 Sep 2014 20:10:40 +0000",
            "categories": ["category"],
            "is_sticky": "0",
            "post_name": "slug"
        }]
	}

## Installation
wpparser can easily be installed through pip.

    $ pip install wpparser


## Contributing

Want to contribute? Awesome. Just send a pull request.


## License

Genres is released under the [MIT License](http://www.opensource.org/licenses/MIT).