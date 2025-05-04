#!/usr/bin/env python
# *****************************************************************************
# Copyright (C) 2024 Thomas Touhey <thomas@touhey.fr>
#
# This software is governed by the CeCILL-C license under French law and
# abiding by the rules of distribution of free software. You can use, modify
# and/or redistribute the software under the terms of the CeCILL-C license
# as circulated by CEA, CNRS and INRIA at the following
# URL: https://cecill.info
#
# As a counterpart to the access to the source code and rights to copy, modify
# and redistribute granted by the license, users are provided only with a
# limited warranty and the software's author, the holder of the economic
# rights, and the successive licensors have only limited liability.
#
# In this respect, the user's attention is drawn to the risks associated with
# loading, using, modifying and/or developing or reproducing the software by
# the user in light of its specific status of free software, that may mean
# that it is complicated to manipulate, and that also therefore means that it
# is reserved for developers and experienced professionals having in-depth
# computer knowledge. Users are therefore encouraged to load and test the
# software's suitability as regards their requirements in conditions enabling
# the security of their systems and/or data to be ensured and, more generally,
# to use and operate it in the same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL-C license and that you accept its terms.
# *****************************************************************************
"""Planète Casio BBCode reverse enginneerer."""

from __future__ import annotations

import re
from collections.abc import Iterable
from urllib.parse import parse_qsl, urlparse

from lxml.etree import Element

_SMILEYS = {
    "twisted.gif": ">:)",
    "evil.gif": ">:(",
    "smile.gif": ":)",
    "wink.gif": ";)",
    "sad.gif": ":(",
    "grin.gif": ":D",
    "hehe.gif": ":p",
    "cool2.gif": "8-)",
    "mad.gif": ":@",
    "eek.gif": "0_0",
    "mrgreen.gif": ":E",
    "shocked.gif": ":O",
    "confused2.gif": ":s",
    "eyebrows.gif": "^^",
    "cry.gif": ":'(",
    # Name based smileys.
    "lol.gif": ":lol:",
    "redface.gif": ":sry:",
    "rolleyes.gif": ":mmm:",
    "waza.gif": ":waza:",
    "whistle.gif": ":whistle:",
    "pointer.gif": ":here:",
    "bow.gif": ":bow:",
    "cool.gif": ":cool:",
    "welldone.gif": ":good:",
    "love.gif": ":love:",
    "facepalm.gif": ":facepalm:",
    "insults.gif": ":argh:",
    "what.gif": ":?:",
    "excl.gif": ":!:",
    "comiteplus.gif": ":+:",
    "comitemoins.gif": ":-:",
    "comitetilde.gif": ":~:",
    "here.gif": ":arrow:",
    # Big name based smileys.
    "champion.gif": ":champ:",
    "bounce.gif": ":bounce:",
    "fusil.gif": ":fusil:",
    "boulet2.gif": ":boulet2:",
    "shocked2.gif": ":omg:",
    "mdr.gif": ":mdr:",
    "merci.gif": ":thx:",
    "banghead2.gif": ":aie:",
}
_FONT_NAMES = {
    "Arial": "arial",
    "Comic MS": "comic",
    "Tahoma": "tahoma",
    "Courier": "courier",
    "Haettenschweiler": "haettenschweiler",
}
_COLOR_TAG_NAMES = {
    "red",
    "blue",
    "green",
    "yellow",
    "maroon",
    "purple",
    "gray",
    "brown",
}

_WHITESPACE = re.compile(r"\s+")
_NEWLINE = re.compile(r"[ \r]*\n[ \r]*")
_SMILEY_URL = re.compile(
    rf"/images/smileys/({'|'.join(re.escape(key) for key in _SMILEYS)})$",
)
_CALC_URL = re.compile(r"^/images/icones/calc/(.+)\.png$")
_YOUTUBE_EMBED_PATTERN = re.compile(r"^https://youtube.com/embed/([^/]+)$")


def _parse_css_statements(raw: str, /) -> dict[str, str]:
    """Parse CSS into statements.

    :param raw: Raw CSS.
    :return: Decoded CSS.
    """
    attrs: dict[str, str] = {}
    for stmt in raw.split(";"):
        key, sep, value = stmt.partition(":")
        if not sep or not key.strip():
            continue

        attrs[key.strip()] = value.strip()

    return attrs


def _process_text(text: str | None, /) -> str:
    """Process raw HTML.

    :param text: Text or tail of a node.
    """
    if text is None:
        return ""

    # TODO: If there's some impossible plaintext (e.g. having raw "[code]"),
    #       this means [noeval] has most likely been called, and therefore,
    #       we probably need to use it here as well.
    return _WHITESPACE.sub(" ", text)


