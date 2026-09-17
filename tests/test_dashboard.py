import http.cookiejar
import json
import urllib.error
import urllib.request
from urllib.parse import urlparse

import pytest

from unfold import Unfold


def test_dashboard_authentication_and_origin_boundary(tmp_path):
    library = Unfold(tmp_path)
    with library.dashboard() as view:
        origin = "http://" + urlparse(view.url).netloc
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(origin + "/state")
        assert error.value.code == 403
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        )
        assert opener.open(view.url).status == 200
        assert json.load(opener.open(origin + "/state"))["projects"] == []
        request = urllib.request.Request(
            origin + "/feedback", data=b"{}", headers={"Origin": "https://untrusted.example"}
        )
        with pytest.raises(urllib.error.HTTPError) as error:
            opener.open(request)
        assert error.value.code == 403
        with pytest.raises(urllib.error.HTTPError) as error:
            opener.open(origin + "/../../etc/passwd")
        assert error.value.code == 404
