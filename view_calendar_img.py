from PIL import Image, ImageDraw, ImageFont
from datetime import date
import calendar


def weekly_agenda(tasks, start_day=0, get_config=lambda x, d: d, today=None):
    background_colour = get_config("cal_background_colour", "#0000")
    border_colour = get_config("cal_border_colour", "#808f")
    border_colour_current = get_config("cal_border_colour_current", "#080f")
    text_colour = get_config("cal_text_colour", "#888f")
    border_width = get_config("cal_border_width", 2)

    im_width = get_config("cal_image_width", 640)
    im_height = get_config("cal_image_height", 480)

    # get a font
    fnt = ImageFont.load_default()

    weekdays = list(calendar.day_name)
    if today is None:
        today = date.today()
        print(today.weekday())
        print()

    with Image.new(mode="RGBA", size=(im_width, im_height), color=background_colour) as im:
        d = ImageDraw.Draw(im)
        # d.line((0, 0) + im.size, fill=border_colour, width=5)
        # d.line((0, im.size[1], im.size[0], 0), fill=border_colour, width=5)
        for i in range(7):
            top_left = (im_width / 7 * i, 0)
            bottom_right = (im_width / 7 * (i + 1), im_height)
            d.rectangle([top_left, bottom_right], outline=border_colour, width=border_width)
            agenda_count = 0
            for agenda_item in tasks[i]:
                d.multiline_text((top_left[0] + 10, top_left[1] + 10 + (20 * agenda_count)), agenda_item, font=fnt,
                                 fill=text_colour)
                agenda_count += 1
        im.show()


if __name__ == '__main__':
    weekly_agenda([
        ["blah", "bluh"],
        ["blah", "bluh"],
        ["blah", "bluh"],
        ["blah", "bluh"],
        ["blah", "bluh"],
        ["blah", "bluh"],
        ["blah", "bluh"]
    ])