def _process_el(el: Element, /) -> str:
    """Transform an element to BBCode.

    :param el: HTML element to transform.
    :return: Obtained BBCode.
    """
    if el.tag == "div":
        if el.attrib.get("class") == "code":
            return f"[code]{''.join(el.itertext())}[/code]"

        if el.attrib.get("class") == "citation":
            if el.text:
                # If there is text before the first element, then the first
                # element cannot be the author.
                return _process_children(
                    el,
                    prefix="[quote]",
                    suffix="[/quote]",
                    force=True,
                )

            author_els = el.xpath(
                "./*[1][name()='b']"
                + "/*[1][name()='i'][contains(text(), ' a écrit :')]",
            )
            if author_els:
                author_content = _process_children(author_els[0])[:-10]
            else:
                author_content = ""

            if not author_content:
                # No author at the first position, the first element is not
                # the author.
                return _process_children(
                    el,
                    prefix="[quote]",
                    suffix="[/quote]",
                    force=True,
                )

            return (
                "[quote="
                + author_content
                + "]"
                + _process_els(list(el)[1:])  # Skip first element.
                + "[/quote]"
            )

        if el.attrib.get("class") == "spoiler":
            closed = _process_children(el.xpath("./div[1]")[0])
            opened = _process_children(el.xpath("./div[2]")[0])

            if opened == "Cliquez pour recouvrir":
                opened = ""
            if closed == "Cliquez pour découvrir":
                closed = ""

            start_tag = "spoiler"
            if opened or closed:
                start_tag = f"spoiler={closed}|{opened}"

            return _process_children(
                el.xpath("./div[3]"),
                prefix=f"[{start_tag}]",
                suffix="[/spoiler]",
                force=True,
            )

        if el.xpath("./div[last()]/div[contains(@style, '#FF3E28')]"):
            value = el.xpath("./div[last()]/div/text()")[0].strip()[:-1]
            return _process_children(
                el,
                prefix=f"[progress={value}]",
                suffix="[/progress]",
                force=True,
            )

        css = _parse_css_statements(el.attrib.get("style", ""))
        if css == {"text-align": "justify"}:
            return _process_children(
                el,
                prefix="[justify]",
                suffix="[/justify]",
                force=True,
            )

        if css == {"text-indent": "30px"}:
            return _process_children(
                el,
                prefix="[indent]",
                suffix="[/indent]",
                force=True,
            )

        raise NotImplementedError()

    if el.tag == "span":
        css = _parse_css_statements(el.attrib.get("style", ""))
        keys = set(css)

        if keys == {"font-family"} and css["font-family"] == "monospace":
            # This is either inline code or just monospace stuff.
            # We can't really distinguish between them, but we can just
            # assume it's inline code if it only has text beneath it.
            if len(el) == 0:
                content = "".join(el.itertext())
                if "`" in content:
                    return f"[inlinecode]{content}[/inlinecode]"

                return f"`{content}`"

            return _process_children(el, prefix="[mono]", suffix="[/mono]")

        if keys == {"font-family"} and css["font-family"] in _FONT_NAMES:
            tag = _FONT_NAMES[css["font-family"]]
            return _process_children(el, prefix=f"[{tag}]", suffix=f"[/{tag}]")

        if keys == {"color"}:
            color = css["color"]
            if color in _COLOR_TAG_NAMES:
                return _process_children(
                    el,
                    prefix=f"[{color}]",
                    suffix=f"[/{color}]",
                )

            return _process_children(
                el,
                prefix=f"[color={color}]",
                suffix="[/color]",
            )

        if css == {"font-size": "15px"}:
            return _process_children(el, prefix="[big]", suffix="[/big]")

        if css == {"font-size": "9px"}:
            return _process_children(el, prefix="[small]", suffix="[/small]")

        raise NotImplementedError()

    if el.tag == "img":
        # Could be an obfuscated e-mail address, an emoji, or an actual image.
        # First, check for obfuscated e-mail addresses.
        url = el.attrib["src"]
        parsed_url = urlparse(url)

        if (
            parsed_url._replace(query="").geturl()
            == "/script/public/email.php"
        ):
            # We may have an obfuscated e-mail address on our hand, as long
            # as parameters "domain" and "user" are defined.
            params = dict(parse_qsl(parsed_url.query))
            if set(params) == {"user", "domain"}:
                return f"{params['user']}@{params['domain']}"
        else:
            # We may have a smiley actually, let's try that.'
            match = _SMILEY_URL.search(url)
            if match is not None:
                return _SMILEYS[match[1]]

        tag = "img"
        if url.startswith("/storage/staff/"):
            tag = "adimg"
            url = url[15:]
        else:
            match = _CALC_URL.match(url)
            if match is not None:
                tag = "calc"
                url = match[1]

        attrs = []
        if "style" in el.attrib:
            css = _parse_css_statements(el.attrib["style"])

            if "width" in css or "height" in css:
                attrs.append(
                    el.attrib.get("width", "").removesuffix("px")
                    + "x"
                    + el.attrib.get("height", "").removesuffix("px"),
                )
            elif "image-rendering" in css:
                attrs.append("pixelated")

        if "class" in el.attrib:
            attrs.append(el.attrib["class"])

        start_tag = tag
        if attrs:
            start_tag += "=" + "|".join(attrs)

        return f"[{start_tag}]{url}[/{tag}]"

    if el.tag == "a":
        # Can be a link, a label or a target.
        if "name" in el.attrib:
            return f"[label={el.attrib['name']}]"

        if el.attrib["href"].startswith("#"):
            return _process_children(
                el,
                prefix=f"[target={el.attrib['href'][1:]}]",
                suffix="[/target]",
            )

        # NOTE: We do not try to reverse engineer [profil] tags here, and will
        #       produce [url] instead.
        return _process_children(
            el,
            prefix=f"[url={el.attrib['href']}]",
            suffix="[/url]",
        )

    if el.tag == "iframe":
        # Youtube videos. "src" attr is of the form
        # "https://www.youtube.com/embed/{code}", which should be reversed
        # to "https://youtu.be/{code}" or
        # "https://www.youtube.com/watch?v={code}".
        # Also, video width and height, which are placed into the "width" and
        # "height" attributes; default are:
        #
        # * For video: w=560, h=340
        # * For video tiny: w=470, h=300
        code_match = _YOUTUBE_EMBED_PATTERN.match(el.attrib.get("src", ""))
        if code_match is None:
            raise NotImplementedError()

        width = el.attrib.get("width")
        height = el.attrib.get("height")
        if height == "300":
            default_width = "470"
            start_tag = "video tiny"
            end_tag = "video tiny"
        else:
            default_width = "560"
            start_tag = "video"
            end_tag = "video"

        if width != default_width:
            start_tag += f"={width}"

        return (
            f"[{start_tag}]https://youtube.com/watch?v={code_match[1]}"
            + f"[/{end_tag}]"
        )

    if el.tag == "video":
        # Video tag.
        src = el.xpath("./source[1]")[0].attrib["src"]
        width = el.attrib.get("width")
        height = el.attrib.get("height")

        if height == "300":
            default_width = "470"
            start_tag = "video tiny"
            end_tag = "video tiny"
        else:
            default_width = "560"
            start_tag = "video"
            end_tag = "video"

        return f"[{start_tag}]{src}[/{end_tag}]"

    if el.tag == "p":
        return _process_children(el)

    if el.tag == "center":
        return _process_children(
            el,
            prefix="[center]",
            suffix="[/center]",
            force=True,
        )

    if el.tag == "b":
        return _process_children(el, prefix="[b]", suffix="[/b]")

    if el.tag == "i":
        return _process_children(el, prefix="[i]", suffix="[/i]")

    if el.tag == "u":
        return _process_children(el, prefix="[u]", suffix="[/u]")

    if el.tag == "strike":
        return _process_children(el, prefix="[strike]", suffix="[/strike]")

    if el.tag == "ol":
        return _process_children(el, prefix="[ol]", suffix="[/ol]", force=True)

    if el.tag == "ul":
        if el.attrib.get("class") == "arrow":
            return _process_children(
                el,
                prefix="[arrow]",
                suffix="[/arrow]",
                force=True,
            )

        return _process_children(
            el,
            prefix="[ul]",
            suffix="[/ul]",
            force=True,
        )

    if el.tag == "li":
        return _process_children(
            el,
            prefix="[li]",
            suffix="[/li]",
            force=True,
        )

    if el.tag == "table":
        return _process_children(
            el,
            prefix="[table]",
            suffix="[/table]",
            force=True,
        )

    if el.tag == "tr":
        return _process_children(
            el,
            prefix="[tr]",
            suffix="[/tr]",
            force=True,
        )

    if el.tag == "td":
        return _process_children(
            el,
            prefix="[td]",
            suffix="[/td]",
            force=True,
        )

    if el.tag == "th":
        return _process_children(
            el,
            prefix="[th]",
            suffix="[/th]",
            force=True,
        )

    if el.tag == "br":
        return "\n"

    raise NotImplementedError(
        f"Could not process the following element: {el!r}",
    )


