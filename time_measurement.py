from datetime import datetime


def measure_time(start, action_name):
    diff = datetime.now() - start
    seconds = diff.seconds + diff.days * 86400
    print(action_name +
          f" completed in {seconds // 60 // 60} hours, {seconds // 60 % 60} minutes, {seconds % 60} seconds")
