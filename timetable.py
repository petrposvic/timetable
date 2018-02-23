#!/usr/bin/python3

import collections
import configparser
import datetime
import json
import sys
import tkinter

def formatTime(time):
    s = str(time).split(".")
    s[1] = str(int(6 * int(s[1]) / 10))
    if (len(s[0]) < 2):
        s[0] = "0" + s[0]
    if (len(s[1]) < 2):
        s[1] = s[1] + "0"
    return "{}:{}".format(s[0], s[1])

def createTimetableWindow(root, config, days, colors):
    window_width = int(config["PADDING"]["left"]) + len(days) * int(config["DAY"]["width"])

    canvas = tkinter.Canvas(root, width=window_width, height=850, bg="white")
    canvas.pack()

    timeline = {}
    for i, day in enumerate(days):
        x = int(config["PADDING"]["left"]) + i * int(config["DAY"]["width"])
        y = 0
        canvas.create_text(x + int(config["PADDING"]["text"]), y + int(config["PADDING"]["text"]), text=day.name, anchor=tkinter.NW)
        y = (day.start - float(config["DAY"]["start"])) * int(config["HOUR"]["height"])
        time = day.start

        hours = {}
        for lesson in day.lessons:
            try:
                bgColor = colors[lesson.name]["bg"]
            except KeyError:
                bgColor = colors["bg"]
            try:
                fgColor = colors[lesson.name]["fg"]
            except KeyError:
                fgColor = colors["fg"]

            canvas.create_rectangle(x, y, x + int(config["DAY"]["width"]) - 2, y + lesson.duration * int(config["HOUR"]["height"]) - 2, fill=bgColor)
            canvas.create_text(x + int(config["PADDING"]["text"]), y + int(config["PADDING"]["text"]), text="{} ({}h)".format(lesson.name, lesson.duration), anchor=tkinter.NW, fill=fgColor)
            y += lesson.duration * int(config["HOUR"]["height"])

            # Sumarize duration
            if (lesson.name in hours):
                hours[lesson.name] += lesson.duration
            else:
                hours[lesson.name] = lesson.duration
            
            # Compute hours
            timeline[time] = formatTime(time)
            time += lesson.duration
            timeline[time] = formatTime(time)

        print(day.name)
        for hour in hours:
            print("- {}: {}".format(hour, hours[hour]))

    # Show line on current time
    now = datetime.datetime.now()
    y = (now.hour - float(config["DAY"]["start"]) + (now.minute / 60.0)) * int(config["HOUR"]["height"])
    canvas.create_line(0, y, window_width, y, fill="red", dash=(1, 3))

    for hour in timeline:
        y = (hour - float(config["DAY"]["start"])) * int(config["HOUR"]["height"])
        canvas.create_text(10, y, text=timeline[hour], anchor=tkinter.NW)
        canvas.create_line(10, y, window_width, y, fill="black", dash=(1,10))

def createColors(filename):
    colors = {}
    with open(filename) as data:
        data = json.load(data)
        colors["bg"] = data["bg"]
        colors["fg"] = data["fg"]
        for lesson in data["lessons"]:
            colors[lesson] = {}
            try:
                colors[lesson]["bg"] = data["lessons"][lesson]["bg"]
            except KeyError:
                colors[lesson]["bg"] = data["bg"]
            try:
                colors[lesson]["fg"] = data["lessons"][lesson]["fg"]
            except KeyError:
                colors[lesson]["fg"] = data["fg"]
    return colors

if (__name__ == "__main__"):
    if (len(sys.argv) != 3):
        print("Usage: {} my-timetable.json my-colors.json".format(sys.argv[0]))
        exit(1)

    timetableFile = sys.argv[1]
    colorsFile = sys.argv[2]

    with open(timetableFile) as data:
        days = json.load(data, object_hook=lambda d: collections.namedtuple('X', d.keys())(*d.values()))

        root = tkinter.Tk()
        root.title("Timetable")

        config = configparser.ConfigParser()
        config.read("timetable.ini")
        createTimetableWindow(
            root, config,
            days,
            createColors(colorsFile)
        )

        root.mainloop()
