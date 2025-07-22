from pytest import fixture
from superdesk.media.image import read_metadata
from superdesk.media.video import get_xmp_tags, convert_xmp_to_args, write_xmp_with_exiftool

from .. import fixture_path

@fixture
def video_binary() -> bytes:
    image_path = fixture_path("cp.mov", "media")
    with open(image_path, mode="rb") as f:
        return f.read()

def test_picture_metadata_read_write(video_binary) -> None:
    metadata = read_metadata(video_binary)
    xmp = get_xmp_tags(metadata)

    assert xmp == {
        "Description": "Your Description Here",
        "Headline": "Your Headline",
        "City": "Your City",
        "Country": "Your Country",
        "CountryCode": "US",
        "Creator": "Your Creator Name",
        "AuthorsPosition": "Your Job Title",
        "TransmissionReference": "Your Job ID",
        "Instructions": "Your Instructions",
        "Title": "Your Title",
        "Rights": "Your Copyright Notice",
        "Credit": "Your Credit Line",
        "State": "Your Province or State",
        "CaptionWriter": "Your Caption Writer",
    }

    updated = {
        "Description": "Your Description Here 1",
        "Headline": "Your Headline 2",
        "City": "Your City 3",
        "Country": "Your Country 4",
        "CountryCode": "US 5",
        "Creator": "Your Creator Name 6",
        "AuthorsPosition": "Your Job Title 7",
        "TransmissionReference": "Your Job ID 8",
        "Instructions": "Your Instructions 9",
        "Title": "Your Title 10",
        "Rights": "Your Copyright Notice 11",
        "Credit": "Your Credit Line 12",
        "State": "Your Province or State 13",
        "CaptionWriter": "Your Caption Writer 14",
    }
    args = convert_xmp_to_args(updated)
    next_video = write_xmp_with_exiftool(video_binary, args)
    metadata = get_xmp_tags(read_metadata(next_video))

    assert metadata == updated