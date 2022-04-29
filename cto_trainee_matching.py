import time
import pickle
import os
import pandas as pd
import logging

logging.basicConfig(filename='cto_trainee_matching_log.log', level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(message)s',force=True)
logger=logging.getLogger(__name__)

schedules = {}
schedules[12] = {}
schedules[8] = {}
schedules[12]['GY01'] = [0,1,1,1,1,0,0,0,1,1,1,0,0,0]
schedules[12]['GY02'] = [0,1,1,1,1,0,0,0,0,1,1,1,0,0]
schedules[12]['GY03'] = [0,0,1,1,1,1,0,0,0,1,1,1,0,0]
schedules[12]['GY04'] = [0,0,1,1,1,1,0,0,0,0,1,1,1,0]
schedules[12]['GY05'] = [0,0,0,1,1,1,1,0,0,0,1,1,1,0]
schedules[12]['GY06'] = [0,0,0,1,1,1,1,0,0,0,0,1,1,1]
schedules[12]['GY07'] = [0,0,0,0,1,1,1,1,0,0,0,1,1,1]
schedules[12]['GY08'] = [1,0,0,0,0,1,1,1,0,0,0,1,1,1]
schedules[12]['GY09'] = [1,0,0,0,0,1,1,1,1,0,0,0,1,1]
schedules[12]['GY10'] = [1,1,0,0,0,0,1,1,1,0,0,0,1,1]
schedules[12]['GY11'] = [1,1,0,0,0,0,1,1,1,1,0,0,0,1]
schedules[12]['GY12'] = [1,1,1,0,0,0,0,1,1,1,0,0,0,1]
schedules[12]['GY13'] = [1,1,1,0,0,0,0,1,1,1,1,0,0,0]
schedules[12]['GY14'] = [1,1,1,1,0,0,0,0,1,1,1,0,0,0]
schedules[12]['PS01'] = [0,1,1,1,1,0,0,0,1,1,1,0,0,0]
schedules[12]['PS02'] = [0,0,1,1,1,1,0,0,0,1,1,1,0,0]
schedules[12]['PS03'] = [0,0,0,1,1,1,1,0,0,0,1,1,1,0]
schedules[12]['PS04'] = [0,0,0,0,1,1,1,1,0,0,0,1,1,1]
schedules[12]['PS05'] = [1,0,0,0,0,1,1,1,0,0,0,1,1,1]
schedules[12]['PS06'] = [1,1,0,0,0,0,1,1,1,0,0,0,1,1]
schedules[12]['PS07'] = [1,1,1,0,0,0,0,1,1,1,0,0,0,1]
schedules[12]['PS08'] = [1,1,1,1,0,0,0,0,1,1,1,0,0,0]
schedules[8]['SUN-MON'] = [0,0,1,1,1,1,1,0,0,1,1,1,1,1]
schedules[8]['MON-TUES'] = [1,0,0,1,1,1,1,1,0,0,1,1,1,1]
schedules[8]['TUES-WED'] = [1,1,0,0,1,1,1,1,1,0,0,1,1,1]
schedules[8]['WED-THURS'] = [1,1,1,0,0,1,1,1,1,1,0,0,1,1]
schedules[8]['THURS-FRI'] = [1,1,1,1,0,0,1,1,1,1,1,0,0,1]
schedules[8]['FRI-SAT'] = [1,1,1,1,1,0,0,1,1,1,1,1,0,0]
schedules[8]['SAT-SUN'] = [0,1,1,1,1,1,0,0,1,1,1,1,1,0]

cto_list = []
trainee_list = []

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
    def updateShift(self, newShift):
        self.shift = newShift
    def updateSchedule(self, newSchedule):
        self.schedule = schedules[newSchedule]
    def updateDisciplines(self, policeUpdate, fireUpdate):
        if self.police != policeUpdate:
            self.police == policeUpdate
        if self.fire != fireUpdate:
            self.fire = fireUpdate
    def __str__(self):
        return f"Last Name: {self.lastName}, First Name: {self.firstName}\nShift: {self.shift}\nSchedule: {self.schedule}"

class CTO(Employee):
    def __init__(self, firstName, lastName, shift, schedule, callTaking, police, fire, personality, partTime, skill, onBreak, assigned = 0):
        super().__init__(firstName, lastName, shift, schedule, callTaking, police, fire, personality)
        self.partTime = partTime
        self.skill = skill
        self.onBreak = onBreak
        self.assigned = assigned
        cto_list.append(self)
    def toggleBreak(self):
        if self.onBreak == 1:
            self.onBreak = 0
        else:
            self.onBreak = 1
    def updateSkill(self, newSkill):
        self.skill = newSkill
    def toggleAssigned(self):
        logger.debug(f'Start value assigned: {self.assigned}')
        if self.assigned == 0:
            self.assigned == 1
        else:
            self.assigned == 0
        logger.debug(f'End value assigned {self.assigned}')
        logger.debug(f'Updating pickle file for {self.firstName} {self.lastName}')
        employee_name = self.lastName + self.firstName
        file = open(employee_name, 'wb')
        pickle.dump(self, file)
        file.close()

class Trainee(Employee):
    def __init__(self, firstName, lastName, shift, schedule, callTaking, police, fire, personality, minSkill):
        super().__init__(firstName, lastName, shift, schedule, callTaking, police, fire, personality)
        self.minSkill = minSkill
        trainee_list.append(self)
    def updateMinSkill(self, newMinSkill):
        self.minSkill = newMinSkill

def create_employee():
    logger.debug('Starting create_employee')
    selection = 0
    try:
        selection = int(input('If the employee is a CTO, enter 1\nIf the employee is a trainee, enter 2\n'))
        if selection not in [1,2]:
            raise ValueError
    except ValueError:
        logging.exception(f'Invalid selection. Entered value was {selection}.')
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
    schedule = input('Enter their assigned schedule.\nFor CTOs, enter their assigned position (i.e. GY01)\nFor trainees enter their days off (i.e. Mon-Tues)\nIf no assigned schedule, enter 0\n').upper()
    if schedule[:2] == 'DS':
        schedule = schedule.replace('DS','GY')
    calltaking = int(input('Are they signed off on call taking?\nEnter 1 for Yes and 0 for No.\n'))
    if calltaking == 1:
        police = int(input('Are they signed off on police?\nEnter 1 for Yes and 0 for No.\n'))
        fire = int(input('Are they signed off on fire?\nEnter 1 for Yes and 0 for No.\n'))
    else:
        police = 0
        fire = 0
    personality = input('Enter their personality type.\n').lower()
    if selection == 1:
        partTime = int(input('Are they a fill in CTO or part time employee?\nEnter 1 for Yes and 0 for No.\n'))
        skill = int(input('Enter their CTO skill level.\n1 = Lower skill/experience\n2 = Normal\n3 = Skilled/Highly Experienced\n'))
        assigned = int(input('Are they currently assigned a trainee?\nEnter 1 for Yes and 0 for No.\n'))
        onBreak = 0
        cto_name = last_name + first_name[0]
        try:
            schedule = schedules[12][schedule]
        except KeyError as err:
            logger.exception(err)
            schedule = 0
        cto_name = CTO(first_name,last_name,shift,schedule,calltaking,police,fire,personality,partTime,skill,onBreak, assigned)
        return cto_name
    if selection == 2:
        minSkill = int(input('Enter the required minimum skill level for their assigned CTOs.\n1 = Lower skill/experience\n2 = Normal\n3 = Skilled/Highly Experienced\n'))
        trainee_name = last_name + first_name[0]
        try:
            schedule = schedules[8][schedule]
        except KeyError as err:
            logger.exception(err)
            schedule = 0
        trainee_name = Trainee(first_name,last_name,shift,schedule,calltaking,police,fire,personality,minSkill)
        return trainee_name

def match_trainee_to_any(trainee, discipline):
    logger.debug(f'Starting match_trainee_to_any with inputs {trainee} and {discipline}')
    options = []
    ideal_list = []
    last_choice = []
    matches = []
    cto_matches = {}
    for cto in cto_list:
        logger.debug(f'Considering CTO {cto.firstName} {cto.lastName}')
        logger.debug(f'{getattr(cto,discipline)}')
        if cto.assigned == 0 and getattr(cto,discipline) == 1:
            logger.debug(f'Matches discipline: {cto.firstName} {cto.lastName}')
            if cto.skill >= trainee.minSkill and cto.personality == trainee.personality:
                logger.debug(f'Adding {cto.firstName} {cto.lastName} to ideal list')
                ideal_list.append(cto)
            elif cto.skill >= trainee.minSkill:
                logger.debug(f'Adding {cto.firstName} {cto.lastName} to options list')
                options.append(cto)
            else:
                last_choice.append(cto)
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
        cto_shift = cto.shift
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
    choice = int(input('What would you like to do?\n1 = Create new employee\n2 = Match Trainee to CTO on any shift\n3 = Remove employee\n4 = Toggle CTO assignment\n8 = Print existing employees\n9 = Exit\n'))
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
            if choice == 2:
                print('Which Trainee?\n')
                for index, name in enumerate(trainee_list):
                    print(f'{index} {name.firstName} {name.lastName}')
                trainee = int(input('\nEnter the corresponding number\n'))
                try:
                    trainee = trainee_list[trainee]
                except ValueError as err:
                    logger.exception(f'Invalid trainee selection:\n{err}')
                    print('Please select a valid number')
                    choice = 0
                training_discipline = input('Which discipline?\n').lower().strip()
                try:
                    if training_discipline == 'call taking':
                        training_discipline = 'calltaking'
                    if training_discipline not in ['calltaking', 'police','fire']:
                        raise ValueError
                except ValueError:
                    logger.exception(f'Invalid discipline entered. Input was: {training_discipline}')
                matches = match_trainee_to_any(trainee, training_discipline)
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
                        match.toggleAssigned()
                        print(f'{cto.first_name} {cto.last_name} marked as assigned')
                    choice = 0
                except (ValueError, KeyError):
                    choice = 0
            if choice ==3:
                print('Choose which employee to delete:\n')
                for index, name in enumerate(loaded_list):
                    print(f'{index} {name.firstName} {name.lastName}')
                selection = int(input('Enter the corresponding number\n'))
                employee = loaded_list[selection]
                employee_name = employee.lastName + employee.firstName
                try:
                    os.remove(employee_name)
                except Exception as err:
                    logger.exception(f'Error occured while attempting to delete pickle file:\n{err}')
                    print('Unable to delete pickle file')
                employee_list.pop(selection)
                if isinstance(employee, CTO):
                    cto_list.remove(employee)
                if isinstance(employee, Trainee):
                    trainee_list.remove(employee)
                del employee
                choice = 0
            if choice == 4:
                print('Currently assigned CTOs:\n')
                for index, name in enumerate(cto_list):
                    if name.assigned == 1:
                        print(f'{index}: {name.firstName} {name.lastName}')
                selection = input('\nSelect CTO to toggle.\nTo view unassigned CTOs, enter q\n')
                try:
                    selection = int(selection)
                    selection = cto_list[selection]
                    selection.toggleAssigned()
                    choice = 0
                except (ValueError, KeyError):
                    for index, name in enumerate(cto_list):
                        if name.assigned == 0:
                            print(f'{index}: {name.firstName} {name.lastName}')
                    selection = input('\nSelect CTO to toggle.\nTo return to main menu, enter q\n')
                    try:
                        selection = int(selection)
                        selection = cto_list[selection]
                        selection.toggleAssigned()
                        choice = 0
                    except (ValueError, KeyError):
                        choice = 0
            if choice == 8:
                report = pd.DataFrame(columns=['First Name', 'Last Name', 'Shift', 'Schedule', 'Call Taking', 'Police', 'Fire', 'Personality', 'Skill', 'On Break','Assigned'])
                for cto in cto_list:
                    print(cto)
                for trainee in trainee_list:
                    print(trainee)
                choice = 0