import time
import pickle
import os
import pandas as pd
from datetime import date
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(handlers=[RotatingFileHandler('cto_trainee_matching_log.log', maxBytes=100000, backupCount=5)], level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(message)s',force=True)
logger=logging.getLogger(__name__)

#Create the possible schedule combinations. Each schedule is a binary array representing a 2 week period from Sunday to Saturday. 0 is not working, 1 is working. Dayshift and Graveyard schedules are identical, so only Graveyard names are used as keys.
schedules = {}
schedules['GY01'] = [0,1,1,1,1,0,0,0,1,1,1,0,0,0]
schedules['GY02'] = [0,1,1,1,1,0,0,0,0,1,1,1,0,0]
schedules['GY03'] = [0,0,1,1,1,1,0,0,0,1,1,1,0,0]
schedules['GY04'] = [0,0,1,1,1,1,0,0,0,0,1,1,1,0]
schedules['GY05'] = [0,0,0,1,1,1,1,0,0,0,1,1,1,0]
schedules['GY06'] = [0,0,0,1,1,1,1,0,0,0,0,1,1,1]
schedules['GY07'] = [0,0,0,0,1,1,1,1,0,0,0,1,1,1]
schedules['GY08'] = [1,0,0,0,0,1,1,1,0,0,0,1,1,1]
schedules['GY09'] = [1,0,0,0,0,1,1,1,1,0,0,0,1,1]
schedules['GY10'] = [1,1,0,0,0,0,1,1,1,0,0,0,1,1]
schedules['GY11'] = [1,1,0,0,0,0,1,1,1,1,0,0,0,1]
schedules['GY12'] = [1,1,1,0,0,0,0,1,1,1,0,0,0,1]
schedules['GY13'] = [1,1,1,0,0,0,0,1,1,1,1,0,0,0]
schedules['GY14'] = [1,1,1,1,0,0,0,0,1,1,1,0,0,0]
schedules['PS01'] = [0,1,1,1,1,0,0,0,1,1,1,0,0,0]
schedules['PS02'] = [0,0,1,1,1,1,0,0,0,1,1,1,0,0]
schedules['PS03'] = [0,0,0,1,1,1,1,0,0,0,1,1,1,0]
schedules['PS04'] = [0,0,0,0,1,1,1,1,0,0,0,1,1,1]
schedules['PS05'] = [1,0,0,0,0,1,1,1,0,0,0,1,1,1]
schedules['PS06'] = [1,1,0,0,0,0,1,1,1,0,0,0,1,1]
schedules['PS07'] = [1,1,1,0,0,0,0,1,1,1,0,0,0,1]
schedules['PS08'] = [1,1,1,1,0,0,0,0,1,1,1,0,0,0]
schedules['SUN-MON'] = [0,0,1,1,1,1,1,0,0,1,1,1,1,1]
schedules['MON-TUES'] = [1,0,0,1,1,1,1,1,0,0,1,1,1,1]
schedules['TUES-WED'] = [1,1,0,0,1,1,1,1,1,0,0,1,1,1]
schedules['WED-THURS'] = [1,1,1,0,0,1,1,1,1,1,0,0,1,1]
schedules['THURS-FRI'] = [1,1,1,1,0,0,1,1,1,1,1,0,0,1]
schedules['FRI-SAT'] = [1,1,1,1,1,0,0,1,1,1,1,1,0,0]
schedules['SAT-SUN'] = [0,1,1,1,1,1,0,0,1,1,1,1,1,0]
schedules[0] = []

cto_list = []
trainee_list = []

#Define Employee class. The CTO and Trainee classes are child classes of Employee
class Employee:
    def __init__(self, firstName, lastName, shift, schedule, callTaking, police, fire, personality):
        self.firstName = firstName
        self.lastName = lastName
        self.shift = shift
        self.schedule = schedule
        self.calltaking = callTaking
        self.police = police
        self.fire = fire
        self.personality = personality
    #All of the attributes except name may need to be updated. Define all attributes as properties with a getter and setter. 
    @property
    def shift(self):
        logger.debug(f'Getting shift for {self.firstName} {self.lastName}')
        return self._shift
    @shift.setter
    def shift(self, newShift):
        logger.debug(f'Assigning new shift to {self.firstName} {self.lastName}')
        self._shift = newShift
        #All setters must also update the pickle file for the Object in order for the updated value to be retained.
        logger.debug(f'Updating pickle file for {self.firstName} {self.lastName}')
        employee_name = self.lastName + self.firstName
        file = open(employee_name, 'wb')
        pickle.dump(self, file)
        file.close()
    @property
    def schedule(self):
        logger.debug(f'Getting schedule for {self.firstName} {self.lastName}')
        return self._schedule
    @schedule.setter
    def schedule(self, newSchedule):
        logger.debug(f'Setting schedule to {newSchedule} for {self.firstName} {self.lastName}')
        self._schedule = newSchedule
        logger.debug(f'Updating pickle file for {self.firstName} {self.lastName}')
        employee_name = self.lastName + self.firstName
        file = open(employee_name, 'wb')
        pickle.dump(self, file)
        file.close()
    @property
    def calltaking(self):
        logger.debug(f'Getting call taking value for {self.firstName} {self.lastName}')
        return self._calltaking
    @calltaking.setter
    def calltaking(self, newValue):
        logger.debug(f'Setting call taking value to {newValue} for {self.firstName} {self.lastName}')
        self._calltaking = newValue
        logger.debug(f'Updating pickle file for {self.firstName} {self.lastName}')
        employee_name = self.lastName + self.firstName
        file = open(employee_name, 'wb')
        pickle.dump(self, file)
        file.close()
    @property
    def police(self):
        logger.debug(f'Getting police value for {self.firstName} {self.lastName}')
        return self._police
    @police.setter
    def police(self, newValue):
        logger.debug(f'Setting police value to {newValue} for {self.firstName} {self.lastName}')
        self._police = newValue
        logger.debug(f'Updating pickle file for {self.firstName} {self.lastName}')
        employee_name = self.lastName + self.firstName
        file = open(employee_name, 'wb')
        pickle.dump(self, file)
        file.close()
    @property
    def fire(self):
        logger.debug(f'Getting fire value for {self.firstName} {self.lastName}')
        return self._fire
    @fire.setter
    def fire(self, newValue):
        logger.debug(f'Setting fire value to {newValue} for {self.firstName} {self.lastName}')
        self._fire = newValue
        logger.debug(f'Updating pickle file for {self.firstName} {self.lastName}')
        employee_name = self.lastName + self.firstName
        file = open(employee_name, 'wb')
        pickle.dump(self, file)
        file.close()
    @property
    def personality(self):
        logger.debug(f'Getting personality for {self.firstName} {self.lastName}')
        return self._personality
    @personality.setter
    def personality(self, newValue):
        logger.debug(f'Setting personality to {newValue} for {self.firstName} {self.lastName}')
        self._personality = newValue
        logger.debug(f'Updating pickle file for {self.firstName} {self.lastName}')
        employee_name = self.lastName + self.firstName
        file = open(employee_name, 'wb')
        pickle.dump(self, file)
        file.close()
    def __str__(self):
        return f"Last Name: {self.lastName}, First Name: {self.firstName}\nShift: {self.shift}\nSchedule: {self.schedule}"

#Define CTO class as a child of the Employee class
class CTO(Employee):
    def __init__(self, firstName, lastName, shift, schedule, callTaking, police, fire, personality, partTime, skill, onBreak, assigned = 0):
        super().__init__(firstName, lastName, shift, schedule, callTaking, police, fire, personality)
        self.partTime = partTime
        self.skill = skill
        self.onBreak = onBreak
        self.assigned = assigned
        cto_list.append(self)
        loaded_list.append(self)
    @property
    def onBreak(self):
        return self._onBreak
    @onBreak.setter
    def onBreak(self, newValue):
        self._onBreak = newValue
        logger.debug(f'Updating pickle file for {self.firstName} {self.lastName}')
        employee_name = self.lastName + self.firstName
        file = open(employee_name, 'wb')
        pickle.dump(self, file)
        file.close()
    def toggle_break(self):
        newValue = 1
        if self.onBreak == 1:
            newValue = 0
        self.onBreak = newValue
    def updateSkill(self, newSkill):
        self.skill = newSkill
        logger.debug(f'Updating pickle file for {self.firstName} {self.lastName}')
        employee_name = self.lastName + self.firstName
        file = open(employee_name, 'wb')
        pickle.dump(self, file)
        file.close()
    @property
    def assigned(self):
        logger.debug(f'Getting assigned value for {self.firstName} {self.lastName}')
        return self._assigned
    @assigned.setter
    def assigned(self, newValue):
        logger.debug(f'Setting assigned value to {newValue} for {self.firstName} {self.lastName}')
        self._assigned = newValue
    def toggleAssigned(self, newValue):
        logger.debug(f'Starting toggleAssigned for {self.firstName} {self.lastName}')
        self.assigned = newValue
        logger.debug(f'Updating pickle file for {self.firstName} {self.lastName}')
        employee_name = self.lastName + self.firstName
        file = open(employee_name, 'wb')
        pickle.dump(self, file)
        file.close()

#Define Trainee class as a child of the Employee class
class Trainee(Employee):
    def __init__(self, firstName, lastName, shift, schedule, callTaking, police, fire, personality, minSkill):
        super().__init__(firstName, lastName, shift, schedule, callTaking, police, fire, personality)
        self.minSkill = minSkill
        trainee_list.append(self)
        loaded_list.append(self)
    @property
    def minSkill(self):
        logger.debug(f'Getting minSkill value for {self.firstName} {self.lastName}')
        return self._minSkill
    @minSkill.setter
    def minSkill(self, newValue):
        logger.debug(f'Setting new minSkill value to {newValue} for {self.firstName} {self.lastName}')
        self._minSkill = newValue
        logger.debug(f'Updating pickle file for {self.firstName} {self.lastName}')
        employee_name = self.lastName + self.firstName
        file = open(employee_name, 'wb')
        pickle.dump(self, file)
        file.close()

def create_employee():
    #Function to take user inputs and create an object of either the CTO or Trainee class
    logger.debug('Starting create_employee')
    selection = 0
    try:
        selection = int(input('If the employee is a CTO, enter 1\nIf the employee is a trainee, enter 2\n'))
        if selection not in [1,2]:
            raise ValueError
    except ValueError:
        logger.exception(f'Invalid selection. Entered value was {selection}.')
        print('Please enter only 1 or 2')
        return 0
    first_name = input('Enter their first name.\n').strip().title()
    last_name = input('Enter their last name.\n').strip().title()
    shift = ""
    while not isinstance(shift,int):
        try:
            shift = int(input('Enter their shift:\nDays = 1\nGraves = 2\nPower = 3\nIf none, enter 0\n'))
        except ValueError:
            print('Please enter only 0, 1, 2, or 3.\n')
            time.sleep(2)
    schedule = input('Enter their assigned schedule.\nFor CTOs, enter their assigned position (i.e. GY01)\nFor trainees enter their days off (i.e. Mon-Tues)\nIf no assigned schedule, enter 0\n').upper().strip()
    if schedule[:2] == 'DS':
        schedule = schedule.replace('DS','GY')
        logger.debug(f'Entered schedule: {schedule}')
    calltaking = int(input('Are they signed off on call taking?\nEnter 1 for Yes and 0 for No.\n'))
    if calltaking == 1:
        police = int(input('Are they signed off on police?\nEnter 1 for Yes and 0 for No.\n').strip())
        fire = int(input('Are they signed off on fire?\nEnter 1 for Yes and 0 for No.\n').strip())
    else:
        police = 0
        fire = 0
    personality = input('Enter their personality type.\n').lower().strip()
    if selection == 1:
        partTime = int(input('Are they a fill in CTO or currently on a break?\nEnter 1 for Yes and 0 for No.\n'))
        skill = int(input('Enter their CTO skill level.\n1 = Lower skill/experience\n2 = Normal\n3 = Skilled/Highly Experienced\n'))
        assigned = int(input('Are they currently assigned a trainee?\nEnter 1 for Yes and 0 for No.\n'))
        onBreak = partTime
        cto_name = last_name + first_name[0]
        try:
            schedule = schedules[schedule]
        except KeyError as err:
            logger.exception(err)
            schedule = 0
        cto_name = CTO(first_name,last_name,shift,schedule,calltaking,police,fire,personality,partTime,skill,onBreak,assigned)
        return cto_name
    if selection == 2:
        minSkill = int(input('Enter the required minimum skill level for their assigned CTOs.\n1 = Lower skill/experience\n2 = Normal\n3 = Skilled/Highly Experienced\n'))
        trainee_name = last_name + first_name[0]
        try:
            schedule = schedules[schedule]
        except KeyError as err:
            logger.exception(err)
            schedule = 0
        trainee_name = Trainee(first_name,last_name,shift,schedule,calltaking,police,fire,personality,minSkill)
        return trainee_name


def match_trainee_to_any(trainee, discipline):
    #Function to match a trainee to any CTO regardless of shift
    logger.debug(f'Starting match_trainee_to_any with inputs:\n {trainee} and {discipline}\n')
    options = []
    ideal_list = []
    last_choice = []
    matches = []
    cto_matches = {}
    for cto in cto_list:
        logger.debug(f'Considering CTO {cto.firstName} {cto.lastName}')
        if cto.assigned == 0 and getattr(cto,discipline) == 1:
            logger.debug(f'Matches discipline: {cto.firstName} {cto.lastName}')
            if cto.skill >= trainee.minSkill and cto.personality == trainee.personality and cto.onBreak == 0:
                logger.debug(f'Adding {cto.firstName} {cto.lastName} to ideal list')
                ideal_list.append(cto)
            elif cto.skill >= trainee.minSkill and cto.onBreak == 0:
                logger.debug(f'Adding {cto.firstName} {cto.lastName} to options list')
                options.append(cto)
            else:
                last_choice.append(cto)
    if len(ideal_list) == 0 and len(options) == 0 and len(last_choice) == 0:
        return f'No matches found for {trainee.firstName} {trainee.lastName}'
    if len(ideal_list) > 1:
        for cto in ideal_list:
            logger.debug(f'Checking ideal list CTO {cto.firstName} {cto.lastName}')
            schedule1 = cto.schedule
            cto_shift = cto.shift
            for second in ideal_list:
                logger.debug(f'Looking for matches with CTO {second.firstName} {second.lastName}')
                if second != cto:
                    logger.debug(f'Comparing shifts: {cto_shift} {second.shift}')
                    if second.shift == cto_shift:
                        logger.debug('CTO shifts match, checking schedules')
                        schedule2 = second.schedule
                        i = 0
                        week1_schedule = []
                        week2_schedule = []
                        days_in_a_row = 0
                        while i < 7:
                            week1_schedule.append(schedule1[i] + schedule2[i])
                            i +=1
                        while i < 14:
                            week2_schedule.append(schedule1[i] + schedule2[i])
                            i += 1
                        logger.debug(f'Test Schedule: {week1_schedule}{week2_schedule}')
                        for day in week1_schedule:
                            if day == 0 and days_in_a_row < 5:
                                days_in_a_row = 0
                            elif day >= 1:
                                days_in_a_row += 1
                        if days_in_a_row >= 5:
                            days_in_a_row = 0
                            for day in week2_schedule:
                                if day == 0 and days_in_a_row < 5:
                                    days_in_a_row = 0
                                elif day >= 1:
                                    days_in_a_row += 1
                            if days_in_a_row >= 5:
                                match_name = f'Ideal Match: {cto.firstName} {cto.lastName}, {second.firstName} {second.lastName}'
                                alt_match_name = f'Ideal Match: {second.firstName} {second.lastName}, {cto.firstName} {cto.lastName}'
                                if (match_name not in matches) and (alt_match_name not in matches):
                                    matches.append(match_name)
                                    cto_matches[match_name] = [cto, second]
    for option in ideal_list:
        logger.debug(f'Checking ideal list CTO: {option.firstName} {option.lastName}')
        schedule1 = option.schedule
        cto_shift = option.shift
        for second in options:
            logger.debug(f'Checking other CTO: {second.firstName} {second.lastName}')
            if second != option:
                logger.debug(f'Comparing shifts: {cto_shift} {second.shift}')
                if second.shift == cto_shift:
                    logger.debug('CTO shifts match, checking schedules')
                    schedule2 = second.schedule
                    i = 0
                    week1_schedule = []
                    week2_schedule = []
                    days_in_a_row = 0
                    while i < 7:
                        week1_schedule.append(schedule1[i] + schedule2[i])
                        i +=1
                    while i < 14:
                        week2_schedule.append(schedule1[i] + schedule2[i])
                        i += 1
                    logger.debug(f'Test Schedule: {week1_schedule}{week2_schedule}')
                    for day in week1_schedule:
                        if day == 0 and days_in_a_row < 5:
                            days_in_a_row = 0
                        elif day >= 1:
                            days_in_a_row += 1
                    if days_in_a_row >= 5:
                        days_in_a_row = 0
                        for day in week2_schedule:
                            if day == 0 and days_in_a_row < 5:
                                days_in_a_row = 0
                            elif day >= 1:
                                days_in_a_row += 1
                        if days_in_a_row >= 5:
                            match_name = f'One Ideal CTO: {option.firstName} {option.lastName}, {second.firstName} {second.lastName}'
                            alt_match_name = f'One Ideal CTO: {second.firstName} {second.lastName}, {option.firstName} {option.lastName}'
                            ideal_match = f'Ideal Match: {cto.firstName} {cto.lastName}, {second.firstName} {second.lastName}'
                            if (match_name not in matches) and (alt_match_name not in matches) and (ideal_match not in matches):
                                matches.append(match_name)
                                cto_matches[match_name] = [option, second]
    for option in options:
        logger.debug(f'Checking non-ideal CTO {option.firstName} {option.lastName}')
        schedule1 = option.schedule
        cto_shift = option.shift
        for second in cto_list:
            logger.debug(f'Checking CTO {second.firstName} {second.lastName}')
            logger.debug(f'Comparing shifts: {cto_shift} {second.shift}')
            if second != option and (second.shift == cto_shift):
                logger.debug('CTO shifts match, checking schedules')
                schedule2 = second.schedule
                i = 0
                week1_schedule = []
                week2_schedule = []
                days_in_a_row = 0
                while i < 7:
                    week1_schedule.append(schedule1[i] + schedule2[i])
                    i +=1
                while i < 14:
                    week2_schedule.append(schedule1[i] + schedule2[i])
                    i +=1
                logger.debug(f'Test Schedule: {week1_schedule}{week2_schedule}')
                for day in week1_schedule:
                    if day == 0 and days_in_a_row < 5:
                        days_in_a_row = 0
                    elif day >= 1:
                        days_in_a_row += 1
                if days_in_a_row >= 5:
                    days_in_a_row = 0
                    for day in week2_schedule:
                        if day == 0 and days_in_a_row < 5:
                            days_in_a_row = 0
                        elif day >= 1:
                            days_in_a_row += 1
                    if days_in_a_row >= 5:
                        match_name = f'Match: {option.firstName} {option.lastName}, {second.firstName} {second.lastName}'
                        alt_match_name = f'Match: {second.firstName} {second.lastName}, {option.firstName} {option.lastName}'
                        ideal_match = f'One Ideal CTO: {option.firstName} {option.lastName}, {second.firstName} {second.lastName}'
                        if (match_name not in matches) and (alt_match_name not in matches) and (ideal_match not in matches):
                            matches.append(match_name)
                            cto_matches[match_name] = [option, second]
    return matches, cto_matches

def match_trainee_to_specific_shift(trainee, discipline):
    #Function to match a trainee to a CTO on the trainee's currenlty assigned shift
    logger.debug(f'Starting match_trainee_to_specific_shift with inputs:\n {trainee} and {discipline}\n')
    options = []
    ideal_list = []
    last_choice = []
    matches = []
    cto_matches = {}
    for cto in cto_list:
        logger.debug(f'Considering CTO {cto.firstName} {cto.lastName}')
        if cto.assigned == 0 and getattr(cto,discipline) == 1 and cto.shift == trainee.shift:
            logger.debug(f'Matches discipline & shift: {cto.firstName} {cto.lastName}')
            if cto.skill >= trainee.minSkill and cto.personality == trainee.personality and cto.onBreak == 0:
                logger.debug(f'Adding {cto.firstName} {cto.lastName} to ideal list')
                ideal_list.append(cto)
            elif cto.skill >= trainee.minSkill and cto.onBreak == 0:
                logger.debug(f'Adding {cto.firstName} {cto.lastName} to options list')
                options.append(cto)
            else:
                last_choice.append(cto)
    if len(ideal_list) == 0 and len(options) == 0 and len(last_choice) == 0:
        return f'No matches found for {trainee.firstName} {trainee.lastName}'
    if len(ideal_list) > 1:
        for cto in ideal_list:
            logger.debug(f'Checking ideal list CTO {cto.firstName} {cto.lastName}')
            schedule1 = cto.schedule
            cto_shift = cto.shift
            for second in ideal_list:
                logger.debug(f'Looking for matches with CTO {second.firstName} {second.lastName}')
                if second != cto:
                    logger.debug(f'Comparing shifts: {cto_shift} {second.shift}')
                    if second.shift == cto_shift:
                        logger.debug('CTO shifts match, checking schedules')
                        schedule2 = second.schedule
                        i = 0
                        week1_schedule = []
                        week2_schedule = []
                        days_in_a_row = 0
                        while i < 7:
                            week1_schedule.append(schedule1[i] + schedule2[i])
                            i +=1
                        while i < 14:
                            week2_schedule.append(schedule1[i] + schedule2[i])
                            i += 1
                        logger.debug(f'Test Schedule: {week1_schedule}{week2_schedule}')
                        for day in week1_schedule:
                            if day == 0 and days_in_a_row < 5:
                                days_in_a_row = 0
                            elif day >= 1:
                                days_in_a_row += 1
                        if days_in_a_row >= 5:
                            days_in_a_row = 0
                            for day in week2_schedule:
                                if day == 0 and days_in_a_row < 5:
                                    days_in_a_row = 0
                                elif day >= 1:
                                    days_in_a_row += 1
                            if days_in_a_row >= 5:
                                match_name = f'Ideal Match: {cto.firstName} {cto.lastName}, {second.firstName} {second.lastName}'
                                alt_match_name = f'Ideal Match: {second.firstName} {second.lastName}, {cto.firstName} {cto.lastName}'
                                if (match_name not in matches) and (alt_match_name not in matches):
                                    matches.append(match_name)
                                    cto_matches[match_name] = [cto, second]
    for option in ideal_list:
        logger.debug(f'Checking ideal list CTO: {option.firstName} {option.lastName}')
        schedule1 = option.schedule
        cto_shift = option.shift
        for second in options:
            logger.debug(f'Checking other CTO: {second.firstName} {second.lastName}')
            if second != option:
                logger.debug(f'Comparing shifts: {cto_shift} {second.shift}')
                if second.shift == cto_shift:
                    logger.debug('CTO shifts match, checking schedules')
                    schedule2 = second.schedule
                    i = 0
                    week1_schedule = []
                    week2_schedule = []
                    days_in_a_row = 0
                    while i < 7:
                        week1_schedule.append(schedule1[i] + schedule2[i])
                        i +=1
                    while i < 14:
                        week2_schedule.append(schedule1[i] + schedule2[i])
                        i += 1
                    logger.debug(f'Test Schedule: {week1_schedule}{week2_schedule}')
                    for day in week1_schedule:
                        if day == 0 and days_in_a_row < 5:
                            days_in_a_row = 0
                        elif day >= 1:
                            days_in_a_row += 1
                    if days_in_a_row >= 5:
                        days_in_a_row = 0
                        for day in week2_schedule:
                            if day == 0 and days_in_a_row < 5:
                                days_in_a_row = 0
                            elif day >= 1:
                                days_in_a_row += 1
                        if days_in_a_row >= 5:
                            match_name = f'One Ideal CTO: {option.firstName} {option.lastName}, {second.firstName} {second.lastName}'
                            alt_match_name = f'One Ideal CTO: {second.firstName} {second.lastName}, {option.firstName} {option.lastName}'
                            ideal_match = f'Ideal Match: {cto.firstName} {cto.lastName}, {second.firstName} {second.lastName}'
                            if (match_name not in matches) and (alt_match_name not in matches) and (ideal_match not in matches):
                                matches.append(match_name)
                                cto_matches[match_name] = [option, second]
    for option in options:
        logger.debug(f'Checking non-ideal CTO {option.firstName} {option.lastName}')
        schedule1 = option.schedule
        cto_shift = option.shift
        for second in cto_list:
            logger.debug(f'Checking CTO {second.firstName} {second.lastName}')
            logger.debug(f'Comparing shifts: {cto_shift} {second.shift}')
            if second != option and (second.shift == cto_shift):
                logger.debug('CTO shifts match, checking schedules')
                schedule2 = second.schedule
                i = 0
                week1_schedule = []
                week2_schedule = []
                days_in_a_row = 0
                while i < 7:
                    week1_schedule.append(schedule1[i] + schedule2[i])
                    i +=1
                while i < 14:
                    week2_schedule.append(schedule1[i] + schedule2[i])
                    i +=1
                logger.debug(f'Test Schedule: {week1_schedule}{week2_schedule}')
                for day in week1_schedule:
                    if day == 0 and days_in_a_row < 5:
                        days_in_a_row = 0
                    elif day >= 1:
                        days_in_a_row += 1
                if days_in_a_row >= 5:
                    days_in_a_row = 0
                    for day in week2_schedule:
                        if day == 0 and days_in_a_row < 5:
                            days_in_a_row = 0
                        elif day >= 1:
                            days_in_a_row += 1
                    if days_in_a_row >= 5:
                        match_name = f'Match: {option.firstName} {option.lastName}, {second.firstName} {second.lastName}'
                        alt_match_name = f'Match: {second.firstName} {second.lastName}, {option.firstName} {option.lastName}'
                        ideal_match = f'One Ideal CTO: {option.firstName} {option.lastName}, {second.firstName} {second.lastName}'
                        if (match_name not in matches) and (alt_match_name not in matches) and (ideal_match not in matches):
                            matches.append(match_name)
                            cto_matches[match_name] = [option, second]
    return matches, cto_matches

def startup():
    #Function to take input then perform an action in the while loop defined below
    choice = int(input('\nWhat would you like to do?\n1 = Create New Employee\n2 = Match a Trainee to a CTO \n3 = Update Employee\n8 = Create Report of Existing Employees\n9 = Exit\n'))
    return choice

if __name__ == "__main__":
    choice = 0
    employee_list = []
    loaded_list = []
    try:
        with open('existing_employees.txt', 'r') as f:
            data = f.readlines()
            employee_list.extend(data)
    except:
        pass
    logger.debug(f'Initializing employees {employee_list}')
    for name in employee_list:
        name = name.strip()
        try:
            file = open(name, 'rb')
            name = pickle.load(file)
            if isinstance(name, CTO):
                cto_list.append(name)
            if isinstance(name, Trainee):
                trainee_list.append(name)
            loaded_list.append(name)
            file.close()
        except FileNotFoundError as err:
            logger.exception(err)
            logger.debug(f'Removing {name}')
            employee_list.remove(name+'\n')
            with open('existing_employees.txt', 'w') as list_file:
                list_file.write(''.join(employee_list)+'\n')
    while choice == 0:
        choice = startup()
        while choice != 0:
            #Create employee
            if choice == 1:
                employee = create_employee()
                try:
                    employee_name = employee.lastName + employee.firstName
                    file = open(employee_name, 'wb')
                    pickle.dump(employee, file)
                    file.close()
                    with open('existing_employees.txt', 'a') as list_file:
                        list_file.writelines(f'{employee_name}\n')
                    print(f'\nSuccessfully created {employee.firstName} {employee.lastName}\n')
                    time.sleep(2)
                    choice = 0
                except (ValueError, AttributeError):
                    choice = 0
            if choice == 9:
                exit()
            #Match a trainee to a CTO
            if choice == 2:
                print('\nMatch trainee to CTOs\n')
                match_type = 0
                while match_type not in [1,2,9]:
                    #Start while loop to get input and direct the app to the correct logic tree
                    match_type = int(input("1 = Match trainee to CTO on any shift\n2 = Match Trainee to CTO on the Trainee's Currently Assigned Shift\n9 = Return to Main Menu\n"))
                    print('\nWhich Trainee?\n')
                    for index, name in enumerate(trainee_list):
                        print(f'{index} {name.firstName} {name.lastName}')
                    try:
                        trainee = int(input('\nEnter the corresponding number\n'))
                        trainee = trainee_list[trainee]
                    except (ValueError, IndexError) as err:
                        logger.exception(f'Invalid trainee selection:\n{err}')
                        print('Please select a valid number\n')
                        time.sleep(1)
                        break
                    training_discipline = int(input('\nWhich discipline?\n1 = Call Taking\n2 = Police\n3 = Fire\n').strip())
                    if match_type == 1:
                        try:
                            disciplines = ['calltaking', 'police', 'fire']
                            training_discipline = disciplines[training_discipline - 1]
                            matches = match_trainee_to_any(trainee, training_discipline)
                            if isinstance(matches, str):
                                print('\n'+matches+'\n')
                                time.sleep(1)
                                choice = 0
                            else:
                                print(f'\nShowing matches for {trainee.firstName} {trainee.lastName}:\n')
                                for index, match in enumerate(matches[0]):
                                    print(f'{index} - {match}')
                                selected_match = input('\nSelect match to mark CTOs as unavailable.\nTo keep CTOs available for other matches, enter q\n')
                                logger.debug(f'Selected match: {selected_match}')
                                try:
                                    selected_match = int(selected_match)
                                    selected_match = matches[0][selected_match]
                                    cto_matches = matches[1]
                                    logger.debug(f'cto_matches list: {cto_matches}')
                                    cto_matches = cto_matches[selected_match]
                                    logger.debug(f'Toggling CTOs to assigned: {cto_matches}')
                                    for match in cto_matches:
                                        match.toggleAssigned(1)
                                        print(f'\n{match.firstName} {match.lastName} marked as assigned\n')
                                    time.sleep(1)
                                    choice = 0
                                except (ValueError, KeyError, IndexError) as err:
                                    if selected_match in ['q','Q']:
                                        print('\nLeaving CTOs as unassigned\nReturning to main menu\n')
                                    else:
                                        logger.exception(err)
                                        print('\nInvalid selection, returning to main menu\n\n')
                                    time.sleep(.75)
                                    choice = 0
                        except (ValueError, IndexError) as err:
                            logger.exception(f'Invalid discipline entered. Input was: {training_discipline}. {err}')
                            print(f'{training_discipline} is not valid. Please enter a number between 1 and 3.\nReturning to main menu\n')
                            time.sleep(.5)
                            choice = 0
                    elif match_type == 2:
                        try:
                            if trainee.shift == 0:
                                print(f'\n{trainee.firstName} {trainee.lastName} has no assigned shift\nSwitching to match CTOs on any shift\n')
                                time.sleep(.5)
                                disciplines = ['calltaking', 'police', 'fire']
                                training_discipline = disciplines[training_discipline - 1]
                                matches = match_trainee_to_any(trainee, training_discipline)
                            else:
                                assigned_shift = ['Day Shift','Graveyard','Power Shift']
                                assigned_shift = assigned_shift[(trainee.shift - 1)]
                                print(f"\n{trainee.firstName} {trainee.lastName}'s currently assigned shift is {assigned_shift}\n")
                                disciplines = ['calltaking', 'police', 'fire']
                                training_discipline = disciplines[training_discipline - 1]
                                matches = match_trainee_to_specific_shift(trainee, training_discipline)
                            if isinstance(matches, str):
                                print('\n'+matches+'\n')
                                time.sleep(1)
                                choice = 0
                            else:
                                print(f'\nShowing matches for {trainee.firstName} {trainee.lastName}:\n')
                                for index, match in enumerate(matches[0]):
                                    print(f'{index} - {match}')
                                selected_match = input('\nSelect match to mark CTOs as unavailable.\nTo keep CTOs available for other matches, enter q\n')
                                logger.debug(f'Selected match: {selected_match}')
                                try:
                                    selected_match = int(selected_match)
                                    selected_match = matches[0][selected_match]
                                    cto_matches = matches[1]
                                    logger.debug(f'cto_matches list: {cto_matches}')
                                    cto_matches = cto_matches[selected_match]
                                    logger.debug(f'Toggling CTOs to assigned: {cto_matches}')
                                    for match in cto_matches:
                                        match.toggleAssigned(1)
                                        print(f'\n{match.firstName} {match.lastName} marked as assigned\n')
                                    time.sleep(1)
                                    match_type = 9
                                except (ValueError, KeyError, IndexError) as err:
                                    if selected_match in ['q','Q']:
                                        print('\nLeaving CTOs as unassigned\nReturning to main menu')
                                        match_type = 9
                                        break
                                    else:
                                        logger.exception(err)
                                        print('\nInvalid selection, returning to main menu\n\n')
                                    time.sleep(.75)
                                    match_type = 9
                        except (ValueError, IndexError):
                            logger.exception(f'Invalid discipline entered. Input was: {training_discipline}')
                            print(f'{training_discipline} is not valid. Please enter a number between 1 and 3.\nReturning to main menu\n')
                            time.sleep(.5)
                            match_type = 9
                    elif match_type == 9:
                        choice = 0
            #Open update employee menu
            if choice ==3:
                update_choice = 0
                while update_choice == 0:
                    print('\nUpdate Employee:\n')
                    update_choice = int(input('1 = Toggle CTO assigned setting\n2 = Update Employee Shift\n3 = Update Employee Schedule\n4 = Update Employee Personality\n5 = Toggle CTO Break Status\n6 = Update Trainee Minimum Skill\n7 = Update Employee Disciplines\n8 = Delete Employee\n9 = Main Menu\n'))
                    #Update CTO assigned setting
                    if update_choice == 1:
                        logger.debug('Toggle CTO assigned value selected')
                        print('Currently assigned CTOs:\n')
                        for index, name in enumerate(cto_list):
                            if name.assigned == 1:
                                print(f'{index}: {name.firstName} {name.lastName}')
                        selection = input('\nSelect CTO to toggle.\nTo view unassigned CTOs, enter q\n')
                        try:
                            newValue = 0
                            selection = int(selection)
                            selection = cto_list[selection]
                            if selection.assigned == 0:
                                    newValue = 1
                            selection.toggleAssigned(newValue)
                            print(f'\nSuccessfully toggled assignment for CTO {selection.firstName} {selection.lastName}\n')
                            time.sleep(1)
                            choice = 0
                        except (ValueError, KeyError):
                            for index, name in enumerate(cto_list):
                                if name.assigned == 0:
                                    print(f'{index}: {name.firstName} {name.lastName}')
                            selection = input('\nSelect CTO to toggle.\nTo return to main menu, enter q\n')
                            try:
                                newValue = 0
                                selection = int(selection)
                                selection = cto_list[selection]
                                if selection.assigned == 0:
                                    newValue = 1
                                selection.toggleAssigned(newValue)
                                print(f'\nSuccessfully toggled assignment for CTO {selection.firstName} {selection.lastName}\n')
                                time.sleep(1)
                                choice = 0
                            except (ValueError, KeyError):
                                choice = 0
                    #Update employee's assigned shift
                    if update_choice == 2:
                        logger.debug('Update employee shift selected')
                        print('\nUpdate Employee Shift:\n')
                        for index, employee in enumerate(loaded_list):
                            print(f'{index}: {employee.firstName} {employee.lastName}')
                        emp_selection = int(input('\nSelect employee to update.\n'))
                        try:
                            emp_selection = loaded_list[emp_selection]
                        except IndexError as err:
                            logger.exception(f'Error occured while selecting employee. Entered value was {emp_selection}')
                            print('\nInvalid selection\n')
                            time.sleep(.5)
                            break
                        try:
                            new_shift = int(input(f'\nEnter new shift for {emp_selection.firstName} {emp_selection.lastName}:\nDays = 1\nGraves = 2\nPower = 3\nIf none, enter 0\n'))
                            if new_shift not in [1,2,3,0]:
                                raise ValueError('Please enter only 0, 1, 2, or 3')
                        except ValueError as err:
                            logger.exception(f'Error occurred while updating employee shift. {err}')
                            print(f'\n{err}\n')
                            time.sleep(.5)
                            break
                        emp_selection.shift = new_shift
                        print('\nShift updated successfully\n')
                        time.sleep(.5)
                        update_choice = 0
                    #Update employee's assigned schedule
                    if update_choice == 3:
                        logger.debug('Update employee schedule selected')
                        print('\nUpdate Employee Schedule:\n')
                        for index, employee in enumerate(loaded_list):
                            print(f'{index}: {employee.firstName} {employee.lastName}')
                        try:
                            emp_selection = int(input('\nSelect employee to update.\n'))
                            emp_selection = loaded_list[emp_selection]
                        except (IndexError, ValueError) as err:
                            logger.exception(f'Error occured while selecting employee. Entered value was {emp_selection}')
                            print('\nInvalid selection\n')
                            time.sleep(.5)
                            break 
                        try:
                            new_schedule = input(f'\nEnter new schedule for {emp_selection.firstName} {emp_selection.lastName}:\nFor CTOs, enter their assigned position (i.e. GY01)\nFor trainees enter their days off (i.e. Mon-Tues)\nIf no assigned schedule, enter 0\n').strip().upper()
                            if new_schedule[:2] == 'DS':
                                new_schedule = new_schedule.replace('DS','GY')
                            emp_selection.schedule = schedules[new_schedule]
                            print(f'\nSuccessfully updated schedule for {emp_selection.firstName} {emp_selection.lastName}\n')
                            time.sleep(1)
                            update_choice = 0
                        except KeyError as err:
                            logger.exception(f'Invalid entry while updating employee shift: {new_schedule}\n{err}')
                            print('Invalid entry')
                            time.sleep(.5)
                            break
                    #Update employee personality setting    
                    if update_choice == 4:
                        print('\nUpdate Employee Personality:\n')
                        #Create list of employees by index
                        for index, employee in enumerate(loaded_list):
                            print(f'{index} - {employee.firstName} {employee.lastName}')
                        try:
                            emp_selection = int(input('\nSelect employee to update:\n'))
                            if emp_selection == 99:
                                for employee in loaded_list:
                                    employee.personality = 'x'
                            else:
                                emp_selection = loaded_list[emp_selection]
                                newValue = input(f'Enter the new personality value for {emp_selection.firstName} {emp_selection.lastName}\n').lower().strip()
                                emp_selection.personality = newValue
                            print('\nPersonality value updated successfully\n')
                            time.sleep(.5)
                        except (IndexError, ValueError) as err:
                            logger.exception(f'Error occcured while updating employee personality setting {err}')
                            print('Invalid entry')
                    #Update CTO break status
                    if update_choice == 5:
                        print('\nToggle CTO Break Status:\n')
                        for index, cto in enumerate(cto_list):
                            print(f'{index} - {cto.firstName} {cto.lastName}')
                        try:
                            newValue = 0
                            cto_selection = int(input('\nSelect the CTO to update:'))
                            cto_selection = cto_list[cto_selection]
                            if cto_selection.onBreak == 0:
                                newValue = 1
                            cto_selection.onBreak = newValue
                            print(f'Successfully updated break status for {cto_selection.firstName} {cto_selection.lastName}')
                            time.sleep(.5)
                        except (IndexError, ValueError) as err:
                            logger.exception(f'Invalid selection while updating CTO break status. Selection was {cto_selection}')
                            print('\nInvalid selection\n')
                            time.sleep(.5)
                            break
                    #Update trainee minimum skill
                    if update_choice == 6:
                        print('\nUpdate trainee minimum skill rating:\n')
                        for index, trainee in enumerate(trainee_list):
                            print(f'{index} - {trainee.firstName} {trainee.lastName}')
                        try:
                            trainee_selection = int(input('Select the trainee to update:\n'))
                            trainee_selection = trainee_list[trainee_selection]
                            print(f'{trainee_selection.firstName} {trainee_selection.lastName} selected\nCurrent minimum skill - {trainee_selection.minSkill}\n')
                            newValue = int(input('Enter new minimum skill value:\n1 = Lower skill/experience\n2 = Normal\n3 = Skilled/Highly Experienced\n'))
                            print('\nMinimum skill updated succeessfully\n')
                            time.sleep(.5)
                        except (IndexError, ValueError) as err:
                            logger.exception(f'Invalid entry while selecting trainee to update. Entered value was {trainee_selection}')
                            print('\nInvalid selection\n')
                            time.sleep(.5)
                            break
                    #Update employee disciplines
                    if update_choice == 7:
                        print('\nUpdate employee disciplines\n')
                        logger.info('Update employee disciplines selected')
                        for index, employee in enumerate(loaded_list):
                            print(f'{index} - {employee.firstName} {employee.lastName}')
                        try:
                            employee_selection = int(input('\nSelect the employee to update:\n'))
                            employee_selection = loaded_list[employee_selection]
                            logger.debug(f'Selected employee is {employee_selection.firstName} {employee_selection.lastName}')
                            print(f'Discipline Settings for {employee_selection.firstName} {employee_selection.lastName}:\n1 - Call Taking - {employee_selection.calltaking}\n2 -   Police    - {employee_selection.police}\n3 -    Fire     - {employee_selection.fire}\n\n0 = Not signed off, 1 = Signed off\n')
                            selection = int(input('Select discipline to update.\n'))
                            logger.debug(f'Selected discipline: {selection}')
                            if selection == 1:
                                if employee_selection.calltaking == 0:
                                    employee_selection.calltaking = 1
                                else:
                                    employee_selection.calltaking = 0
                            if selection == 2:
                                if employee_selection.police == 0:
                                    employee_selection.police = 1
                                else:
                                    employee_selection.police = 0
                            if selection == 3:
                                if employee_selection.fire == 0:
                                    employee_selection.fire = 1
                                else:
                                    employee_selection.fire = 0
                            print('\nDiscipline successfully updated\n')
                            time.sleep(.5)
                            break
                        except (ValueError, IndexError) as err:
                            logger.exception(err)
                            print('An error occured while attempting to update employee discipline. Please try again.\n')
                    #Delete employeee
                    if update_choice == 8:
                        logger.debug('Delete employee selected')
                        print('Choose which employee to delete:\n')
                        for index, name in enumerate(loaded_list):
                            print(f'{index} - {name.firstName} {name.lastName}')
                        try:
                            selection = int(input('Enter the corresponding number\n'))
                            employee = loaded_list[selection]
                            print(f'\nDeleting {employee.firstName} {employee.lastName}\n')
                            employee_name = employee.lastName + employee.firstName
                            try:
                                logger.debug(f'Deleting {employee_name}')
                                time.sleep(.25)
                                os.remove(employee_name)
                            except Exception as err:
                                logger.exception(f'Error occured while attempting to delete pickle file:\n{err}')
                                print('Unable to delete pickle file')
                            employee_list.pop(selection)
                        except (IndexError, ValueError) as err:
                            logger.exception(f'Invalid selection while deleting employee.')
                            print('Invalid selection')
                            time.sleep(.5)
                            break
                        loaded_list.remove(employee)
                        if isinstance(employee, CTO):
                            cto_list.remove(employee)   
                        if isinstance(employee, Trainee):
                            trainee_list.remove(employee)
                        del employee
                        print('Success\n')
                        time.sleep(1)
                        choice = 0
                    if update_choice == 9:
                        choice = 0
            #Create report of all employee in the app
            if choice == 8:
                report = pd.DataFrame()
                temp_cto_list = []
                temp_trainee_list = []
                c = 0
                t = 0
                for cto in cto_list:
                    temp_cto_list.append(vars(cto))
                    for key, value in schedules.items():
                        if value == temp_cto_list[c]['_schedule']:
                            temp_cto_list[c]['_schedule'] = key
                            if temp_cto_list[c]['_shift'] == 1:
                                temp_cto_list[c]['_schedule'] = temp_cto_list[c]['_schedule'].replace('GY','DS')
                            if temp_cto_list[c]['_shift'] == 3:
                                temp_cto_list[c]['_schedule'] = temp_cto_list[c]['_schedule'].replace('GY','PS')
                    c += 1
                cdf = pd.DataFrame(temp_cto_list)
                for trainee in trainee_list:
                    temp_trainee_list.append(vars(trainee))
                    for key, value in schedules.items():
                        if value == temp_trainee_list[t]['_schedule']:
                            temp_trainee_list[t]['_schedule'] = key
                            if temp_trainee_list[t]['_shift'] == 1:
                                temp_trainee_list[t]['_schedule'] = temp_cto_list[t]['_schedule'].replace('GY','DS')
                            if temp_trainee_list[t]['_shift'] == 1:
                                temp_trainee_list[t]['_schedule'] = temp_cto_list[t]['_schedule'].replace('GY','PS')
                    t += 1
                tdf = pd.DataFrame(temp_trainee_list)
                report = pd.concat([report,cdf,tdf], ignore_index=True)
                print(report)
                option = int(input('Would you like to export to Excel?\nEnter 1 for yes\n'))
                if option == 1:
                    try:
                        report.to_excel(f'{date.today()} employee_report.xlsx')
                        print('\nReport created\n')
                    except Exception as err:
                        print(f'Unknown error occured: {err}')
                while choice != 0:
                    choice = int(input('\nEnter 0 to return to main menu\n'))
                choice = 0