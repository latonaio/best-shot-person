#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) Latona. All rights reserved.

import datetime as dt
import os
import sys
from glob import glob
from re import split
from time import sleep

import simplejson as json
from StatusJsonPythonModule import StatusJsonRest
from aion.logger_library.LoggerClient import LoggerClient

log = LoggerClient("BestShotPerson")

BEST_SHOT_THRESHOLD = 0.4
MAX_NUMBER_OF_PICTURE = 50
TIME_INTERVAL_TO_CHOISE_BY_SEC = 5
JSON_INTERVAL_TO_SKIP = 10
OBJECT_TO_CHOISE = "person"


class BestShotPerson():
    @log.function_log
    def __init__(self, object_json_path):
        if not os.path.isdir(object_json_path):
            log.print("Error: transcript data is None")
            sys.exit(1)

        self.object_json_path = object_json_path
        self.before_time = dt.datetime(dt.MINYEAR, 1, 1)

    def _getDatetimeFromFileName(self, fname):
        return dt.datetime.strptime(split("[/.]", fname)[-2], "XXXXXXXXXX")

    def choise_best_shot(self):
        flist = [
            [x, self._getDatetimeFromFileName(x)]
            for x in glob(os.path.join(self.object_json_path, "*.json"))]

        nflist = [x for x in flist if x[1] > self.before_time][::JSON_INTERVAL_TO_SKIP]
        if flist:
            self.before_time = max(flist, key=lambda x: x[1])[1]

        if not nflist:
            return None

        picture_list = []
        for x in nflist:
            with open(x[0], "r") as f:
                try:
                    df = json.load(f)
                except json.JSONDecodeError:
                    continue

                if not df.get("result"): continue
                for object_data in df["result"]:
                    if (object_data.get("object") == OBJECT_TO_CHOISE
                            and object_data.get("rate") > BEST_SHOT_THRESHOLD):
                        boxes = object_data.get("boxes")
                        picture_list.append({
                            "picture_file_name": df.get("filename"),
                            "timestamp": df.get("timestamp"),
                            "rate": object_data.get("rate"),
                            "coordinate": {
                                "x": boxes[0],
                                "y": boxes[1],
                                "width": boxes[2],
                                "height": boxes[3]
                            }
                        })

        sort_list = sorted(
            picture_list, reverse=True,
            key=lambda x: x["rate"])[:MAX_NUMBER_OF_PICTURE]

        tmp = {}
        for data in sort_list:
            filename = data["picture_file_name"]
            if filename not in tmp.keys():
                tmp[filename] = []
            tmp[filename].append(data["coordinate"])

        ret = []
        for k, v in tmp.items():
            ret.append({
                "picture_file_name": k,
                "coordinates": v
            })

        return ret

@log.function_log
def main():
    # read status json file
    statusObj = StatusJsonRest.StatusJsonRest(os.getcwd(), __file__)
    statusObj.initializeInputStatusJson()

    object_json_path = statusObj.getInputFileNameFromJson()
    selectClassObj = BestShotPerson(object_json_path)

    statusObj.initializeOutputStatusJson()
    statusObj.copyToOutputJsonFromInputJson()
    """
    statusObj.setNextService(
        "ShowRectInBestShot",
        "/home/latona/athena/Runtime/show-rect-in-best-shot",
        "python", "main.py", "athena")

    statusObj.setNextService(
        "TrimFace",
        "/home/latona/athena/Runtime/trimface",
        "python", "main.py", "athena")
    """
    log.print(">>> start: chose best shot of person")
    while True:
        statusObj.resetOutputJsonFile()

        picture_list = selectClassObj.choise_best_shot()

        if picture_list:
            statusObj.setMetadataValue("pictures", picture_list)
            statusObj.setMetadataValue("device_name", 'demeter')
            statusObj.outputJsonFile()
            log.print("> Success: best shots are choised")
        else:
            log.print("> There is no best shot picture. skip")

        sleep(TIME_INTERVAL_TO_CHOISE_BY_SEC)


if __name__ == "__main__":
    main()
