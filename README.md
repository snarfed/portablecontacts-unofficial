portablecontacts-unofficial ![PortableContacts](https://raw.github.com/snarfed/portablecontacts-unofficial/master/static/logo.jpg)
===

  * [About](#about)
  * [Using](#using)
    * [Using the REST API](#using-the-REST-API)
    * [Using the library](#using-the-library)
  * [Future work](#future-work)
  * [Development](#development)


About
---

This is a library and REST API that converts Facebook and Twitter user data to
the [PortableContacts](http://portablecontacts.net/) format. You can try it out
with these interactive demos:

http://facebook-poco.appspot.com/  
http://twitter-poco.appspot.com/

It's part of a suite of projects that implement the
[OStatus](http://ostatus.org/) federation protocols for the major social
networks. The other projects include
[activitystreams-](https://github.com/snarfed/activitystreams-unofficial),
[salmon-](https://github.com/snarfed/salmon-unofficial),
[webfinger-](https://github.com/snarfed/webfinger-unofficial), and
[ostatus-unofficial](https://github.com/snarfed/ostatus-unofficial).

Google isn't included because it already serves Gmail contacts and user data in
PortableContacts format at `gmail.com`.

License: This project is placed in the public domain.


Using
---

The library and REST API are both based on the
[PortableContacts 1.0 Draft C spec](http://portablecontacts.net/draft-spec.html)

Let's start with an example. This code using the library:

```python
from portablecontacts_unofficial import twitter
...
tw = twitter.Twitter(handler)
tw.get_contacts()
```

is equivalent to this `HTTP GET` request:

```
https://twitter-poco.appspot.com/poco/@me/@all/USER_ID?access_token_key=KEY&access_token_secret=SECRET
```

They return the Twitter users that the authenticated user follows. Here's the
JSON output:

```json
{
  "itemsPerPage": 10,
  "startIndex": 0,
  "totalResults": 12
  "items": [{
    "id": "139199211",
    "displayName": "Ryan Barrett",
    "name": {"formatted": "Ryan Barrett"},
    "accounts": [{"domain": "twitter.com",
                  "userid": "139199211",
                  "username": "snarfed_org",
                  }],
    "addresses": [{"formatted": "San Francisco, CA", "type": "home", }],
    "photos": [{"value": "http://a1.twimg.com/profile_images/866165047/ryan_normal.jpg",
                "primary": "true",
                }],
    "urls": [{"value": "http://snarfed.org/",
              "type": "home",
              }],
    ...
  }, ...]
  ...
}
```

The request parameters are the same for both, all optional: `group_id` may be
`@all` or `@self`. `USER_ID` may be a specific user id or unset for all users.

Paging is supported via the `startIndex` and `count` parameters. They're self
explanatory, and described in detail in the
[OpenSearch spec](http://www.opensearch.org/Specifications/OpenSearch/1.1#The_.22count.22_parameter).

Output data is
[PoCo JSON](http://portablecontacts.net/draft-spec.html#rfc.section.6.3.4)
formatted
[response object](http://portablecontacts.net/draft-spec.html#response-format)
dicts, which put the contacts in a top-level `entry` list alongside
`itemsPerPage`, `totalCount`, etc. fields.

Most requests will need an OAuth access token from the source provider. Here are
their authentication docs:
[Facebook](https://developers.facebook.com/docs/facebook-login/access-tokens/),
[Twitter](https://dev.twitter.com/docs/auth/3-legged-authorization).

If you get an access token and pass it along, it will be used to sign and
authorize the underlying requests to the sources providers. See the demos on the
REST API [endpoints above](#about) for examples.


Using the REST API
---

The [endpoints above](#about) all implement the
[PoCo REST API](http://portablecontacts.net/draft-spec.html#anchor7).
Request paths are of the form:

```
/poco/@me/GROUP_ID/[USER_ID]?startIndex=...&count=...&format=FORMAT&access_token=...
```

All query parameters are optional.
`FORMAT` may be `json` (the default), `xml`, or `atom`, both of which return
[Atom](http://www.intertwingly.net/wiki/pie/FrontPage).
The rest of the path elements and query params are [described above](#using).

Errors are returned with the appropriate HTTP response code, e.g. 403 for
Unauthorized, with details in the response body.

To use the REST API in an existing PoCo client, you'll need to
hard-code exceptions for the domains you want to use e.g. `facebook.com`, and
redirect HTTP requests to the corresponding [endpoint above](#about).


Using the library
---

See the [example above](#using) for a quick start guide.

Clone or download this repo into a directory named `portablecontacts_unofficial`
(note the underscore instead of dash). Each source works the same way. Import
the module for the source you want to use, then instantiate its class by passing
the HTTP handler object. The handler should have a `request` attribute for the
current HTTP request.

The useful methods are `get_contact()` and `get_current_user()`, which returns
the current authenticated user (if any). See the
[individual method docstrings](https://github.com/snarfed/portablecontacts-unofficial/blob/master/source.py)
for details. All return values are Python dicts of decoded PortableContacts JSON
objects.


Future work
---

Twitter needs to be ported to their v1.1 API.

The REST APIs are currently much more usable than the library. We need to make
the library easier to use. Most of the hard work is already done; here's what remains.

  * Allow passing OAuth tokens as keyword args.
  * Expose the initial OAuth permission flow. The hard work is already done, we
    just need to let users trigger it programmatically.
  * Expose the `format` arg and let users request
    [Atom](http://www.intertwingly.net/wiki/pie/FrontPage) output.

We'd also love to add more sites! Off the top of my head,
[Yahoo](http://yahoo.com/),
[Outlook.com](http://msdn.microsoft.com/en-us/library/windows/apps/Hh770846.aspx),
[Apple's iCloud](https://www.icloud.com/),
[Instagram](http://instagram.com/developer/), and
[Sina Weibo](http://en.wikipedia.org/wiki/Sina_Weibo) would be good candidates. If
you're looking to get started, implementing a new site is a good place to start.
It's pretty self contained and the existing sites are good examples to follow,
but it's a decent amount of work, so you'll be familiar with the whole project
by the end.

Finally, here are some Facebook tweaks we should implement to make sure we
comply with their TOS:

* [can't use user ids](https://developers.facebook.com/policy/#data); switch to
  [User.third_party_id](https://developers.facebook.com/docs/reference/api/user/)
* can
  [only use friend connections](https://developers.facebook.com/policy/#data) if
  *both* users have opted into app:


Development
---

Pull requests are welcome! Feel free to [ping me](http://snarfed.org/about) with
any questions.

Most dependencies are included as git submodules. Be sure to run `git submodule
init` after cloning this repo.

[This PortableContacts test client and validator](http://www.plaxo.com/pdata/testClient)
is useful for manual testing.

You can run the unit tests with `./alltests.py`. They depend on the
[App Engine SDK](https://developers.google.com/appengine/downloads) and
[mox](http://code.google.com/p/pymox/), both of which you'll need to install
yourself.

Note the `app.yaml.*` files, one for each App Engine app id. To work on or deploy
a specific app id, `symlink app.yaml` to its `app.yaml.xxx` file. Likewise, if you
add a new site, you'll need to add a corresponding `app.yaml.xxx` file.

To deploy:

```shell
rm -f app.yaml && ln -s app.yaml.twitter app.yaml && \
  ~/google_appengine/appcfg.py --oauth2 update . && \
rm -f app.yaml && ln -s app.yaml.facebook app.yaml && \
  ~/google_appengine/appcfg.py --oauth2 update .
```
