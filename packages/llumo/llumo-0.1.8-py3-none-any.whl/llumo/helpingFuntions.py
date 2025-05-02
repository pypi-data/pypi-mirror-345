import time
import uuid
import numpy as np

def getProcessID():
    return f"{int(time.time() * 1000)}{uuid.uuid4()}"


def getInputPopulatedPrompt(promptTemplate, tempObj):
    for key, value in tempObj.items():
        promptTemplate = promptTemplate.replace(f"{{{{{key}}}}}", value)
    return promptTemplate

def costColumnMapping(costResults, allProcess):
    # this dict will store cost column data for each row
    cost_cols = {}

    compressed_prompt = []
    compressed_prompt_output = []
    cost = []
    cost_saving = []

    for record in allProcess:
        cost_cols[record] = []
        for item in costResults:
            if list(item.keys())[0].split("-")[0] == record.split("-")[0]:
                cost_cols[record].append(list(item.values())[0])

    for ky, val in cost_cols.items():
        try:
            compressed_prompt.append(val[0])
        except IndexError:
            compressed_prompt.append("error occured")

        try:
            compressed_prompt_output.append(val[1])
        except IndexError:
            compressed_prompt_output.append("error occured")

        try:
            cost.append(val[2])
        except IndexError:
            cost.append("error occured")

        try:
            cost_saving.append(val[3])
        except IndexError:
            cost_saving.append("error occured")

    return compressed_prompt, compressed_prompt_output, cost, cost_saving