def _process_els(
    els: Iterable[Element],
    /,
    *,
    prefix: str = "",
    suffix: str = "",
    force: bool = False,
) -> str:
    """Transform a list of elements into BBCode.

    :param el: Elements to process.
    :param prefix: Prefix to add.
    :param suffix: Suffix to add.
    :param force: Whether to force using the prefix and suffix if there is
        no subcontent.
    :return: Obtained BBCode.
    """
    content = "".join(_process_el(el) + _process_text(el.tail) for el in els)
    if not content and not force:
        return ""

    return prefix + content + suffix


def _process_children(
    el: Element,
    /,
    *,
    prefix: str = "",
    suffix: str = "",
    force: bool = False,
) -> str:
    """Transform children of the provided element into BBCode.

    :param el: Element for which to process the children.
    :param prefix: Prefix to add.
    :param suffix: Suffix to add.
    :param force: Whether to force using the prefix and suffix if there
        is no subcontent.
    :return: Obtained BBCode.
    """
    content = _process_text(el.text) + _process_els(el)
    if not content and not force:
        return ""

    return prefix + content + suffix


def transform_html_to_bbcode(content: Element | list[Element], /) -> str:
    """Reverse engineer BBCode from produced HTML.

    :param content: HTML element or elements to parse.
    :return: Obtained BBCode.
    """
    if isinstance(content, list):
        result = "".join(
            _process_el(el) + _process_text(el.tail) for el in content
        )
    else:
        result = _process_el(content) + _process_text(content.tail)

    return _NEWLINE.sub("\n", result).strip()
