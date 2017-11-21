from parser import Parser


def test_person_example():
    html = '<span class="h-card">Frances Berriman</span>'
    p = Parser()
    result = p.parse(html)
    assert result["items"][0]["type"] == ["h-card"]
    assert result["items"][0]["properties"]["name"] == ["Frances Berriman"]


def test_link_person_example():
    html = '<a class="h-card" href="http://benward.me">Ben Ward</a>'
    p = Parser()
    result = p.parse(html)
    assert result["items"][0]["type"] == ["h-card"]
    assert result["items"][0]["properties"]["name"] == ["Ben Ward"]
    assert result["items"][0]["properties"]["url"] == ["http://benward.me"]


def test_hyperlinked_person_image():
    html = '<a class="h-card" href="http://rohit.khare.org/">' \
           '<img alt="Rohit Khare" ' \
           'src="https://s3.amazonaws.com/twitter_production/profile_images/53307499/180px-Rohit-sq_bigger.jpg" />' \
           '</a>'
    p = Parser()
    result = p.parse(html)
    assert result["items"][0]["type"] == ["h-card"]
    assert result["items"][0]["properties"]["name"] == ["Rohit Khare"]
    assert result["items"][0]["properties"]["url"] == ["http://rohit.khare.org/"]
    assert result["items"][0]["properties"]["photo"] == \
           ["https://s3.amazonaws.com/twitter_production/profile_images/53307499/180px-Rohit-sq_bigger.jpg"]


def test_detailed_person_example():
    html = '<div class="h-card">' \
           '<img class="u-photo" alt="photo of Mitchell" ' \
           '    src="https://webfwd.org/content/about-experts/300.mitchellbaker/mentor_mbaker.jpg"/>' \
           '<a class="p-name u-url" href="http://blog.lizardwrangler.com/">Mitchell Baker</a>' \
           '(<a class="u-url" href="https://twitter.com/MitchellBaker">@MitchellBaker</a>)' \
           '<span class="p-org">Mozilla Foundation</span>' \
           '<p class="p-note">Mitchell is responsible for setting the direction and scope of the Mozilla Foundation ' \
           'and its activities.</p>' \
           '<span class="p-category">Strategy</span><span class="p-category">Leadership</span></div>'
    p = Parser()
    result = p.parse(html)
    assert result["items"][0]["type"] == ["h-card"]
    assert result["items"][0]["properties"]["name"] == ["Mitchell Baker"]
    assert result["items"][0]["properties"]["url"] == ["http://blog.lizardwrangler.com/",
                                                       "https://twitter.com/MitchellBaker"]
    assert result["items"][0]["properties"]["photo"] == \
           ["https://webfwd.org/content/about-experts/300.mitchellbaker/mentor_mbaker.jpg"]
    assert result["items"][0]["properties"]["org"] == ["Mozilla Foundation"]
    assert result["items"][0]["properties"]["note"] == ["Mitchell is responsible for setting the direction and scope "
                                                        "of the Mozilla Foundation and its activities."]
    assert result["items"][0]["properties"]["category"] == ["Strategy", "Leadership"]


def test_h_event_location_h_card():
    html = '<div class="h-event">' \
           '    <a class="p-name u-url" href="http://indiewebcamp.com/2012">' \
           '        IndieWebCamp 2012' \
           '    </a>' \
           '    from <time class="dt-start">2012-06-30</time>' \
           '    to <time class="dt-end">2012-07-01</time> at' \
           '    <span class="p-location h-card">' \
           '        <a class="p-name p-org u-url" href="http://geoloqi.com/">' \
           '            Geoloqi' \
           '        </a>,' \
           '        <span class="p-street-address">920 SW 3rd Ave. Suite 400</span>,' \
           '        <span class="p-locality">Portland</span>,' \
           '        <abbr class="p-region" title="Oregon">OR</abbr>' \
           '    </span>' \
           '</div>'
    p = Parser()
    result = p.parse(html)
    assert result["items"][0]["type"] == ["h-event"]
    properties = result["items"][0]["properties"]
    assert properties["name"] == ["IndieWebCamp 2012"]
    assert properties["url"] == ["http://indiewebcamp.com/2012"]
    assert properties["start"] == ["2012-06-30"]
    assert properties["end"] == ["2012-07-01"]
    location = properties["location"]
    assert location["value"] == "Geoloqi"
    assert location["type"] == "h-card"
    assert location["properties"]["name"] == ["Geoloqi"]
    assert location["properties"]["org"] == ["Geoloqi"]
    assert location["properties"]["url"] == ["http://geoloqi.com/"]
    assert location["properties"]["street-address"] == ["920 SW 3rd Ave. Suite 400"]
    assert location["properties"]["locality"] == ["Portland"]
    assert location["properties"]["region"] == ["Oregon"]


def test_h_card_org_h_card():
    html = '<div class="h-card">' \
           '    <a class="p-name u-url" ' \
           '       href="http://blog.lizardwrangler.com/"' \
           '      >Mitchell Baker</a>' \
           '    (<span class="p-org">Mozilla Foundation</span>)' \
           '</div>'
    p = Parser()
    result = p.parse(html)
    assert result["items"][0]["type"] == ["h-card"]
    properties = result["items"][0]["properties"]
    assert properties["name"] == ["Mitchell Baker"]
    assert properties["url"] == ["http://blog.lizardwrangler.com/"]
    assert properties["org"] == ["Mozilla Foundation"]

#   todo: add other examples from http://microformats.org/wiki/microformats2
